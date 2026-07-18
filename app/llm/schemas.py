"""
Shared request and response models for LLM providers.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    A single conversation message.
    """

    role: str
    content: str


class ToolDefinition(BaseModel):
    """
    A tool available to the language model.
    """

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """
    A tool invocation requested by the language model.
    """

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """
    Standardized request for text generation.
    """

    messages: list[Message]

    tools: list[ToolDefinition] = Field(default_factory=list)

    response_schema: dict[str, Any] | None = None

    temperature: float = 0.2

    max_tokens: int | None = None


class TokenUsage(BaseModel):
    """
    Token usage reported by the provider.
    """

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0


class GenerationResponse(BaseModel):
    """
    Standardized response returned by all providers.
    """

    content: str

    tool_calls: list[ToolCall] = Field(default_factory=list)

    usage: TokenUsage | None = None

    finish_reason: str | None = None