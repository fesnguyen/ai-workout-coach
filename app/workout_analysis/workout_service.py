from __future__ import annotations

from app.api.api_schemas import WorkoutAnalyzeRequest
from app.workout_analysis.compression.empty_metric_compression import EmptyMetricCompression
from app.workout_analysis.compression.exercise_filter_compression import ExerciseFilterCompression
from app.workout_analysis.compression.metric_selection_compression import MetricSelectionCompression
from app.workout_analysis.compression.top_k_compression import TopKCompression
from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.metrics.consistency_metric import ConsistencyMetric
from app.workout_analysis.metrics.exercise_distribution_metric import ExerciseDistributionMetric
from app.workout_analysis.metrics.exercise_gap_metric import ExerciseGapMetric
from app.workout_analysis.metrics.frequency_metric import FrequencyMetric
from app.workout_analysis.metrics.intensity_metric import IntensityMetric
from app.workout_analysis.metrics.personal_record_metric import PersonalRecordMetric
from app.workout_analysis.metrics.progression_metric import ProgressionMetric
from app.workout_analysis.metrics.recovery_metric import RecoveryMetric
from app.workout_analysis.metrics.volume_metric import VolumeMetric
from app.workout_analysis.workout_context import WorkoutContext
from app.workout_analysis.workout_schemas import (
    AnalysisResult,
    CompressionContext,
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
    ) -> None:
        self._context = WorkoutContext(
            metrics=[
                VolumeMetric(),
                FrequencyMetric(),
                ProgressionMetric(),
                PersonalRecordMetric(),
                ConsistencyMetric(),
                ExerciseDistributionMetric(),
                RecoveryMetric(),
                ExerciseGapMetric(),
                IntensityMetric(),
            ],
            compressions=[
                EmptyMetricCompression(),
                # TopKCompression(),
                # ExerciseFilterCompression(),
                # MetricSelectionCompression(),
            ],
        )

    async def analyze(
        self,
        analysisRequest: WorkoutAnalyzeRequest,
    ) -> AnalysisResult:
        """
        Analyze a user's workout history.
        """

        await self._context.validator.validate(analysisRequest.history)

        analysis =  await self._context.analyzer.analyze(analysisRequest.history)

        compressed_analysis = await self._context.compressor.compress(
            CompressionContext(
                analysis=analysis,
                query=analysisRequest.query,
            )
        )

        return compressed_analysis