"""
OpenAI implementation of the language model interface.
"""

from __future__ import annotations

from openai import AsyncOpenAI
import json

from app.api.exceptions import InvalidPreviousResponseError
from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import (
    GenerationRequest,
    GenerationResponse,
    Message,
    ToolCall,
    ToolOutput,
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
        previous_response_id: str = None,
    ) -> GenerationResponse:
        """
        Generate a response using the OpenAI API.
        """

        kwargs = {
            "model": self._model,
            "input": self._build_input(request.messages),
            "max_output_tokens": request.max_tokens,
            "previous_response_id": previous_response_id or None,
        }

        if request.tool_definitions:
            kwargs["tools"] = request.tool_definitions

        try:
            response = await self._client.responses.create(**kwargs)
        except Exception as ex:
            raise InvalidPreviousResponseError(
                "Invalid previous_response_id."
            ) from ex

        # Collect tool calls
        tool_calls = []
        for item in response.output:
            if item.type == "function_call":
                tool_calls.append(
                    ToolCall(
                        id=item.call_id,
                        name=item.name,
                        arguments=json.loads(item.arguments),
                    )
                )

        return GenerationResponse(
            response=response.output_text,
            tool_calls=tool_calls,
            previous_response_id=response.id,
            finish_reason=response.status,
        )

    @staticmethod
    def _build_input(
        messages: list[Message | ToolOutput],
    ) -> list[dict]:
        """
        Convert application messages into the OpenAI input format.
        """

        result: list[dict] = []

        # Structure input base on Message type
        for item in messages:
            if isinstance(item, Message):
                result.append(
                    {
                        "role": item.role,
                        "content": item.content,
                    }
                )

            elif isinstance(item, ToolOutput):
                result.append(
                    {
                        "type": item.type,
                        "call_id": item.call_id,
                        "output": item.output,
                    }
                )

        return result