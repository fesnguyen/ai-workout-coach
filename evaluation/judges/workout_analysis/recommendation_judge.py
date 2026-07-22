from evaluation.judges.base_judge import BaseJudge
from evaluation.models import (
    EvaluationContext,
    JudgeResult,
    WorkoutAnalysisCase,
)
from evaluation.judges.utilities import Utilities


class RecommendationJudge(BaseJudge):
    """
    Checks whether the generated response contains the expected recommendations.
    """

    async def evaluate(
        self,
        case: WorkoutAnalysisCase,
        context: EvaluationContext,
    ) -> JudgeResult:
        response = Utilities.normalize_text(context.generated_response or "")
        
        # Normalize expected recommendation groups (supports string or list of strings)
        expected_groups: list[list[str]] = []
        for item in case.expected.recommendations:
            if isinstance(item, list):
                expected_groups.append([Utilities.normalize_text(kw) for kw in item])
            else:
                expected_groups.append([Utilities.normalize_text(item)])

        matched_groups: list[list[str]] = []
        missing_groups: list[list[str]] = []

        for group in expected_groups:
            # Pass if ANY synonym/keyword in the target group matches the response
            if any(keyword in response for keyword in group):
                matched_groups.append(group)
            else:
                missing_groups.append(group)

        coverage = (
            len(matched_groups) / len(expected_groups)
            if expected_groups
            else 1.0
        )

        score = round(coverage * 5, 1)

        return JudgeResult(
            passed=coverage >= 0.8,
            score=score,
            reason=(
                f"Matched groups: {matched_groups}; "
                f"Missing groups: {missing_groups}"
            ),
        )