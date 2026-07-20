from __future__ import annotations

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.workout_schemas import AnalysisResult, CompressionContext


class EmptyMetricCompression(BaseCompression):
    """
    Removes metrics that contain no useful data.
    """

    async def compress(
        self,
        context: CompressionContext,
    ) -> None:
        # Keep only metrics that contain data.
        context.analysis.metrics = {
            name: metric
            for name, metric in context.analysis.metrics.items()
            if metric
        }