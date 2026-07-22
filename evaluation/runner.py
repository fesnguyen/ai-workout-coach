import asyncio
import json
from pathlib import Path

from app.application_container import ApplicationContainer

from evaluation.judges.faithfulness_judge import FaithfulnessJudge
from evaluation.models import EvaluationResult, SearchCase
from evaluation.report_builder import ReportBuilder


def load_cases(filename: str) -> list[SearchCase]:
    dataset = Path(__file__).parent / "data" / filename

    with dataset.open("r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [
        SearchCase(**case)
        for case in raw_cases
    ]


async def evaluate_rag_search(
    container: ApplicationContainer,
) -> list[EvaluationResult]:
    rag = container.rag_service

    generator = container.generator

    judges = [
        FaithfulnessJudge(generator),
        # SourceJudge(),
        # StructureJudge(),
    ]

    results: list[EvaluationResult] = []

    for case in load_cases("rag_search_cases.json"):
        print(f"Evaluating {case.id}...")

        response = await rag.search(case.query)

        for judge in judges:
            judge_result = await judge.evaluate(
                case=case,
                answer=response.answer,
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
        # Future evaluations.
        #
        # results.extend(
        #     await evaluate_workout_analysis(container)
        # )
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