from __future__ import annotations

from collections.abc import Sequence

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.compression.workout_compressor import WorkoutCompressor
from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_analyzer import WorkoutAnalyzer
from app.workout_analysis.workout_validator import WorkoutValidator


class WorkoutContext:
    """
    Holds the shared components required by the workout analysis pipeline.
    """

    def __init__(
        self,
        metrics: Sequence[BaseMetric],
        compressions: Sequence[BaseCompression],
    ) -> None:
        self.validator = WorkoutValidator()

        self.analyzer = WorkoutAnalyzer(
            metrics=metrics,
        )

        self.compressor = WorkoutCompressor(
            compressions,
        )