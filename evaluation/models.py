from dataclasses import dataclass
from typing import Any

from app.rag.rag_schemas import RAGResponse


@dataclass(slots=True)
class ExpectedAnswer:
    answer: str
    facts: list[str]

@dataclass(slots=True)
class SearchCase:
    """
    A single evaluation case.
    """

    id: str
    query: str
    expected: ExpectedAnswer


@dataclass(slots=True)
class EvaluationContext:
    """
    Shared context passed to every evaluation judge.
    """

    response: RAGResponse


@dataclass(slots=True)
class JudgeResult:
    """
    Result returned by a single evaluation judge.
    """

    passed: bool
    score: float
    reason: str


@dataclass(slots=True)
class EvaluationResult:
    """
    Result of evaluating one case with one judge.
    """

    category: str
    case_id: str
    question: str

    judge: str

    passed: bool
    score: float
    reason: str

    answer: str