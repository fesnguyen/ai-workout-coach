from pathlib import Path

import json

from app.application_container import ApplicationContainer
from evaluation.judges.rag_search.rag_search_registry import build_rag_judges
from evaluation.models import ExpectedAnswer, SearchCase, EvaluationResult, EvaluationContext


def load_rag_search_cases(filename: str) -> list[SearchCase]:
    dataset = Path(__file__).parent.parent / "datasets" / filename

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


async def evaluate_rag_search(
    container: ApplicationContainer,
    judges: list,
) -> list[EvaluationResult]:
    rag = container.rag_service

    results: list[EvaluationResult] = []

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