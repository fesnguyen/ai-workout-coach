from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SearchCase:
    """
    A single evaluation case.
    """

    id: str
    query: str
    expected: dict[str, Any]


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