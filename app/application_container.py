"""
Application dependency container.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from app.agent.agent import Agent
from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry
from app.agent.tools.calculator_tool import CalculatorTool
from app.configs.llm_settings import llm_settings
from app.configs.rag_settings import rag_settings
from app.llm.base_generator import BaseGenerator
from app.llm.generator_factory import GeneratorFactory
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.embedding.embedder_factory import EmbedderFactory
from app.rag.embedding.openai_embedder import OpenAIEmbedder
from app.rag.rag_service import RAGService
from app.workout_analysis.metrics.consistency_metric import ConsistencyMetric
from app.workout_analysis.metrics.exercise_distribution_metric import ExerciseDistributionMetric
from app.workout_analysis.metrics.exercise_gap_metric import ExerciseGapMetric
from app.workout_analysis.metrics.frequency_metric import FrequencyMetric
from app.workout_analysis.metrics.intensity_metric import IntensityMetric
from app.workout_analysis.metrics.personal_record_metric import PersonalRecordMetric
from app.workout_analysis.metrics.progression_metric import ProgressionMetric
from app.workout_analysis.metrics.recovery_metric import RecoveryMetric
from app.workout_analysis.metrics.volume_metric import VolumeMetric
from app.workout_analysis.workout_analyzer import WorkoutAnalyzer
from app.workout_analysis.workout_service import WorkoutService


class ApplicationContainer:
    """
    Holds shared application services.

    Instances are created once during application startup and reused
    for the lifetime of the application.
    """

    def __init__(self) -> None:
        # Generator
        self.generator: BaseGenerator = GeneratorFactory.create(
            provider=llm_settings.llm_provider,
            api_key=llm_settings.openai_api_key,
            model=llm_settings.openai_model,
        )

        # Tool executor
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        executor = ToolExecutor(registry)

        # Agent who hold the workflow
        agent = Agent(
            generator=self.generator,
            tool_executor=executor,
        )
        self.agent = agent

        self.embedder: BaseEmbedder = EmbedderFactory.create(
            provider=rag_settings.embedding_provider,
            api_key=rag_settings.openai_api_key,
            model=rag_settings.model,
        )

        # RAG
        self.rag_service = RAGService(
            generator=self.generator,
            embedder=self.embedder,
            knowledge_path=rag_settings.rag_knowledge_path,
            database_path=rag_settings.rag_database_path,
        )

        # Workout analysis
        self.workout_service = WorkoutService(
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
        )
        

    async def initialize(self) -> None:
        # Init RAG embedding
        await self.rag_service.initialize()
        pass

    async def shutdown(self) -> None:
        """
        Release application resources.
        """
        pass