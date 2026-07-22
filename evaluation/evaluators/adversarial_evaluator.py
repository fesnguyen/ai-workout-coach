import json
from pathlib import Path

from app.application_container import ApplicationContainer
from app.api.api_schemas import ChatRequest

from evaluation.models import (
    AdversarialCase,
    EvaluationContext,
    EvaluationResult,
    ExpectedAdversarial,
)


def load_adversarial_cases(
    filename: str,
) -> list[AdversarialCase]:
    """
    Load adversarial evaluation cases.
    """

    dataset = Path(__file__).parent.parent / "datasets" / filename

    with dataset.open("r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [
        AdversarialCase(
            id=case["id"],
            request=ChatRequest(**case["request"]),
            expected=ExpectedAdversarial(**case["expected"]),
        )
        for case in raw_cases
    ]


async def evaluate_adversarial(
    container: ApplicationContainer,
    judges: list,
) -> list[EvaluationResult]:
    """
    Evaluate adversarial guardrail cases.
    """

    agent = container.agent

    results: list[EvaluationResult] = []

    for case in load_adversarial_cases(
        "adversarial_cases.json"
    ):
        print(f"Evaluating {case.id}...")

        response = await agent.chat(
            case.request,
        )

        context = EvaluationContext(
            generated_response=response.answer,
        )

        for judge in judges:
            judge_result = await judge.evaluate(
                case=case,
                context=context,
            )

            results.append(
                EvaluationResult(
                    category="Adversarial",
                    case_id=case.id,
                    question=case.request.message,
                    judge=judge.__class__.__name__,
                    passed=judge_result.passed,
                    score=judge_result.score,
                    reason=judge_result.reason,
                    answer=response.answer,
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