from __future__ import annotations

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class PersonalRecordMetric(BaseMetric):
    """
    Detects the personal record (PR) for each exercise.
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        # Store the best lift found for each exercise.
        records: dict[str, dict] = {}

        for entry in history:
            for exercise_set in entry.sets:

                current = records.get(entry.exercise)

                # Update the PR if a heavier lift is found.
                if (
                    current is None
                    or exercise_set.weight > current["weight"]
                ):
                    records[entry.exercise] = {
                        "weight": exercise_set.weight,
                        "reps": exercise_set.reps,
                        "unit": exercise_set.unit,
                        "date": entry.date.isoformat(),
                    }

        result.metrics["personal_records"] = records