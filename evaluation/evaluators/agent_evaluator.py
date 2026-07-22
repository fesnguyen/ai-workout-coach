import json
from pathlib import Path

from app.application_container import ApplicationContainer
from app.api.api_schemas import ChatRequest

from evaluation.judges.agent.agent_registry import build_agent_judges
from evaluation.models import (
    AgentCase,
    EvaluationContext,
    EvaluationResult,
    ExpectedAnswer,
)


def load_agent_cases(
    filename: str,
) -> list[AgentCase]:
    """
    Load agent evaluation cases.
    """

    dataset = Path(__file__).parent.parent / "datasets" / filename

    with dataset.open("r", encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [
        AgentCase(
            id=case["id"],
            request=ChatRequest(**case["request"]),
            expected=ExpectedAnswer(**case["expected"]),
        )
        for case in raw_cases
    ]


async def evaluate_agent(
    container: ApplicationContainer,
    judges: list,
) -> list[EvaluationResult]:
    """
    Evaluate the chat agent end-to-end.
    """

    agent = container.agent

    results: list[EvaluationResult] = []

    for case in load_agent_cases("agent_cases.json"):
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
                    category="Agent",
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