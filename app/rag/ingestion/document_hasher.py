"""
Document hashing utilities.

Responsibilities
----------------
- Generate a deterministic hash for a document.
- Detect document changes.
- Support incremental indexing.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class DocumentHasher:
    """
    Generate SHA-256 hashes for documents.

    Hashes are used to determine whether a document has
    changed since it was last indexed.
    """

    @staticmethod
    def hash_file(
        path: Path,
    ) -> str:
        """
        Compute the SHA-256 hash of a file.

        Parameters
        ----------
        path
            Path to the document.

        Returns
        -------
        str
            Hexadecimal SHA-256 digest.
        """

        _BUFFER_SIZE = 8192

        sha256 = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(_BUFFER_SIZE), b""):
                sha256.update(chunk)

        return sha256.hexdigest()