import json
from pathlib import Path

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest, Message
from app.rag.embedding.base_embedder import BaseEmbedder
from app.rag.retrieval.query_analyzer import Classification, QueryAnalysis
from app.rag.retrieval.query_preprocessor import ProcessedQuery
from app.rag.rag_context import RAGContext
from app.rag.rag_schemas import RAGResponse


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
        history: list[Message] | None = None, # Not used yet
    ) -> RAGResponse:
        """
        Answer user query directly after retrieved the context
        """
        # Handle request search for chunks
        retrieved_chunks, rewritten_query = await self.search_context(query=query)

        # Nothing relevant was found.
        if not retrieved_chunks:
            return RAGResponse(
                answer=(
                    "I couldn't find enough information in my "
                    "knowledge base to answer that question."
                ),
            )
        
        # Build the system message with retrieval data
        generator_messages = self._context.prompt_builder.build(
            query=rewritten_query,
            chunks=retrieved_chunks,
        )

        response = await self._context.generator.generate(
            GenerationRequest(
                messages=generator_messages,
                tool_definitions=[]
            )
        )

        response_obj = json.loads(response.response)
        return RAGResponse(
            answer=response_obj["answer"],
            sources=response_obj["sources"],
        )
    

    async def search_context(
        self,
        query: str,
    ):
        """
        RAG pipeline - retrieve chunks
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

        # Redict or completely refuse the question gentally
        if query_analysis.classification != Classification.FITNESS:
            return RAGResponse(
                answer=query_analysis.response,
            )
        
        rewritten_query = query_analysis.rewritten_query
        # Convert the rewritten query into an embedding.
        embedding = await self._context.embedder.embed_query(
            rewritten_query,
        )

        # Retrieve the most relevant chunks from the vector store.
        retrieved_chunks = await self._context.retriever.retrieve(
            embedding=embedding,
            top_k=30,
        )

        # Remove duplicates and reduce the context size.
        retrieved_chunks = await self._context.compressor.compress(
            retrieved_chunks,
        )

        return retrieved_chunks, rewritten_query
