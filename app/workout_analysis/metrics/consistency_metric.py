from __future__ import annotations

from datetime import timedelta

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class ConsistencyMetric(BaseMetric):
    """
    Computes training consistency statistics.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Handle an empty workout history.
        if not history:
            result.metrics["consistency"] = {
                "current_streak": 0,
                "longest_streak": 0,
                "missed_days": 0,
            }
            return

        # Collect unique training days in chronological order.
        training_days = sorted({
            entry.date
            for entry in history
        })

        longest_streak = 1
        current_streak = 1
        streak = 1

        # Track consecutive training days.
        for previous, current in zip(
            training_days,
            training_days[1:],
        ):
            if current - previous == timedelta(days=1):
                streak += 1
            else:
                streak = 1

            longest_streak = max(
                longest_streak,
                streak,
            )

        # Calculate the user's current streak ending
        # with the latest recorded workout.
        streak = 1

        for previous, current in zip(
            reversed(training_days[:-1]),
            reversed(training_days[1:]),
        ):
            if current - previous == timedelta(days=1):
                streak += 1
            else:
                break

        current_streak = streak

        # Count missed days between the first and
        # last recorded workout.
        total_days = (
            training_days[-1]
            - training_days[0]
        ).days + 1

        missed_days = total_days - len(training_days)

        result.metrics["consistency"] = {
            "training_days": len(training_days),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "missed_days": missed_days,
        }