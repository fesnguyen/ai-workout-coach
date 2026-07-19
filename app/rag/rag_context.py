"""
RAG pipeline.

Responsibilities
----------------
- Construct and own all RAG components.
- Wire dependencies between components.
- Expose a unified pipeline for the RAG service.

The pipeline intentionally performs NO business logic.

Business logic belongs to RAGService.

Pipeline
--------

                    RAGPipeline
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
Loader              Chunker             Embedder
                                             │
                                             ▼
                                        Vector Store
                                             │
                                             ▼
                                        Retriever
                                             │
                                             ▼
                                        Compressor

Other Components
----------------

- Guardrail
- Query Rewriter
- Generator
"""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI

from app.llm.base_generator import BaseGenerator
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.ingestion.document_chunker import DocumentChunker
from app.rag.ingestion.document_loader import DocumentLoader
from app.rag.retrieval.rag_compressor import RAGCompressor
from app.rag.embedding.openai_embedder import OpenAIEmbedder
from app.rag.retrieval.rag_guardrail import RAGGuardrail
from app.rag.retrieval.rag_query_rewriter import RAGQueryRewriter
from app.rag.retrieval.rag_retriever import RAGRetriever
from app.rag.retrieval.rag_store import RAGStore


class RAGContext:
    """
    Owns every component of the RAG subsystem.

    Components are constructed once during application startup
    and reused throughout the application's lifetime.
    """

    def __init__(
        self,
        *,
        generator: BaseGenerator,
        embedder: BaseEmbedder,
        knowledge_path: Path,
        database_path: Path,
    ) -> None:
        # ---------------------------------------------------------------------
        # Ingestion
        # ---------------------------------------------------------------------

        self.loader = DocumentLoader(
            knowledge_path=knowledge_path,
        )

        self.chunker = DocumentChunker()

        self.embedder = embedder

        # ---------------------------------------------------------------------
        # Storage & Retrieval
        # ---------------------------------------------------------------------

        self.store = RAGStore(
            database_path=database_path,
        )

        self.retriever = RAGRetriever(
            store=self.store,
        )

        self.compressor = RAGCompressor()

        # ---------------------------------------------------------------------
        # Query Processing
        # ---------------------------------------------------------------------

        self.guardrail = RAGGuardrail(
            generator=generator,
        )

        self.query_rewriter = RAGQueryRewriter(
            generator=generator,
        )

        # ---------------------------------------------------------------------
        # Future Components
        # ---------------------------------------------------------------------

        # self.reranker = RAGReranker()

        # self.generator = RAGGenerator(
        #     generator=generator,
        # )