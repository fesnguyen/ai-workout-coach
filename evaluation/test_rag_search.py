import asyncio
import json
from pathlib import Path

from app.application_container import ApplicationContainer

from evaluation.judges.faithfulness_judge import FaithfulnessJudge
from evaluation.models import EvaluationResult, SearchCase
from evaluation.report_builder import ReportBuilder


def load_cases() -> list[SearchCase]:
    dataset = (
        Path(__file__).parent
        / "data"
        / "rag_search_cases.json"
    )

    with dataset.open("r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [
        SearchCase(**case)
        for case in raw_cases
    ]


async def main() -> None:
    container = ApplicationContainer()

    await container.initialize()

    try:
        rag = container.rag_service
        generator = container.generator

        judges = [
            FaithfulnessJudge(generator),
            # SourceJudge(),
            # StructureJudge(),
        ]

        results: list[EvaluationResult] = []

        for case in load_cases():
            print(f"Evaluating {case.id}...")

            response = await rag.search(case.query)

            for judge in judges:
                judge_result = await judge.evaluate(
                    case=case,
                    answer=response,
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

        ReportBuilder().build(
            results=results,
            output=Path("EVALUATION.md"),
        )

        print()
        print("===================================")
        print("Evaluation completed.")
        print(f"Total Results : {len(results)}")

        passed = sum(result.passed for result in results)

        print(f"Passed        : {passed}")
        print(f"Failed        : {len(results) - passed}")
        print("Report        : EVALUATION.md")
        print("===================================")

    finally:
        await container.shutdown()


if __name__ == "__main__":
    asyncio.run(main())