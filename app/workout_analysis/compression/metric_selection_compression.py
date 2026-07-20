from __future__ import annotations

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.workout_schemas import CompressionContext


class MetricSelectionCompression(BaseCompression):
    """
    Keeps only the metrics relevant to the user's query.
    """

    _METRIC_MAPPING: dict[str, set[str]] = {
        "progress": {
            "progression",
            "personal_records",
            "intensity",
        },
        "trend": {
            "progression",
            "personal_records",
            "intensity",
        },
        "strength": {
            "progression",
            "personal_records",
            "intensity",
        },
        "recover": {
            "recovery",
            "exercise_gap",
        },
        "rest": {
            "recovery",
            "exercise_gap",
        },
        "consistent": {
            "consistency",
            "frequency",
        },
        "frequency": {
            "frequency",
            "consistency",
        },
        "volume": {
            "volume",
            "frequency",
        },
        "neglect": {
            "exercise_distribution",
            "exercise_gap",
        },
        "distribution": {
            "exercise_distribution",
        },
    }

    async def compress(
        self,
        context: CompressionContext,
    ) -> None:
        # Normalize the query for keyword matching.
        query = context.query.lower()

        selected_metrics: set[str] = set()

        # Collect all metrics relevant to the detected keywords.
        for keyword, metrics in self._METRIC_MAPPING.items():
            if keyword in query:
                selected_metrics.update(metrics)

        # Skip compression if no matching keywords are found.
        if not selected_metrics:
            return

        # Keep only the selected metrics.
        context.analysis.metrics = {
            name: metric
            for name, metric in context.analysis.metrics.items()
            if name in selected_metrics
        }