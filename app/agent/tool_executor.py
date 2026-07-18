from app.llm.llm_schemas import ToolCall, ToolOutput
from app.agent.tool_registry import ToolRegistry


class ToolExecutor:
    """Executes tool calls."""

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry


    @property
    def tool_definitions(self) -> list[dict]:
        return [
            tool.openai_definition
            for tool in self._registry.list()
        ]

    async def execute(
        self,
        tool_calls: list[ToolCall],
    ) -> list[str]:
        """
        Execute all requested tool calls.
        """

        results: list[str] = []

        for tool_call in tool_calls:
            # Get the tool
            tool = self._registry.get(tool_call.name)

            # Execute
            result = await tool.invoke(tool_call.arguments)

            # Append result back
            results.append(
                ToolOutput(
                    call_id=tool_call.id,
                    output=result,
                )
            )

        return results