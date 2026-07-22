from evaluation.judges.base_judge import BaseJudge
from evaluation.models import (
    AgentCase,
    EvaluationContext,
    JudgeResult,
)

from evaluation.judges.utilities import Utilities



class FactCoverageJudge(BaseJudge):
    """
    Checks whether the generated response covers the expected facts.
    """

    async def evaluate(
        self,
        case: AgentCase,
        context: EvaluationContext,
    ) -> JudgeResult:
        response = Utilities.normalize_text(
            context.generated_response or ""
        )

        facts = [
            Utilities.normalize_text(fact)
            for fact in case.expected.facts
        ]

        matched = [
            fact
            for fact in facts
            if fact in response
        ]

        missing = [
            fact
            for fact in facts
            if fact not in response
        ]

        coverage = (
            len(matched) / len(facts)
            if facts
            else 1.0
        )

        score = round(coverage * 5, 1)

        return JudgeResult(
            passed=coverage >= 0.8,
            score=score,
            reason=(
                f"Matched: {matched}; "
                f"Missing: {missing}"
            ),
        )