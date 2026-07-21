"""
Schemas used by the Retrieval-Augmented Generation (RAG) pipeline.
"""

from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    A source document loaded from the knowledge base.
    """

    id: str

    title: str

    source: Path

    content: str


class Chunk(BaseModel):
    """
    A semantic chunk generated from a document.
    """

    id: str

    document_id: str

    source: Path

    index: int

    content: str

    score: float | None = None


class RAGResponse(BaseModel):
    """
    Final grounded response returned by the RAG pipeline.
    """

    answer: str

    sources: list[str] = Field(default_factory=list)


class IndexedDocument(BaseModel):
    """
    Use for Incremental Indexing
    """
    source: Path
    hash: str


class IndexPlan(BaseModel):
    added: list[IndexedDocument]
    modified: list[IndexedDocument]
    deleted: list[Path]
    unchanged: list[IndexedDocument]