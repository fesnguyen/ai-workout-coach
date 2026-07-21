import json
from pathlib import Path

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest, Message
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.retrieval.query_analyzer import Classification, QueryAnalysis
from app.rag.retrieval.query_preprocessor import ProcessedQuery
from app.rag.rag_context import RAGContext
from app.rag.rag_schemas import Chunk, RAGResponse


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
        await self._context.ingestion.sync()

    async def search(
        self,
        query: str,
    ) -> RAGResponse:
        """
        Answer user query directly after retrieved the context
        """
        query_analysis = await self._analyze_query(query=query)

        # Redict or completely refuse the question gentally
        if query_analysis.classification != Classification.FITNESS:
            return RAGResponse(
                answer=query_analysis.response,
            )

        # Handle request search for chunks
        rewritten_query = query_analysis.rewritten_query
        chunks = await self._retrieve_and_compress_chunks(
            rewritten_query
        )

        # Nothing relevant was found.
        if not chunks:
            return RAGResponse(
                answer=(
                    "I couldn't find enough information in my "
                    "knowledge base to answer that question."
                ),
            )
        
        # Build the system message with retrieval data
        generator_messages = self._context.prompt_builder.build(
            query=rewritten_query,
            chunks=chunks,
        )

        # Answer use query
        response = await self._context.generator.generate(
            GenerationRequest(
                messages=generator_messages,
                tool_definitions=[]
            )
        )

        try:
            response_obj = json.loads(response.response)
            return RAGResponse(
                answer=response_obj.get("answer", response.response),
                sources=response_obj.get("sources", []),
            )
        except json.JSONDecodeError:
            return RAGResponse(
                answer=response.response,
                sources=[],
            )

    async def _analyze_query(
        self,
        query: str,
    ):
        """
        Query Guardrail, Classification and Analysis
        """
        # Normalize query
        normalized_query = await self._context.query_normalizer.normalize(query)

        # Expand query into a normalized, retrieval-friendly representation
        preprocessed_query: ProcessedQuery = \
            await self._context.query_preprocessor.process(
                normalized_query
            )

        # Guard rail, classify, rewrite querry
        query_analysis: QueryAnalysis = await self._context.query_analyzer \
            .analyze(preprocessed_query)
        
        return query_analysis


    async def _retrieve_and_compress_chunks(
        self,
        rewritten_query: str,
    ):
        # Convert the rewritten query into an embedding.
        embedding = await self._context.embedder.embed_query(
            rewritten_query,
        )

        # Retrieve the most relevant chunks from the vector store.
        chunks = await self._context.retriever.retrieve(
            embedding=embedding,
            top_k=30,
        )

        # Remove duplicates and reduce the context size.
        chunks = await self._context.compressor.compress(
            chunks,
        )

        return chunks


    async def search_context(
        self,
        query: str,
    ) -> list[Chunk]:
        """
        RAG pipeline - retrieve chunks
        """
        query_analysis = await self._analyze_query(query=query)

        # Return empty query got rejected
        if query_analysis.classification != Classification.FITNESS:
            return []
        
        return await self._retrieve_and_compress_chunks(
            query_analysis.rewritten_query
        )
