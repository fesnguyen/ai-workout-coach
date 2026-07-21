from __future__ import annotations

import json

from app.agent.tools.base_tool import BaseTool
from app.rag.rag_service import RAGService


class RagTool(BaseTool):
    """
    Retrieves relevant knowledge from the fitness knowledge base.

    This tool is intended for agent workflows. It returns the retrieved
    knowledge as structured data instead of generating a final answer.
    The coach agent is responsible for combining this information with
    other tool results into a single response.
    """

    def __init__(
        self,
        rag_service: RAGService,
    ) -> None:
        self._rag_service = rag_service

    @property
    def name(self) -> str:
        return "rag_search"

    @property
    def openai_definition(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": (
                "Search the fitness knowledge base for factual information, "
                "exercise guidance, training principles, rehabilitation "
                "advice, and coaching best practices."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The search query describing the information "
                            "to retrieve from the knowledge base."
                        ),
                    }
                },
                "required": [
                    "query",
                ],
                "additionalProperties": False,
            },
            "strict": True,
        }

    async def invoke(
        self,
        arguments: dict[str, object],
    ) -> str:
        # Extract the search query.
        query = str(arguments["query"])

        # Retrieve the relevant knowledge without generating a user-facing
        # response.
        chunks, _ = (
            await self._rag_service.search_context(
                query=query,
            )
        )

        # Return an empty result when no supporting evidence is found.
        if not chunks:
            return json.dumps(
                {
                    "chunks": [],
                }
            )

        # Serialize the retrieved chunks for the agent.
        return json.dumps(
            {
                "chunks": [
                    {
                        "content": chunk.content,
                        "score": chunk.score,
                        "source": str(chunk.source),
                    }
                    for chunk in chunks
                ]
            },
            ensure_ascii=False,
        )