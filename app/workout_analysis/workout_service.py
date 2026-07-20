from __future__ import annotations

from app.api.api_schemas import WorkoutAnalyzeRequest
from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_context import WorkoutContext
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)
from app.workout_analysis.workout_validator import WorkoutValidator
from app.workout_analysis.workout_analyzer import WorkoutAnalyzer


class WorkoutService:
    """
    Coordinates the workout analysis pipeline.

    Pipeline:

        Validate
            ↓
        Analyze
            ↓
        Return structured analysis
    """

    def __init__(
        self,
        metrics: list[BaseMetric],
    ) -> None:
        self._context = WorkoutContext(
            metrics=metrics
        )

    async def analyze(
        self,
        analysisRequest: WorkoutAnalyzeRequest,
    ) -> AnalysisResult:
        """
        Analyze a user's workout history.
        """

        await self._context.validator.validate(analysisRequest.history)

        return await self._context.analyzer.analyze(analysisRequest.history)