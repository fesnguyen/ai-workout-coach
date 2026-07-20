"""
Query analysis.

Responsibilities
----------------
Analyze a preprocessed query using an LLM.

The analyzer understands the user's intent and produces structured
information for downstream retrieval.

It is responsible for:

- Guardrail classification
- Query rewriting
- Intent classification
- Entity extraction
- Metadata filter extraction
- Clarification detection

Pipeline
--------

Processed Query
        │
        ▼
LLM
        │
        ▼
QueryAnalysis

The analyzer intentionally performs NO:

- retrieval
- embedding
- reranking
- context compression
- answer generation
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import (
    GenerationRequest,
    Message,
)
from app.rag.retrieval.query_preprocessor import (
    ProcessedQuery,
)


class Classification(str, Enum):
    """
    Request Classification.
    """

    FITNESS = "fitness"

    OUT_OF_SCOPE = "out_of_scope"

    RESTRICTED = "restricted"


class QueryAnalysis(BaseModel):
    """
    Result of query analysis.
    """

    classification: Classification

    rewritten_query: str | None = None

    response: str | None = None


SYSTEM_PROMPT = """
You are the Query Analyzer for a fitness RAG system.

Your job is to determine how the system should process the user's request.

There are only three possible cases.

1. "fitness"

Don't answer this question, rewrite the query and expand its words.

In this case:

- Rewrite the query to improve retrieval.
- Expand the query with relevant fitness terminology, synonyms, abbreviations and related concepts.
- Preserve the original intent.
- Do NOT answer the question.

Consistent schema with example for "fitness" case:

Question: How many grams of protein should I eat after a workout?

Return:

{
  "classification": "fitness",
  "rewritten_query": "Recommended protein intake after exercise, post-workout protein consumption, optimal grams of protein for muscle recovery and muscle growth,...",
  "response": null
}

2. "out_of_scope"

The request is unrelated to the fitness assistant.

In this case:

- Answer the user directly and concisely.
- Do NOT rewrite the query.
- Do NOT prepare retrieval.

Consistent schema with example for "out_of_scope" case:

Question: What's the weather today?

Return:

{
  "classification": "out_of_scope",
  "rewritten_query": null,
  "response": "I can't provide live weather information. Please check a weather service for the latest forecast."
}

3. "restricted"

The request is unsafe or asks for prohibited medical advice that requires a qualified healthcare professional.

Examples include:

- diagnosis
- treatment recommendations
- prescription advice
- interpreting medical symptoms
- dangerous requests
- illegal activities
- eating disorder encouragement
- any unsafe request

In this case:

- Politely refuse or redirect the user.
- Do NOT rewrite the query.
- Do NOT prepare retrieval.

Consistent schema with example for "restricted" case:

Question: Who won the FIFA World Cup?

Return:

{
  "classification": "restricted",
  "rewritten_query": null,
  "response": "I can't diagnose injuries or provide medical advice. Please consult a qualified healthcare professional for an accurate evaluation."
}

Rules

- Never answer FITNESS questions.
- Only FITNESS queries should continue to retrieval.
- Only rewrite FITNESS queries.
- Be nice and graceful with any request.
- Return valid JSON only.
"""


class QueryAnalyzer:
    """
    Analyze a query before retrieval.
    """

    def __init__(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    async def analyze(
        self,
        query: ProcessedQuery,
        history: list[Message] = [],
    ) -> QueryAnalysis:
        """
        Analyze a preprocessed query.

        Parameters
        ----------
        query
            Preprocessed query.

        history
            Recent conversation history.

        Returns
        -------
        QueryAnalysis
        """

        messages = [
            Message(
                role="system",
                content=SYSTEM_PROMPT,
            ),
            *history,
            Message(
                role="user",
                content=(
                    f"Original query:\n"
                    f"{query.original}\n\n"
                    f"Expanded query:\n"
                    f"{query.expanded}\n\n"
                    f"Keywords:\n"
                    f"{query.keywords}\n\n"
                    f"Metadata hints:\n"
                    f"{query.metadata_filters}"
                ),
            ),
        ]

        response = await self._generator.generate(
            GenerationRequest(
                messages=messages,
            )
        )

        return QueryAnalysis.model_validate_json(
            response.response,
        )