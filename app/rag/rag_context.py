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

from app.llm.base_generator import BaseGenerator
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.ingestion.document_chunker import DocumentChunker
from app.rag.ingestion.document_hasher import DocumentHasher
from app.rag.ingestion.document_loader import DocumentLoader
from app.rag.ingestion.index_planner import IndexPlanner
from app.rag.ingestion.ingestion_service import IngestionService
from app.rag.ingestion.manifest_store import ManifestStore
from app.rag.retrieval.prompt_builder import PromptBuilder
from app.rag.retrieval.query_analyzer import QueryAnalyzer
from app.rag.retrieval.query_normalizer import QueryNormalizer
from app.rag.retrieval.query_preprocessor import QueryPreprocessor
from app.rag.retrieval.rag_compressor import RAGCompressor
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

        self.generator = generator

        self.prompt_builder = PromptBuilder()

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

        self.hasher = DocumentHasher()
        self.manifest = ManifestStore(
            database_path=database_path
        )
        self.planner = IndexPlanner(
            self.manifest,
        )

        self.ingestion = IngestionService(
            loader=self.loader,
            chunker=self.chunker,
            hasher=self.hasher,
            planner=self.planner,
            manifest=self.manifest,
            embedder=self.embedder,
            store=self.store,
        )

        self.query_normalizer = QueryNormalizer()

        self.query_preprocessor = QueryPreprocessor()

        self.query_analyzer = QueryAnalyzer(generator)

        self.retriever = RAGRetriever(
            store=self.store,
        )

        self.compressor = RAGCompressor()

        # ---------------------------------------------------------------------
        # Query Processing
        # ---------------------------------------------------------------------
