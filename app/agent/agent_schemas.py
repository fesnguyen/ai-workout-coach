from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    name: str
    result: str
