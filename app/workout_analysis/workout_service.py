from __future__ import annotations
from pathlib import Path
from textwrap import indent
import uuid

from langchain_text_splitters import json

from app.api.api_schemas import WorkoutAnalyzeRequest, WorkoutAnalyzeResponse
from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest
from app.prompts.system_prompt_builder import SystemPromptBuilder
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
        generator: BaseGenerator,
        system_prompt_builder: SystemPromptBuilder,
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
            generator=generator,
            system_prompt_builder=system_prompt_builder,
        )

    async def analyze(
        self,
        analysis_request: WorkoutAnalyzeRequest,
    ) -> WorkoutAnalyzeResponse:
        """
        Analyze a user's workout history.
        """

        # Validate the user's workout data structure before analysis
        await self._context.validator.validate(
            analysis_request.user_profile.workouts
        )

        # Run core analytics to compute volume, frequency, progression, and PR metrics
        analysis = await self._context.analyzer.analyze(
            analysis_request.user_profile.workouts
        )

        # Compress the raw metrics to fit context limits while retaining relevant query details
        compressed_analysis = await self._context.compressor.compress(
            CompressionContext(
                analysis=analysis,
                query=analysis_request.query,
            )
        )

        # Persist the raw analysis result to storage (JSON/DB) and retrieve the generated user ID
        user_id = await self._save_analysis_result(
            user_name=analysis_request.user_profile.name,
            analysis_result=compressed_analysis,
        )

        # Invoke generator to synthesize natural language insights from the analysis
        response = await self._invoke_generator(
            analysis=compressed_analysis,
            query=analysis_request.query,
        )

        # Return the final structured response with the LLM output and reference user ID
        return WorkoutAnalyzeResponse(
            response=response,
            user_id=user_id,
        )
    
    async def _invoke_generator(
        self,
        analysis: AnalysisResult,
        query: str,
    ) -> str:
        """
        Invoke the LLM generator to answer a user's query based on their workout analysis.
        """

        analysis_messages = self._context.workout_prompt_builder.build(
            query=query,
            analysis=analysis,
        )

        # Call the LLM generator to synthesize natural language insights from the analysis
        response = await self._context.generator.generate(
            GenerationRequest(
                messages=analysis_messages,
                tool_definitions=[]
            )
        )

        return response.response

    
    async def _save_analysis_result(
        self,
        user_name: str,
        analysis_result: AnalysisResult,
    )-> str:
        """
        Save workout analysis result
        """
        output_dir = Path("data/workout_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        user_id = f"{user_name}_{uuid.uuid4().hex}"

        filename = f"{user_id}.json"
        file_path = output_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(analysis_result.model_dump_json(indent=2))

        return user_id

    
    async def load_analysis(
        self,
        user_id: str,
    ) -> str:
        """
        Load workout analysis from json file
        """
        file_path = Path(f"data/workout_analysis/{user_id}.json")

        if not file_path.exists():
            raise FileNotFoundError(f"Analysis result for user_id {user_id} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            analysis_json = f.read()

        # Return analysis result as JSON string
        return analysis_json