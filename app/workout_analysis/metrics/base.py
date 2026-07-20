from __future__ import annotations

from abc import ABC, abstractmethod

from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    ExerciseHistory,
)


class BaseMetric(ABC):
    """
    Base class for all workout analysis metrics.
    """

    @abstractmethod
    def compute(
        self,
        history: ExerciseHistory,
        result: AnalysisResult,
    ) -> None:
        """
        Computes a metric and stores the result in the shared AnalysisResult.
        """
        raise NotImplementedError