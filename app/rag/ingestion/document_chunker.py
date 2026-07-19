"""
Document chunker.

Responsibilities
----------------
- Split documents into semantic chunks.
- Preserve document metadata.
- Produce chunks ready for embedding.

The chunker intentionally performs NO:

- embedding
- vector storage
- retrieval
- LLM calls

Pipeline
--------

Documents
    │
    ▼
DocumentChunker
    │
    ▼
Chunks
"""

from __future__ import annotations

from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.rag_schemas import Chunk, Document


class DocumentChunker:
    """
    Split documents into semantic chunks.

    Uses RecursiveCharacterTextSplitter, which is the current
    standard approach for Markdown-based RAG systems.

    Splitting priority:

    1. Paragraphs
    2. Newlines
    3. Sentences
    4. Words
    5. Characters
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    async def chunk(
        self,
        documents: list[Document],
    ) -> list[Chunk]:
        """
        Split every document into chunks.
        """

        chunks: list[Chunk] = []

        for document in documents:
            chunks.extend(
                await self.chunk_document(document)
            )

        return chunks

    async def chunk_document(
        self,
        document: Document,
    ) -> list[Chunk]:
        """
        Split a single document.
        """

        if not document.content:
            return []

        texts = self._splitter.split_text(
            document.content,
        )

        chunks: list[Chunk] = []

        for index, text in enumerate(texts):
            chunks.append(
                Chunk(
                    id=str(uuid4()),
                    document_id=document.id,
                    source=document.source,
                    index=index,
                    content=text,
                )
            )

        return chunks