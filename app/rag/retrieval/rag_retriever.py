"""
Retriever for the RAG pipeline.

Responsibilities
----------------
- Perform semantic retrieval.
- Return the most relevant chunks.
- Hide vector database implementation details.

The retriever intentionally performs NO:

- document loading
- chunking
- embedding generation
- context compression
- LLM generation

Pipeline
--------

Query Embedding
        │
        ▼
RAGRetriever
        │
        ▼
Retrieved Chunks
"""

from __future__ import annotations

from app.rag.rag_schemas import Chunk
from app.rag.retrieval.rag_store import RAGStore


class RAGRetriever:
    """
    Semantic retriever.

    The retriever delegates similarity search to the
    underlying vector store.

    It exists primarily to separate retrieval logic from
    storage implementation, making future enhancements
    such as reranking or hybrid retrieval straightforward.
    """

    def __init__(
        self,
        store: RAGStore,
    ) -> None:
        self._store = store

    async def retrieve(
        self,
        embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[Chunk]:
        """
        Retrieve the most relevant chunks.

        Parameters
        ----------
        embedding
            Query embedding.

        top_k
            Maximum number of retrieved chunks.

        Returns
        -------
        list[RetrievedChunk]
        """

        return await self._store.search(
            embedding=embedding,
            top_k=top_k,
        )