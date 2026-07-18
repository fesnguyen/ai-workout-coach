"""
Application dependency container.
"""

from __future__ import annotations

from app.agent.agent import Agent
from app.agent.tool_executor import ToolExecutor
from app.agent.tool_registry import ToolRegistry
from app.agent.tools.calculator_tool import CalculatorTool
from app.configs.llm_settings import settings
from app.llm.base_generator import BaseGenerator
from app.llm.generator_factory import GeneratorFactory


class ApplicationContainer:
    """
    Holds shared application services.

    Instances are created once during application startup and reused
    for the lifetime of the application.
    """

    def __init__(self) -> None:
        # Generator
        self.generator: BaseGenerator = GeneratorFactory.create(
            provider=settings.llm_provider,
            api_key=settings.openai_api_key,
            model=settings.openai_model,
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
        

    async def initialize(self) -> None:
        """
        Initialize resources that require asynchronous startup.
        Ex: Local LLM
        """
        pass

    async def shutdown(self) -> None:
        """
        Release application resources.
        """
        pass