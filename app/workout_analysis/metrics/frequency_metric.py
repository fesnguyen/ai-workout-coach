from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class FrequencyMetric(BaseMetric):
    """
    Computes workout frequency statistics.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        """
        Computes workout frequency metrics (total sessions, distinct training days, 
        weekly frequency, and per-exercise session counts) over a date range and 
        writes them into the AnalysisResult object.
        """

        # Extract unique workout dates using a set set comprehension
        training_days = {entry.date for entry in history}

        # Count how many times each exercise was performed overall
        per_exercise: dict[str, int] = defaultdict(int)

        for entry in history:
            per_exercise[entry.exercise] += 1

        # Identify the start and end dates across the workout history
        first_day = min(training_days)
        last_day = max(training_days)

        # Calculate total date span in days (inclusive of the start day)
        # Uses max(..., 1) so a single-day workout history defaults to 1 day instead of 0
        duration_days = max(
            (last_day - first_day).days + 1,
            1,
        )

        # Convert the total active timeframe into weeks
        duration_weeks = duration_days / 7

        # Store aggregated frequency metrics into the result object
        result.metrics["frequency"] = {
            "total_sessions": len(history),
            "training_days": len(training_days),
            # Calculate average sessions per week over the active timeframe
            "sessions_per_week": round(
                len(history) / duration_weeks,
                2,
            ),
            # Sort exercise session counts alphabetically by exercise name
            "per_exercise": dict(
                sorted(per_exercise.items())
            ),
        }