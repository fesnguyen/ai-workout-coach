from __future__ import annotations

from copy import deepcopy

from app.workout_analysis.workout_schemas import (
    ExerciseHistory,
)

LB_TO_KG = 0.45359237


class WorkoutNormalizer:
    """
    Normalizes workout history into a canonical representation.

    Responsibilities:
    - Convert all weights to kilograms.
    - Normalize weight units.
    - Preserve workout semantics.
    """

    async def normalize(
        self,
        history: ExerciseHistory,
    ) -> ExerciseHistory:
        """
        Return a normalized copy of the workout history.
        """

        normalized_history = deepcopy(history)

        for entry in normalized_history:
            for exercise_set in entry.sets:
                self._normalize_set(exercise_set)

        return normalized_history

    def _normalize_set(
        self,
        exercise_set,
    ) -> None:
        """
        Normalize a single exercise set.
        """

        if exercise_set.unit == "lb":
            exercise_set.weight = round(
                exercise_set.weight * LB_TO_KG,
                2,
            )
            exercise_set.unit = "kg"