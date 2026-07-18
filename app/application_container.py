"""
Application dependency container.
"""

from __future__ import annotations

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
        self.generator: BaseGenerator = GeneratorFactory.create(
            provider=settings.llm_provider,
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

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