from __future__ import annotations

from collections.abc import Sequence

from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.workout_schemas import AnalysisResult, CompressionContext


class WorkoutCompressor:
    """
    Executes a sequence of compression strategies.
    """

    def __init__(
        self,
        compressions: Sequence[BaseCompression],
    ):
        self._compressions = list(compressions)

    async def compress(
        self,
        context: CompressionContext,
    ) -> AnalysisResult:
        # Execute each compression strategy in order.
        for compression in self._compressions:
            await compression.compress(context)

        return context