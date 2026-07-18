from app.agent.tools.base_tool import BaseTool


class ToolRegistry:
    """Stores available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {name}") from exc

    def list(self) -> list[BaseTool]:
        return list(self._tools.values())