from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class ProgressionMetric(BaseMetric):
    """
    Computes strength progression for each exercise.

    Progression is determined by comparing the heaviest
    weight performed in the earliest session against the
    heaviest weight performed in the latest session.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Group workout entries by exercise name.
        exercises: dict[str, list] = defaultdict(list)

        for entry in history:
            exercises[entry.exercise].append(entry)

        progression: dict[str, dict] = {}

        # Analyze progression independently for each exercise.
        for exercise, entries in exercises.items():

            # Sort chronologically so we can compare
            # the first and latest training sessions.
            entries.sort(key=lambda entry: entry.date)

            first_entry = entries[0]
            latest_entry = entries[-1]

            # Find the heaviest set performed in the
            # earliest recorded session.
            first_weight = max(
                exercise_set.weight
                for exercise_set in first_entry.sets
            )

            # Find the heaviest set performed in the
            # most recent recorded session.
            latest_weight = max(
                exercise_set.weight
                for exercise_set in latest_entry.sets
            )

            change = latest_weight - first_weight

            # Classify the direction of progress.
            if change > 0:
                trend = "improving"
            elif change < 0:
                trend = "declining"
            else:
                trend = "stable"

            progression[exercise] = {
                "first_weight": first_weight,
                "latest_weight": latest_weight,
                "change": round(change, 2),
                "trend": trend,
            }

        result.metrics["progression"] = progression