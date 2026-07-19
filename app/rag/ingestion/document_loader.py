"""
Document loader.

Responsibilities
----------------
- Discover supported documents.
- Read document contents.
- Preserve metadata.
- Return standardized Document objects.

The loader intentionally performs NO:

- chunking
- embedding
- retrieval
- preprocessing

Those belong to later stages of the RAG pipeline.

Pipeline
--------

Knowledge Folder
        │
        ▼
DocumentLoader
        │
        ▼
List[Document]
"""

from __future__ import annotations

from pathlib import Path

from app.rag.rag_schemas import Document


class DocumentLoader:
    """
    Load knowledge documents from disk.

    Supported formats
    -----------------

    - Markdown (.md)

    Future extensions

    - PDF
    - HTML
    - DOCX
    """

    SUPPORTED_EXTENSIONS = {
        ".md",
    }

    def __init__(
        self,
        knowledge_path: Path,
    ) -> None:
        self._knowledge_path = knowledge_path

    async def load(self) -> list[Document]:
        """
        Load every supported document.

        Returns
        -------
        list[Document]
            Documents ready for chunking.
        """

        if not self._knowledge_path.exists():
            raise FileNotFoundError(
                f"Knowledge directory does not exist: "
                f"{self._knowledge_path}"
            )

        documents: list[Document] = []

        for path in sorted(self._knowledge_path.rglob("*")):

            if not path.is_file():
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            documents.append(
                await self._load_markdown(path)
            )

        return documents

    async def _load_markdown(
        self,
        path: Path,
    ) -> Document:
        """
        Load a markdown file.

        No parsing is performed here.

        Markdown syntax is intentionally preserved because
        modern embedding models generally perform well on
        raw Markdown.
        """

        content = path.read_text(
            encoding="utf-8",
        )

        return Document(
            id=self._build_document_id(path),
            title=path.stem,
            source=str(path),
            content=content,
        )

    @staticmethod
    def _build_document_id(
        path: Path,
    ) -> str:
        """
        Build a deterministic document id.

        Example
        -------

        knowledge/training/progressive_overload.md

        →

        training/progressive_overload
        """

        return path.with_suffix("").as_posix()