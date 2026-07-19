"""
Schemas used by the Retrieval-Augmented Generation (RAG) pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    A source document loaded from the knowledge base.
    """

    id: str

    title: str

    source: str

    content: str


class Chunk(BaseModel):
    """
    A semantic chunk generated from a document.
    """

    id: str

    document_id: str

    source: str

    index: int

    content: str



class RetrievedChunk(BaseModel):
    """
    A chunk returned by the retriever.
    """

    chunk: Chunk

    score: float


class Source(BaseModel):
    """
    Source attribution included in the final response.
    """

    document: str

    chunk_index: int


class RAGResponse(BaseModel):
    """
    Final grounded response returned by the RAG pipeline.
    """

    answer: str

    sources: list[Source] = Field(default_factory=list)