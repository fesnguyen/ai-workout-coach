"""
RAG ingestion service.

Responsibilities
----------------
- Synchronize the knowledge base with the vector database.
- Execute incremental indexing plans.

The ingestion service orchestrates the indexing workflow.

It intentionally contains no document loading, hashing,
chunking, embedding, or storage implementations.
"""

from __future__ import annotations

from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.ingestion.document_chunker import DocumentChunker
from app.rag.ingestion.document_hasher import DocumentHasher
from app.rag.ingestion.document_loader import DocumentLoader
from app.rag.ingestion.index_planner import IndexPlanner
from app.rag.ingestion.manifest_store import ManifestStore
from app.rag.rag_schemas import Chunk, IndexedDocument
from app.rag.retrieval.rag_store import RAGStore


class IngestionService:
    """
    Synchronizes the knowledge base with the vector store.
    """

    def __init__(
        self,
        *,
        loader: DocumentLoader,
        chunker: DocumentChunker,
        hasher: DocumentHasher,
        planner: IndexPlanner,
        manifest: ManifestStore,
        embedder: BaseEmbedder,
        store: RAGStore,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._hasher = hasher
        self._planner = planner
        self._manifest = manifest
        self._embedder = embedder
        self._store = store

    async def sync(self) -> None:
        """
        Synchronize the knowledge base with the vector database.
        """

        # Load every document from the knowledge base.
        documents = await self._loader.load()

        # Build a lookup table for fast source -> document access.
        documents_by_source = {
            document.source: document
            for document in documents
        }

        # Compute the current hash of every document.
        indexed_documents = [
            IndexedDocument(
                source=document.source,
                hash=self._hasher.hash_file(
                    document.source,
                ),
            )
            for document in documents
        ]

        # Determine which documents added, modified, deleted.
        plan = self._planner.plan(indexed_documents)

        # Collect docs, chunks that will be embedded in one batch.
        pending_chunks: list[Chunk] = []
        pending_documents: list[IndexedDocument] = []

        # Collect added documents.
        for indexed_document in plan.added:
            document = documents_by_source[
                indexed_document.source
            ]

            pending_chunks.extend(
                await self._chunker.chunk_document(document)
            )

            pending_documents.append(
                indexed_document
            )

        # Collect modified documents.
        for indexed_document in plan.modified:
            await self._store.delete(
                source=str(indexed_document.source),
            )

            document = documents_by_source[
                indexed_document.source
            ]

            pending_chunks.extend(
                await self._chunker.chunk_document(document)
            )

            pending_documents.append(
                indexed_document
            )

        # Remove deleted documents.
        for source in plan.deleted:
            await self._store.delete(
                source=str(source),
            )

            self._manifest.delete(
                str(source),
            )

        # Embed every pending chunk in a single batch.
        if pending_chunks:
            embeddings = await self._embedder.embed_documents(
                [
                    chunk.content
                    for chunk in pending_chunks
                ]
            )
            
            # Persist all chunks in one operation.
            await self._store.upsert(
                chunks=pending_chunks,
                embeddings=embeddings,
            )

            # Update the manifest only after a successful upsert.
            for indexed_document in pending_documents:
                self._manifest.upsert(
                    source=str(indexed_document.source),
                    hash_value=indexed_document.hash,
                )