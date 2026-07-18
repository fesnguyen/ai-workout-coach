"""
Abstract interface for all LLM providers.

Concrete implementations translate between the application's
request/response models and a specific LLM backend.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.schemas import GenerationRequest, GenerationResponse


class BaseGenerator(ABC):
    """
    Contract for language model providers.

    Every provider must expose the same interface so the application
    remains independent of the underlying LLM implementation.
    """

    @property
    @abstractmethod
    def model(self) -> str:
        ...

    @abstractmethod
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """
        Generate a response from the language model.

        Args:
            request: Standardized generation request.

        Returns:
            A standardized generation response.
        """
        raise NotImplementedError