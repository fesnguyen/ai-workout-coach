import re

from evaluation.judges.base_judge import BaseJudge

from evaluation.judges.utilities import Utilities
from evaluation.models import (
    EvaluationContext,
    JudgeResult,
    SearchCase,
)


class FactCoverageJudge(BaseJudge):
    """
    Measures how many expected facts appear in the generated answer.
    """

    async def evaluate(
        self,
        case: SearchCase,
        context: EvaluationContext,
    ) -> JudgeResult:
        answer = Utilities.normalize_text(context.response.answer)

        matched: list[str] = []
        missing: list[str] = []

        for fact in case.expected.facts:
            normalized_fact = Utilities.normalize_text(fact)

            if normalized_fact in answer:
                matched.append(fact)
            else:
                missing.append(fact)

        total = len(case.expected.facts)

        coverage = len(matched) / total if total else 1.0
        score = coverage * 5.0

        return JudgeResult(
            passed=coverage >= 0.8,
            score=score,
            reason=(
                f"Matched {len(matched)}/{total} facts. "
                f"Matched: {', '.join(matched) if matched else 'None'}. "
                f"Missing: {', '.join(missing) if missing else 'None'}."
            ),
        )