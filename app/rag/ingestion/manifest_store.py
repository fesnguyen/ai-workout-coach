"""
Manifest store for incremental indexing.

Responsibilities
----------------
- Persist indexed document metadata.
- Detect whether a document has changed.
- Support incremental indexing.

The manifest intentionally stores metadata only.

Document chunks and embeddings belong to ChromaDB.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class ManifestStore:
    """
    Stores document hashes used for incremental indexing.
    """

    def __init__(
        self,
        database_path: Path,
    ) -> None:
        self._database = database_path / "manifest.db"

        self._initialize()

    def _initialize(self) -> None:
        self._database.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with sqlite3.connect(self._database) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    source TEXT PRIMARY KEY,
                    hash TEXT NOT NULL,
                    indexed_at TEXT NOT NULL
                )
                """
            )

    def get_hash(
        self,
        source: str,
    ) -> str | None:
        """
        Return the stored hash for a document.
        """

        with sqlite3.connect(self._database) as connection:
            cursor = connection.execute(
                """
                SELECT hash
                FROM documents
                WHERE source = ?
                """,
                (source,),
            )

            row = cursor.fetchone()

        return row[0] if row else None
    

    def list_hashes(self) -> dict[Path, str]:
        """
        Return all indexed document hashes.
        """

        with sqlite3.connect(self._database) as connection:
            cursor = connection.execute(
                """
                SELECT source, hash
                FROM documents
                """
            )

            return {
                Path(source): hash_value
                for source, hash_value in cursor.fetchall()
            }


    def list_sources(self) -> set[str]:
        """
        Return all indexed document sources.
        """

        with sqlite3.connect(self._database) as connection:
            cursor = connection.execute(
                """
                SELECT source
                FROM documents
                """
            )

            return {
                Path(row[0])
                for row in cursor.fetchall()
            }

    def upsert(
        self,
        *,
        source: str,
        hash_value: str,
    ) -> None:
        """
        Insert or update a document hash.
        """

        with sqlite3.connect(self._database) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    source,
                    hash,
                    indexed_at
                )
                VALUES (?, ?, ?)
                ON CONFLICT(source)
                DO UPDATE SET
                    hash = excluded.hash,
                    indexed_at = excluded.indexed_at
                """,
                (
                    source,
                    hash_value,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()

    def delete(
        self,
        source: str,
    ) -> None:
        """
        Remove a document from the manifest.
        """

        with sqlite3.connect(self._database) as connection:
            connection.execute(
                """
                DELETE FROM documents
                WHERE source = ?
                """,
                (source,),
            )
            connection.commit()