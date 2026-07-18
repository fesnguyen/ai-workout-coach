"""
OpenAI implementation of the language model interface.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from app.llm.base_generator import BaseGenerator
from app.llm.schemas import (
    GenerationRequest,
    GenerationResponse,
    Message,
    TokenUsage,
)


class OpenAIGenerator(BaseGenerator):
    """
    OpenAI-backed language model provider.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    
    @property
    def model(self) -> str:
        return self._model

    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """
        Generate a response using the OpenAI API.
        """

        kwargs = {
            "model": self._model,
            "input": self._build_input(request.messages),
            "max_output_tokens": request.max_tokens,
        }

        response = await self._client.responses.create(**kwargs)

        return GenerationResponse(
            content=response.output_text,
            usage=TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens,
            )
            if response.usage
            else None,
            finish_reason=response.status,
        )

    @staticmethod
    def _build_input(
        messages: list[Message],
    ) -> list[dict]:
        """
        Convert application messages into the OpenAI input format.
        """

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]