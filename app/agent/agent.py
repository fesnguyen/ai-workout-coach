from __future__ import annotations

from app.agent.tool_executor import ToolExecutor
from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import (
    GenerationRequest,
    GenerationResponse,
    Message,
)


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
        max_iterations: int = 5,
    ) -> None:
        self._generator = generator
        self._tool_executor = tool_executor
        self._max_iterations = max_iterations

    async def invoke(
        self,
        messages: list[Message],
        previous_response_id: str = None,
    ) -> str:
        """
        Execute the agent loop until the model returns
        a final response or the iteration limit is reached.
        """

        history = list(messages)

        for i in range(self._max_iterations):
            # Item centric strategy, provide managed the conversation flow/cache
            # => If it's first invoke generator, send full message
            # From the second time, only send the last message + previous_response_id
            response: GenerationResponse = await self._generator.generate(
                GenerationRequest(
                    messages=(history if i == 0 else [history[-1]]),
                    tool_definitions=self._tool_executor.tool_definitions,
                ),
                previous_response_id
            )

            # Output to use once no more tool call
            if not response.tool_calls:
                return response.response

            # Execute tool
            tool_outputs = await self._tool_executor.execute(
                response.tool_calls,
            )

            # Append tool output to the messages
            history.extend(tool_outputs)

            # Saving response id for next generation
            previous_response_id = response.previous_response_id

        raise RuntimeError(
            f"Agent exceeded the maximum iterations ({self._max_iterations})."
        )