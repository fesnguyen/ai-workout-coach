"""
Application dependency container.
"""

from __future__ import annotations

from app.agent.agent import Agent
from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry
from app.agent.tools.calculator_tool import CalculatorTool
from app.agent.tools.rag_tool import RagTool
from app.configs.llm_settings import llm_settings
from app.configs.rag_settings import rag_settings
from app.llm.base_generator import BaseGenerator
from app.llm.generator_factory import GeneratorFactory
from app.prompts.context_prompt_builder import ContextPromptBuilder
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.embedding.embedder_factory import EmbedderFactory
from app.rag.rag_service import RAGService
from app.workout_analysis.workout_service import WorkoutService
from app.agent.tools.workout_analyzer_tool import WorkoutAnalyzerTool



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

        # Embedder
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
            generator=self.generator,
        )

        # Tool registry
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        registry.register(RagTool(self.rag_service))
        registry.register(WorkoutAnalyzerTool(self.workout_service))

        self.tool_executor = ToolExecutor(registry)

        # Prompt builder
        self.context_prompt_builder = ContextPromptBuilder()

        # Async dependencies (initialized later)
        self._postgres_pool = None
        self.conversation_store = None
        self.conversation_service = None

        # Agent (created during initialization)
        self.agent = None

    async def initialize(self) -> None:
        """
        Initialize all asynchronous application resources.
        """

        # Build the RAG vector database.
        await self.rag_service.initialize()

        # Create the agent after all dependencies are ready.
        self.agent = Agent(
            generator=self.generator,
            tool_executor=self.tool_executor,
            context_prompt_builder=self.context_prompt_builder,
        )

    async def shutdown(self) -> None:
        """
        Release application resources.
        """
        pass