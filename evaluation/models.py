from dataclasses import dataclass
from typing import Any

from app.api.api_schemas import WorkoutAnalyzeRequest
from app.rag.rag_schemas import RAGResponse
from app.workout_analysis.workout_schemas import AnalysisResult


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
class ExpectedWorkoutAnalysis:
    answer: str

    findings: list[str]

    recommendations: list[str]

@dataclass(slots=True)
class WorkoutAnalysisCase:
    id: str

    request: WorkoutAnalyzeRequest

    expected: ExpectedWorkoutAnalysis


@dataclass(slots=True)
class EvaluationContext:
    """
    Shared context passed to every evaluation judge.
    """

    # RAG evaluation
    response: RAGResponse | None = None

    # Workout history evaluation
    analysis: AnalysisResult | None = None
    generated_response: str | None = None


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