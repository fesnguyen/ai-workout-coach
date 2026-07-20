"""
Incremental indexing planner.

Responsibilities
----------------
- Compare the current knowledge base with the manifest.
- Determine which documents should be indexed.
- Detect added, modified, unchanged, and deleted documents.
"""

from __future__ import annotations

from pathlib import Path

from app.rag.ingestion.manifest_store import ManifestStore
from app.rag.rag_schemas import (
    IndexedDocument,
    IndexPlan,
)


class IndexPlanner:
    """
    Plans incremental indexing operations.
    """

    def __init__(
        self,
        manifest: ManifestStore,
    ) -> None:
        self._manifest = manifest

    def plan(
        self,
        documents: list[IndexedDocument],
    ) -> IndexPlan:
        added: list[IndexedDocument] = []
        modified: list[IndexedDocument] = []
        unchanged: list[IndexedDocument] = []

        stored_hashes = self._manifest.list_hashes()

        current_sources: set[str] = set()

        for document in documents:
            current_sources.add(document.source)

            stored_hash = stored_hashes.get(document.source)

            if stored_hash is None:
                added.append(document)

            elif stored_hash != document.hash:
                modified.append(document)

            else:
                unchanged.append(document)

        manifest_sources = self._manifest.list_sources()

        deleted = [
            Path(source)
            for source in manifest_sources - current_sources
        ]

        return IndexPlan(
            added=added,
            modified=modified,
            deleted=deleted,
            unchanged=unchanged,
        )