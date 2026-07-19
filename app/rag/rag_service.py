from pathlib import Path

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import Message
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.ingestion.document_chunker import DocumentChunker
from app.rag.ingestion.document_loader import DocumentLoader
from app.rag.retrieval.rag_compressor import RAGCompressor
from app.rag.embedding.openai_embedder import OpenAIEmbedder
from app.rag.retrieval.rag_guardrail import GuardrailAction, RAGGuardrail
from app.rag.rag_context import RAGContext
from app.rag.retrieval.rag_query_rewriter import RAGQueryRewriter
from app.rag.retrieval.rag_retriever import RAGRetriever
from app.rag.rag_schemas import RAGResponse
from app.rag.retrieval.rag_store import RAGStore


class RAGService:
    """
    Retrieval-Augmented Generation service.

    Responsibilities:
    - Build the vector index from the knowledge base.
    - Retrieve relevant documents.
    - Generate grounded responses.
    - Apply query rewriting and guardrails.
    """

    def __init__(
        self,
        generator: BaseGenerator,
        embedder: BaseEmbedder,
        knowledge_path: Path,
        database_path: Path,
    ) -> None:

        self._context = RAGContext(
            generator=generator,
            embedder=embedder,
            knowledge_path=knowledge_path,
            database_path=database_path,
        )

    async def initialize(self) -> None:
        """
        Persistent embeddings into chromadb
        """
        documents = await self._context.loader.load()

        chunks = await self._context.chunker.chunk(documents)

        embeddings = await self._context.embedder.embed_documents(
            [chunk.content for chunk in chunks]
        )

        await self._context.store.index(
            chunks,
            embeddings,
        )

    async def search(
        self,
        query: str,
        history: list[Message] | None = None,
    ) -> RAGResponse:

        decision = await self._context.guardrail.validate(query)

        query = await self._context.query_rewriter.rewrite(
            query,
            history,
        )

        embedding = await self._context.embedder.embed_query(query)

        chunks = await self._context.retriever.retrieve(
            embedding,
            top_k=30,
        )

        chunks = await self._context.compressor.compress(chunks)

        return await self._generate(
            query=query,
            chunks=chunks,
        )