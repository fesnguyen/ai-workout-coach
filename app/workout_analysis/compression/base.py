from __future__ import annotations

from abc import ABC, abstractmethod

from app.workout_analysis.workout_schemas import AnalysisResult


class BaseCompression(ABC):
    """
    Base class for all workout analysis compression strategies.
    """

    @abstractmethod
    async def compress(
        self,
        analysis: AnalysisResult,
    ) -> None:
        """
        Compresses the analysis result in-place.
        """
        ...