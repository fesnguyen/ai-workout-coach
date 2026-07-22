"""
Build static system prompts for different LLM tasks.
"""

from app.llm.llm_schemas import Message
from app.prompts.static_system_prompts import (
    DEVELOPER_NOTES,
    KNOWLEDGE_RULES,
    RESPONSE_RULES,
    SAFETY_RULES,
    SYSTEM_PROMPT,
    TOOL_RULES,
)


def _build(*sections: str) -> list[Message]:
    """Build a list of system messages from prompt sections."""
    return [
        Message(
            role="system",
            content=section,
        )
        for section in sections
    ]


class SystemPromptBuilder:
    """Build prompt templates."""

    def build_agent_prompt(self) -> list[Message]:
        return _build(
            SYSTEM_PROMPT,
            DEVELOPER_NOTES,
            SAFETY_RULES,
            KNOWLEDGE_RULES,
            TOOL_RULES,
            RESPONSE_RULES,
        )

    def build_rag_prompt(self) -> list[Message]:
        return _build(
            DEVELOPER_NOTES,
            SAFETY_RULES,
            KNOWLEDGE_RULES,
            RESPONSE_RULES,
        )

    def build_workout_analysis_prompt(self) -> list[Message]:
        return _build(
            SYSTEM_PROMPT,
            DEVELOPER_NOTES,
            SAFETY_RULES,
            KNOWLEDGE_RULES,
        )