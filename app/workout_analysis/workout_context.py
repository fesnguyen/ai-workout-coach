from __future__ import annotations

from collections.abc import Sequence

from app.llm.base_generator import BaseGenerator
from app.prompts.system_prompt_builder import SystemPromptBuilder
from app.workout_analysis.compression.base import BaseCompression
from app.workout_analysis.compression.workout_compressor import WorkoutCompressor
from app.workout_analysis.metrics.base import BaseMetric
from app.workout_analysis.workout_analyzer import WorkoutAnalyzer
from app.workout_analysis.workout_normalizer import WorkoutNormalizer
from app.workout_analysis.workout_prompt_builder import WorkoutPromptBuilder
from app.workout_analysis.workout_validator import WorkoutValidator


class WorkoutContext:
    """
    Holds the shared components required by the workout analysis pipeline.
    """

    def __init__(
        self,
        metrics: Sequence[BaseMetric],
        compressions: Sequence[BaseCompression],
        generator: BaseGenerator,
        system_prompt_builder: SystemPromptBuilder,
    ) -> None:
        self.validator = WorkoutValidator()

        self.normalizer = WorkoutNormalizer()

        self.system_prompt_builder = system_prompt_builder

        self.workout_prompt_builder = WorkoutPromptBuilder(
            self.system_prompt_builder,
        )

        self.generator = generator

        self.analyzer = WorkoutAnalyzer(
            metrics=metrics,
        )

        self.compressor = WorkoutCompressor(
            compressions,
        )