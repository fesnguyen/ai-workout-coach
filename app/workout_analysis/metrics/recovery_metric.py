from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class RecoveryMetric(BaseMetric):
    """
    Computes recovery time between workouts for each exercise.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Group workout dates by exercise.
        exercise_dates: dict[str, list] = defaultdict(list)

        for entry in history:
            exercise_dates[entry.exercise].append(entry.date)

        recovery: dict[str, dict] = {}

        # Compute recovery statistics for each exercise.
        for exercise, dates in exercise_dates.items():
            dates.sort()

            if len(dates) < 2:
                recovery[exercise] = {
                    "average_rest_days": None,
                    "minimum_rest_days": None,
                    "maximum_rest_days": None,
                }
                continue

            rest_days = [
                (current - previous).days
                for previous, current in zip(
                    dates,
                    dates[1:],
                )
            ]

            recovery[exercise] = {
                "average_rest_days": round(
                    sum(rest_days) / len(rest_days),
                    2,
                ),
                "minimum_rest_days": min(rest_days),
                "maximum_rest_days": max(rest_days),
            }

        result.metrics["recovery"] = recovery