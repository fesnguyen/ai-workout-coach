from __future__ import annotations
import uuid

from app.agent.tool_executor import ToolExecutor
from app.api.api_schemas import ChatRequest, ChatResponse
from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import (
    GenerationRequest,
    GenerationResponse,
    Message,
)
from app.prompts.context_prompt_builder import ContextPromptBuilder


class Agent:
    """
    Agent workflow
    Standard workflow
    User
            ↓
        LLM
            ↓
        Tool(s)
            ↓
        LLM
            ↓
        Final response
    """

    def __init__(
        self,
        generator: BaseGenerator,
        tool_executor: ToolExecutor,
        context_prompt_builder: ContextPromptBuilder,
        max_iterations: int = 5,
    ) -> None:
        self._generator = generator
        self._tool_executor = tool_executor
        self._max_iterations = max_iterations

        self._context_prompt_builder = context_prompt_builder

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Execute the agent workflow until the model returns a final response.
        """

        # Build the initial request based on whether this starts a new conversation.
        previous_response_id = request.previous_response_id
        history = [
            Message(
                role="user",
                content=request.message,
            ),
        ]

        if previous_response_id is None:
            history = [
                *self._context_prompt_builder.build(),
                *history,
            ]

        # Execute the tool-calling loop until the model returns a final response.
        for iteration in range(self._max_iterations):

            # Send the initial request once, then continue with only the latest
            # tool outputs because the Responses API reconstructs the context.
            request_messages = (
                history
                if iteration == 0
                else history[-len(tool_outputs):]
            )

            response: GenerationResponse = await self._generator.generate(
                GenerationRequest(
                    messages=request_messages,
                    tool_definitions=self._tool_executor.tool_definitions,
                ),
                previous_response_id,
            )

            # Return the final response once no additional tool calls are requested.
            if not response.tool_calls:
                return ChatResponse(
                    previous_response_id=response.previous_response_id,
                    answer=response.response,
                )

            # Execute the requested tools and append their outputs for the next iteration.
            tool_outputs = await self._tool_executor.execute(
                response.tool_calls,
            )

            history.extend(tool_outputs)

            # Continue the Responses API chain in the next iteration.
            previous_response_id = response.previous_response_id

        raise RuntimeError(
            f"Agent exceeded the maximum iterations ({self._max_iterations})."
        )