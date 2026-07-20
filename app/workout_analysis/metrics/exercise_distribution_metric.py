from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class ExerciseDistributionMetric(BaseMetric):
    """
    Computes the distribution of exercises performed.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Count how many workout sessions include
        # each exercise.
        distribution: dict[str, int] = defaultdict(int)

        for entry in history:
            distribution[entry.exercise] += 1

        # Sort exercises by frequency in descending order.
        sorted_distribution = dict(
            sorted(
                distribution.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        result.metrics["exercise_distribution"] = {
            "total_exercises": len(sorted_distribution),
            "distribution": sorted_distribution,
        }