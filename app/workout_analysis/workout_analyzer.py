from __future__ import annotations

from collections.abc import Sequence

from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class WorkoutAnalyzer:
    """
    Executes all registered workout analysis metrics.
    """

    def __init__(
        self,
        metrics: Sequence[BaseMetric],
    ) -> None:
        self._metrics = list(metrics)

    async def analyze(
        self,
        history: ExerciseHistory,
    ) -> AnalysisResult:
        """
        Analyze a workout history by executing every metric.
        """

        result = AnalysisResult()

        for metric in self._metrics:
            await metric.compute(
                history=history,
                result=result,
            )

        return result