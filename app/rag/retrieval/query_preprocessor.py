"""
Query preprocessing.

Responsibilities
----------------
Prepare a normalized query for retrieval using deterministic,
domain-specific techniques.

Preprocessing may enrich the query but never changes the user's intent.

Pipeline
--------

Normalized Query
        │
        ▼
Abbreviation Expansion
        │
        ▼
Synonym Expansion
        │
        ▼
Exercise Alias Expansion
        │
        ▼
Unit Normalization
        │
        ▼
Keyword Extraction
        │
        ▼
Metadata Hint Extraction
        │
        ▼
Processed Query

The preprocessor intentionally performs NO:

- LLM inference
- query rewriting
- intent classification
- guardrail
- retrieval
- embedding
- answer generation
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class ProcessedQuery:
    """
    Result of deterministic query preprocessing.
    """

    original: str

    expanded: str

    keywords: list[str]

    metadata_filters: dict[str, str]


class QueryPreprocessor:
    """
    Deterministically prepare a query for retrieval.
    """

    _ABBREVIATIONS = {
        "bp": "bench press",
        "dl": "deadlift",
        "ohp": "overhead press",
        "rdl": "romanian deadlift",
        "rom": "range of motion",
        "hiit": "high intensity interval training",
        "1rm": "one repetition maximum",
    }

    _SYNONYMS = {
        "pec": "chest",
        "pecs": "chest",
        "quad": "quadriceps",
        "quads": "quadriceps",
        "hamstring": "hamstrings",
        "hammy": "hamstrings",
        "abs": "abdominals",
        "core": "abdominals",
        "glute": "glutes",
        "glutes": "gluteus",
    }

    # Maps common colloquial names or variations to formal exercise names
    _EXERCISE_ALIASES = {
        "flat bench": "bench press",
        "conventional deadlift": "deadlift",
        "military press": "overhead press",
        "squats": "squat",
    }

    # Maps unit variations to standard expressions (e.g., handling weight configurations)
    _UNIT_MAPPINGS = {
        "lbs": "pounds",
        "lb": "pounds",
        "kgs": "kilograms",
        "kg": "kilograms",
    }

    _STOP_WORDS = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "of",
        "to",
        "for",
        "with",
        "on",
        "at",
        "in",
        "and",
        "or",
        "i",
        "me",
        "my",
        "should",
        "can",
        "could",
        "would",
        "do",
    }

    _TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")

    async def process(
        self,
        query: str,
    ) -> ProcessedQuery:
        """
        Transform a raw user query into a normalized, retrieval-friendly representation.
        """
        # Phase 1: Text Expansion & Normalization
        expanded = self._expand_abbreviations(query)
        expanded = self._expand_synonyms(expanded)
        expanded = self._expand_exercise_aliases(expanded)
        expanded = self._normalize_units(expanded)

        # Phase 2: Tokenization & Feature Extraction
        keywords = self._extract_keywords(expanded)
        filters = self._extract_metadata_filters(
            keywords,
        )

        return ProcessedQuery(
            original=query,
            expanded=expanded,
            keywords=keywords,
            metadata_filters=filters,
        )

    def _expand_abbreviations(
        self,
        query: str,
    ) -> str:
        """
        Replaces known fitness abbreviations with their full text expressions.
        Uses case-insensitive, whole-word matching.
        """
        for abbreviation, expansion in self._ABBREVIATIONS.items():
            query = re.sub(
                rf"\b{re.escape(abbreviation)}\b",
                expansion,
                query,
                flags=re.IGNORECASE,
            )

        return query

    def _expand_synonyms(
        self,
        query: str,
    ) -> str:
        """
        Standardizes anatomical terms and common muscle group descriptions
        to unified targets.
        """
        for synonym, canonical in self._SYNONYMS.items():
            query = re.sub(
                rf"\b{re.escape(synonym)}\b",
                canonical,
                query,
                flags=re.IGNORECASE,
            )

        return query

    def _expand_exercise_aliases(
        self,
        query: str,
    ) -> str:
        """
        Maps conversational or alternative movement titles to their structured
        exercise names.
        """
        for alias, canonical in self._EXERCISE_ALIASES.items():
            query = re.sub(
                rf"\b{re.escape(alias)}\b",
                canonical,
                query,
                flags=re.IGNORECASE,
            )
        return query

    def _normalize_units(
        self,
        query: str,
    ) -> str:
        """
        Ensures metric and imperial measurement terms match a single, 
        predictable keyword pattern.
        """
        for unit, standardized in self._UNIT_MAPPINGS.items():
            query = re.sub(
                rf"\b{re.escape(unit)}\b",
                standardized,
                query,
                flags=re.IGNORECASE,
            )
        return query

    def _extract_keywords(
        self,
        query: str,
    ) -> list[str]:
        """
        Tokenizes the normalized text stream and filters out structural language / stop words
        to isolate core conceptual terms.
        """
        keywords = []

        for token in self._TOKEN_PATTERN.findall(
            query.lower(),
        ):
            if token not in self._STOP_WORDS:
                keywords.append(token)

        return keywords

    def _extract_metadata_filters(
        self,
        keywords: list[str],
    ) -> dict[str, str]:
        """
        Inspects the isolated keywords to generate high-confidence metadata search hints
        for downstream engines.
        """
        filters: dict[str, str] = {}

        if "nutrition" in keywords:
            filters["category"] = "nutrition"

        if "protein" in keywords:
            filters["topic"] = "protein"

        if "deadlift" in keywords:
            filters["exercise"] = "deadlift"

        if "bench" in keywords:
            filters["exercise"] = "bench_press"

        return filters