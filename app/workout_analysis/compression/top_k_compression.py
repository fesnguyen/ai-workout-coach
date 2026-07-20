from __future__ import annotations

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.workout_schemas import AnalysisResult, CompressionContext


class TopKCompression(BaseCompression):
    """
    Keeps only the top K exercises for selected metrics.
    """

    def __init__(
        self,
        top_k: int = 5,
    ):
        self._top_k = top_k

    async def compress(
        self,
        context: CompressionContext,
    ) -> None:
        # Apply compression to each metric independently.
        for metric in context.analysis.metrics.values():
            if not isinstance(metric, dict):
                continue

            self._compress_metric(metric)

    def _compress_metric(
        self,
        metric: dict,
    ) -> None:
        # Compress nested exercise dictionaries.
        for key, value in metric.items():
            if not isinstance(value, dict):
                continue

            if len(value) <= self._top_k:
                continue

            metric[key] = dict(
                list(value.items())[: self._top_k]
            )