"""
Query normalization.

Responsibilities
----------------
Normalize user queries into a consistent representation without changing
their semantic meaning.

Normalization includes:

- Unicode normalization
- Whitespace normalization
- Line ending normalization
- Quote normalization
- Dash normalization
- Ellipsis normalization
- Removal of zero-width characters
- Removal of control characters

The normalizer intentionally performs NO:

- query rewriting
- synonym expansion
- spelling correction
- abbreviation expansion
- keyword extraction
- intent classification
"""

from __future__ import annotations

import re
import unicodedata


class QueryNormalizer:
    """
    Normalize user queries before retrieval.
    """

    _WHITESPACE_PATTERN = re.compile(r"\s+")

    _ZERO_WIDTH_PATTERN = re.compile(
        r"[\u200B\u200C\u200D\u2060\uFEFF]"
    )

    _CONTROL_PATTERN = re.compile(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
    )

    _QUOTE_TRANSLATION = str.maketrans(
        {
            "“": '"',
            "”": '"',
            "„": '"',
            "‟": '"',
            "‘": "'",
            "’": "'",
            "‚": "'",
            "‛": "'",
        }
    )

    _DASH_TRANSLATION = str.maketrans(
        {
            "–": "-",
            "—": "-",
            "―": "-",
        }
    )

    _ELLIPSIS_TRANSLATION = str.maketrans(
        {
            "…": "...",
        }
    )

    async def normalize(
        self,
        query: str,
    ) -> str:
        """
        Normalize a user query.

        Parameters
        ----------
        query
            Raw user query.

        Returns
        -------
        str
            Normalized query.
        """

        # Normalize Unicode representation.
        query = unicodedata.normalize(
            "NFKC",
            query,
        )

        # Normalize line endings.
        query = query.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        )

        # Remove zero-width characters.
        query = self._ZERO_WIDTH_PATTERN.sub(
            "",
            query,
        )

        # Remove ASCII control characters while preserving newlines.
        query = self._CONTROL_PATTERN.sub(
            "",
            query,
        )

        # Normalize quotation marks.
        query = query.translate(
            self._QUOTE_TRANSLATION,
        )

        # Normalize dash characters.
        query = query.translate(
            self._DASH_TRANSLATION,
        )

        # Normalize ellipsis.
        query = query.translate(
            self._ELLIPSIS_TRANSLATION,
        )

        # Collapse all whitespace.
        query = self._WHITESPACE_PATTERN.sub(
            " ",
            query,
        )

        return query.strip()