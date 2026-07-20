from __future__ import annotations

from collections import defaultdict

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class VolumeMetric(BaseMetric):
    """
    Computes training volume statistics.

    Volume = Σ(weight × reps)
    """

    async def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        """
        Computes total and per-exercise volume/sets from a workout history 
        and writes the aggregated metrics into the AnalysisResult object.
        """
        # Track overall volume (weight * reps) and total number of sets completed across all exercises
        total_volume = 0.0
        total_sets = 0

        # Accumulate volume and sets grouped by exercise name
        # defaultdict automatically initializes missing keys with 0.0 or 0
        exercise_volume: dict[str, float] = defaultdict(float)
        exercise_sets: dict[str, int] = defaultdict(int)

        # Loop through each workout entry in the provided history
        for entry in history:
            # Loop through every individual set performed in this workout entry
            for exercise_set in entry.sets:
                # Calculate the workload volume for this set
                volume = (
                    exercise_set.weight
                    * exercise_set.reps
                )

                # Update overall totals
                total_volume += volume
                total_sets += 1

                # Update totals specific to this exercise name
                exercise_volume[entry.exercise] += volume
                exercise_sets[entry.exercise] += 1

        # Store the formatted and rounded aggregation metrics directly into the result object
        result.metrics["volume"] = {
            "total_volume": round(total_volume, 2),
            "total_sets": total_sets,
            # Alphabetically sort exercises and construct a breakdown dictionary for each
            "per_exercise": {
                exercise: {
                    "volume": round(
                        exercise_volume[exercise],
                        2,
                    ),
                    "sets": exercise_sets[exercise],
                }
                for exercise in sorted(exercise_volume)
            },
        }