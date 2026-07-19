"""
Query rewriter for the RAG pipeline.

Responsibilities
----------------
- Rewrite follow-up questions into standalone search queries.
- Resolve pronouns and ambiguous references using conversation history.
- Optimize queries for semantic retrieval.

The rewriter intentionally performs NO:

- retrieval
- embedding
- generation

Pipeline
--------

Conversation History
        │
        ▼
User Query
        │
        ▼
RAGQueryRewriter
        │
        ▼
Standalone Search Query
"""

from __future__ import annotations

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest, Message


SYSTEM_PROMPT = """
You are a search query rewriter.

Your job is to rewrite the user's latest message into a standalone,
retrieval-friendly search query.

Rules

- Preserve the original meaning.
- Resolve pronouns using conversation history.
- Expand implicit references.
- Keep the rewritten query concise.
- DO NOT answer the question.
- DO NOT invent facts.
- DO NOT add information not present in the conversation.
- If the query is already clear, return it unchanged.

Return ONLY the rewritten query.
"""


class RAGQueryRewriter:
    """
    Rewrite conversational queries into retrieval-friendly queries.
    """

    def __init__(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    async def rewrite(
        self,
        query: str,
        history: list[Message] | None = None,
    ) -> str:
        """
        Rewrite a user query for semantic retrieval.

        Parameters
        ----------
        query
            Latest user question.

        history
            Previous conversation messages.

        Returns
        -------
        str
            Standalone retrieval query.
        """

        messages: list[Message] = [
            Message(
                role="system",
                content=SYSTEM_PROMPT,
            ),
        ]

        if history:
            messages.extend(history)

        messages.append(
            Message(
                role="user",
                content=query,
            )
        )

        response = await self._generator.generate(
            GenerationRequest(
                input=messages,
            )
        )

        return response.content.strip()