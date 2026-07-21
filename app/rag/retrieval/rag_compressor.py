"""
Context compressor for the RAG pipeline.

Responsibilities
----------------
- Remove duplicate chunks.
- Remove low-confidence retrievals.
- Limit the amount of context sent to the LLM.
- Preserve source attribution.

The compressor intentionally performs NO:

- retrieval
- embedding
- generation

Pipeline
--------

Retrieved Chunks
        │
        ▼
RAGCompressor
        │
        ▼
Filtered Chunks
"""

from __future__ import annotations

from app.rag.rag_schemas import Chunk, RetrievedChunk


class RAGCompressor:
    """
    Compress retrieved context before generation.

    The goal is not summarization.

    The goal is to maximize useful information while staying
    within the model's context budget.
    """

    def __init__(
        self,
        *,
        max_chunks: int = 5,
        min_score: float = 0.3,
    ) -> None:
        self._max_chunks = max_chunks
        self._min_score = min_score

    async def compress(
        self,
        retrieved_chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """
        Compress retrieved chunks.

        Strategy

        1. Sort by relevance
        2. Remove duplicates
        3. Remove low-score chunks
        4. Keep only the best N chunks
        """

        if not retrieved_chunks:
            return []

        retrieved_chunks = sorted(
            retrieved_chunks,
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        retrieved_chunks = self._remove_duplicates(retrieved_chunks)

        retrieved_chunks = [
            chunk
            for chunk in retrieved_chunks
            if chunk.score >= self._min_score
        ]

        return retrieved_chunks[: self._max_chunks]

    @staticmethod
    def _remove_duplicates(
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """
        Remove duplicate chunks.

        Duplicate detection is based on chunk id.
        """

        unique: list[RetrievedChunk] = []

        seen: set[str] = set()

        for chunk in chunks:

            if chunk.chunk.id in seen:
                continue

            seen.add(chunk.chunk.id)

            unique.append(chunk)

        return unique