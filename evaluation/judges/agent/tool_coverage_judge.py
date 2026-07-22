from evaluation.judges.base_judge import BaseJudge
from evaluation.models import (
    AgentCase,
    EvaluationContext,
    JudgeResult,
)


class ToolCoverageJudge(BaseJudge):
    """
    Checks whether the expected tools were invoked by the agent.
    """

    async def evaluate(
        self,
        case: AgentCase,
        context: EvaluationContext,
    ) -> JudgeResult:

        expected = {
            tool.lower()
            for tool in case.expected.tool_calls
        }

        actual = {
            tool.lower()
            for tool in (context.tool_calls or [])
        }

        matched = sorted(expected & actual)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)

        coverage = (
            len(matched) / len(expected)
            if expected
            else 1.0
        )

        score = round(coverage * 5, 1)

        return JudgeResult(
            passed=coverage >= 1.0,
            score=score,
            reason=(
                f"Matched: {matched}; "
                f"Missing: {missing}; "
                f"Unexpected: {unexpected}"
            ),
        )