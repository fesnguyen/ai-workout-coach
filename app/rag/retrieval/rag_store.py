"""
Persistent vector store for the RAG pipeline.

Responsibilities
----------------
- Store chunk embeddings.
- Perform semantic search.
- Support incremental indexing.
- Persist the vector database.

The store intentionally performs NO:

- document loading
- chunking
- embedding generation
- LLM calls

Pipeline
--------

Chunk
    │
    ▼
Embedding
    │
    ▼
RAGStore
    │
    ▼
ChromaDB
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.rag.rag_schemas import Chunk


class RAGStore:
    """
    Persistent ChromaDB vector store.

    Documents are uniquely identified by Chunk.id,
    allowing incremental indexing without rebuilding
    the entire database.
    """

    COLLECTION_NAME = "knowledge"

    def __init__(
        self,
        database_path: Path,
    ) -> None:

        # Create database, dir to db path
        self._client = chromadb.PersistentClient(
            path=str(database_path),
        )

        # Config collection, remove old data for metadata changes take effect
        self._collection: Collection = (
            self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        )

    async def upsert(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """
        Insert or update chunk embeddings.

        Existing chunk IDs are updated.

        New chunk IDs are inserted.
        """

        if not chunks:
            return

        self._collection.upsert(
            ids=[
                chunk.id
                for chunk in chunks
            ],
            embeddings=embeddings,
            documents=[
                chunk.content
                for chunk in chunks
            ],
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "source": str(chunk.source),
                    "chunk_index": chunk.index,
                }
                for chunk in chunks
            ],
        )

    async def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[Chunk]:
        """
        Perform semantic similarity search.
        """

        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        chunks: list[Chunk] = []

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, document, metadata, distance in zip(
            ids,
            docs,
            metas,
            distances,
        ):
            chunks.append(
                Chunk(
                    id=chunk_id,
                    document_id=metadata["document_id"],
                    source=metadata["source"],
                    index=metadata["chunk_index"],
                    content=document,
                    score=1.0 - distance,
                )
            )

        return chunks

    async def contains(
        self,
        chunk_id: str,
    ) -> bool:
        """
        Check whether a chunk already exists.
        """

        result = self._collection.get(
            ids=[chunk_id],
        )

        return len(result["ids"]) > 0

    async def count(self) -> int:
        """
        Return the number of indexed chunks.
        """

        return self._collection.count()

    async def reset(self) -> None:
        """
        Delete every indexed chunk.
        """

        self._client.delete_collection(
            self.COLLECTION_NAME,
        )

        self._collection = (
            self._client.create_collection(
                self.COLLECTION_NAME,
            )
        )

    
    async def delete(
        self,
        source: str,
    ) -> None:
        """
        Delete every chunk belonging to a document.
        """

        self._collection.delete(
            where={
                "source": source,
            },
        )