from __future__ import annotations

from app.workout_analysis.workout_schemas import ExerciseHistory


class WorkoutValidationError(ValueError):
    """
    Raised when workout history violates business validation rules.
    """


class WorkoutValidator:
    """
    Validates workout history before analysis.

    Responsibilities:
    - Ensure required workout data exists.
    - Verify chronological ordering.
    - Validate business constraints.
    - Reject impossible values.
    """

    async def validate(
        self,
        history: ExerciseHistory,
    ) ->None:
        if not history:
            raise WorkoutValidationError(
                "Workout history is empty."
            )

        self._validate_chronology(history)
        self._validate_exercises(history)
        self._validate_sets(history)

    @staticmethod
    def _validate_chronology(
        history: ExerciseHistory,
    ) ->None:
        previous_date = history[0].date

        for entry in history[1:]:
            if entry.date < previous_date:
                raise WorkoutValidationError(
                    "Workout history must be sorted chronologically."
                )

            previous_date = entry.date

    @staticmethod
    def _validate_exercises(
        history: ExerciseHistory,
    ) ->None:
        for entry in history:
            if not entry.exercise.strip():
                raise WorkoutValidationError(
                    "Exercise name cannot be empty."
                )

    @staticmethod
    def _validate_sets(
        history: ExerciseHistory,
    ) ->None:
        for entry in history:
            if not entry.sets:
                raise WorkoutValidationError(
                    f"{entry.exercise} contains no sets."
                )

            for exercise_set in entry.sets:

                if exercise_set.reps <= 0:
                    raise WorkoutValidationError(
                        f"{entry.exercise} contains an invalid repetition count."
                    )

                # Zero weight is valid (bodyweight exercises).
                if exercise_set.weight < 0:
                    raise WorkoutValidationError(
                        f"{entry.exercise} contains a negative weight."
                    )

                # Optional, if your schema includes a unit field.
                if hasattr(exercise_set, "unit"):
                    if exercise_set.unit not in {"kg", "lb"}:
                        raise WorkoutValidationError(
                            f"{entry.exercise} contains an unsupported weight unit."
                        )