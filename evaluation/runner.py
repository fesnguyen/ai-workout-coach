import asyncio
import json
from pathlib import Path

from app.api.api_schemas import UserProfile, WorkoutAnalyzeRequest
from app.application_container import ApplicationContainer
from evaluation.judges.rag_search.rag_search_registry import build_rag_judges
from evaluation.judges.workout_analysis.workout_analysis_registry import build_workout_judges

from evaluation.models import EvaluationContext, EvaluationResult, ExpectedAnswer, ExpectedWorkoutAnalysis, SearchCase, WorkoutAnalysisCase
from evaluation.report_builder import ReportBuilder
from evaluation.evaluators.rag_search_evaluator import evaluate_rag_search
from evaluation.evaluators.workout_analysis_evaluator import evaluate_workout_analysis, load_workout_analysis_cases

JUDGE_REGISTRY = {
    "rag": build_rag_judges,
    "workout": build_workout_judges,
}


async def main() -> None:
    container = ApplicationContainer()

    await container.initialize()

    try:
        results: list[EvaluationResult] = []

        # results.extend(
        #     await evaluate_rag_search(
        #         container=container,
        #         judges=JUDGE_REGISTRY["rag"](container)
        #     )
        # )

        #
        # Workout analysis evaluation.
        #
        results.extend(
            await evaluate_workout_analysis(
                container=container,
                judges=JUDGE_REGISTRY["workout"](container)
            )
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