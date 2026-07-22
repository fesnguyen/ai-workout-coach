import asyncio
import json
from pathlib import Path

from app.api.api_schemas import UserProfile, WorkoutAnalyzeRequest
from app.application_container import ApplicationContainer
from evaluation.judges.rag_search.rag_search_registry import build_rag_judges
from evaluation.judges.workout_analysis.workout_analysis_registry import build_workout_judges

from evaluation.models import EvaluationContext, EvaluationResult, ExpectedAnswer, ExpectedWorkoutAnalysis, SearchCase, WorkoutAnalysisCase
from evaluation.report_builder import ReportBuilder


def load_rag_search_cases(filename: str) -> list[SearchCase]:
    dataset = Path(__file__).parent / "datasets" / filename

    with dataset.open("r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [
        SearchCase(
            id=case["id"],
            query=case["query"],
            expected=ExpectedAnswer(**case["expected"]),
        )
        for case in raw_cases
    ]

def load_workout_analysis_cases(
    filename: str,
) -> list[WorkoutAnalysisCase]:

    dataset_dir = Path(__file__).parent / "datasets"

    with (dataset_dir / filename).open(
        "r",
        encoding="utf-8",
    ) as f:
        raw_cases = json.load(f)

    cases: list[WorkoutAnalysisCase] = []

    for case in raw_cases:

        workout_file = (
            dataset_dir
            / case["request"]["user_profile"]["workouts"]
        )

        with workout_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            workout_data = json.load(f)

        request = WorkoutAnalyzeRequest(
            query=case["request"]["query"],
            user_profile=UserProfile(**workout_data),
        )

        cases.append(
            WorkoutAnalysisCase(
                id=case["id"],
                request=request,
                expected=ExpectedWorkoutAnalysis(
                    **case["expected"]
                ),
            )
        )

    return cases

JUDGE_REGISTRY = {
    "rag": build_rag_judges,
    "workout": build_workout_judges,
}

async def evaluate_rag_search(
    container: ApplicationContainer,
) -> list[EvaluationResult]:
    rag = container.rag_service

    results: list[EvaluationResult] = []

    judges = JUDGE_REGISTRY["rag"](container)

    for case in load_rag_search_cases("rag_search_cases.json"):
        print(f"Evaluating {case.id}...")

        response = await rag.search(case.query)

        context = EvaluationContext(
            response=response,
        )

        for judge in judges:
            judge_result = await judge.evaluate(
                case=case,
                context=context,
            )

            results.append(
                EvaluationResult(
                    category="RAG Search",
                    case_id=case.id,
                    question=case.query,
                    judge=judge.__class__.__name__,
                    passed=judge_result.passed,
                    score=judge_result.score,
                    reason=judge_result.reason,
                    answer=response.answer,
                )
            )

            status = "PASS" if judge_result.passed else "FAIL"

            print(
                f"  [{status}] "
                f"{judge.__class__.__name__} "
                f"({judge_result.score:.1f}/5)"
            )

    return results


async def evaluate_workout_analysis(
    container: ApplicationContainer,
) -> list[EvaluationResult]:

    workout_service = container.workout_analysis_service

    results: list[EvaluationResult] = []

    judges = JUDGE_REGISTRY["workout"](container)

    for case in load_workout_analysis_cases(
        "workout_analysis_cases.json",
    ):
        print(f"Evaluating {case.id}...")

        response = await workout_service.analyze(
            case.request,
        )

        context = EvaluationContext(
            analysis=response.analysis,
            generated_response=response.response,
        )

        for judge in judges:
            judge_result = await judge.evaluate(
                case=case,
                context=context,
            )

            results.append(
                EvaluationResult(
                    category="Workout Analysis",
                    case_id=case.id,
                    question=case.request.query,
                    judge=judge.__class__.__name__,
                    passed=judge_result.passed,
                    score=judge_result.score,
                    reason=judge_result.reason,
                    answer=response.response,
                )
            )

            status = (
                "PASS"
                if judge_result.passed
                else "FAIL"
            )

            print(
                f"  [{status}] "
                f"{judge.__class__.__name__} "
                f"({judge_result.score:.1f}/5)"
            )

    return results


async def main() -> None:
    container = ApplicationContainer()

    await container.initialize()

    try:
        results: list[EvaluationResult] = []

        #
        # Evaluate the RAG search pipeline.
        #
        results.extend(
            await evaluate_rag_search(container)
        )

        #
        # Workout analysis evaluation.
        #
        results.extend(
            await evaluate_workout_analysis(container)
        )
        #
        # results.extend(
        #     await evaluate_agent(container)
        # )
        #
        # results.extend(
        #     await evaluate_adversarial(container)
        # )

        ReportBuilder().build(
            results=results,
            output=Path("EVALUATION.md"),
        )

        passed = sum(
            result.passed
            for result in results
        )

        failed = len(results) - passed

        print()
        print("========================================")
        print("Evaluation completed")
        print("========================================")
        print(f"Total  : {len(results)}")
        print(f"Passed : {passed}")
        print(f"Failed : {failed}")
        print("Report : EVALUATION.md")
        print("========================================")

    finally:
        await container.shutdown()


if __name__ == "__main__":
    asyncio.run(main())