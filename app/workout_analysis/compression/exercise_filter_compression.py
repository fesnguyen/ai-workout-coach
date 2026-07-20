from __future__ import annotations

import re

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.workout_schemas import AnalysisResult, CompressionContext


class ExerciseFilterCompression(BaseCompression):
    """
    Keeps only the exercises explicitly mentioned in the query.
    """

    async def compress(
        self,
        context: CompressionContext,
    ) -> None:
        # Find all exercise names that appear in the analysis.
        exercise_names = self._extract_exercises(context.analysis)

        # Determine which exercises are referenced by the user.
        matched_exercises = {
            exercise
            for exercise in exercise_names
            if re.search(
                rf"\b{re.escape(exercise)}\b",
                context.query,
                flags=re.IGNORECASE,
            )
        }

        # Skip compression if no exercise is mentioned.
        if not matched_exercises:
            return

        # Filter each metric to include only the matched exercises.
        for metric in context.analysis.metrics.values():
            if not isinstance(metric, dict):
                continue

            self._filter_metric(
                metric=metric,
                exercises=matched_exercises,
            )

    def _extract_exercises(
        self,
        analysis: AnalysisResult,
    ) -> set[str]:
        exercises = set()

        for metric in analysis.metrics.values():
            if not isinstance(metric, dict):
                continue

            for value in metric.values():
                if isinstance(value, dict):
                    exercises.update(value.keys())

        return exercises

    def _filter_metric(
        self,
        metric: dict,
        exercises: set[str],
    ) -> None:
        for key, value in metric.items():
            if not isinstance(value, dict):
                continue

            metric[key] = {
                exercise: data
                for exercise, data in value.items()
                if exercise in exercises
            }