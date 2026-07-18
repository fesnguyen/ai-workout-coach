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



class GenerationRequest(BaseModel):
    """
    Standardized request for text generation.
    """

    messages: list[Message | ToolOutput]

    tool_definitions: list[dict[str, Any]] = Field(default_factory=list)

    max_tokens: int | None = None


class ToolCall(BaseModel):
    """
    A tool invocation requested by the language model.
    """

    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolOutput(BaseModel):
    """
    Tool result, our answer to the tool call
    """
    # Natively required by openai
    type: str = "function_call_output"

    # Call ID, must match the tool call ID
    call_id: str

    # Tool output
    output: str


class GenerationResponse(BaseModel):
    """
    Standardized response returned by all providers.
    """

    previous_response_id: str | None = None

    response: str

    tool_calls: list[ToolCall] = Field(default_factory=list)

    finish_reason: str | None = None