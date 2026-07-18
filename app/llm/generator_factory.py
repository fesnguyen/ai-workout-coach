"""
Factory for creating LLM providers.
"""

from app.llm.base_generator import BaseGenerator
from app.llm.openai_generator import OpenAIGenerator


class GeneratorFactory:
    """
    Creates language model providers from configuration.
    """

    @staticmethod
    def create(
        provider: str,
        **kwargs,
    ) -> BaseGenerator:
        """
        Create an LLM provider.

        Args:
            provider: Provider identifier.
            **kwargs: Provider-specific configuration.

        Returns:
            Configured language model provider.

        Raises:
            ValueError: If the provider is not supported.
        """

        match provider.lower():
            case "openai":
                return OpenAIGenerator(**kwargs)

            case _:
                raise ValueError(f"Unsupported LLM provider: {provider}")