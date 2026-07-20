from __future__ import annotations

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class ExerciseGapMetric(BaseMetric):
    """
    Computes the number of days since each exercise
    was last performed.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Skip if there is no workout history.
        if not history:
            result.metrics["exercise_gap"] = {}
            return

        latest_date = max(
            entry.date
            for entry in history
        )

        latest_exercise_dates: dict[str, object] = {}

        # Track the latest workout date for each exercise.
        for entry in history:
            previous = latest_exercise_dates.get(entry.exercise)

            if previous is None or entry.date > previous:
                latest_exercise_dates[entry.exercise] = entry.date

        gaps = {}

        # Compute the number of days since each exercise
        # was last performed.
        for exercise, workout_date in latest_exercise_dates.items():
            gaps[exercise] = {
                "days_since_last_session": (
                    latest_date - workout_date
                ).days,
                "last_session": workout_date.isoformat(),
            }

        result.metrics["exercise_gap"] = gaps