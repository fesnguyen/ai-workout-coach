from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class IntensityMetric(BaseMetric):
    """
    Computes intensity statistics for each exercise.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Collect all performed sets for each exercise.
        exercise_sets: dict[str, list] = defaultdict(list)

        for entry in history:
            exercise_sets[entry.exercise].extend(
                entry.sets
            )

        intensity = {}

        # Compute intensity statistics for each exercise.
        for exercise, sets in exercise_sets.items():
            weights = [
                exercise_set.weight
                for exercise_set in sets
            ]

            reps = [
                exercise_set.reps
                for exercise_set in sets
            ]

            intensity[exercise] = {
                "average_weight": round(
                    sum(weights) / len(weights),
                    2,
                ),
                "maximum_weight": max(weights),
                "average_reps": round(
                    sum(reps) / len(reps),
                    2,
                ),
            }

        result.metrics["intensity"] = intensity