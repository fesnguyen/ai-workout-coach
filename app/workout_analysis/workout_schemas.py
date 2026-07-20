from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


WeightUnit = Literal["kg", "lb"]

ExerciseName = str

WorkoutQuery = str

ExerciseHistory = list["ExerciseEntry"]

ExerciseIndex = dict[
    ExerciseName,
    list["ExerciseEntry"],
]


class ExerciseSet(BaseModel):
    """
    A single performed set.
    """

    reps: int = Field(gt=0)
    weight: float = Field(ge=0)
    unit: WeightUnit


class ExerciseEntry(BaseModel):
    """
    A single exercise performed during a workout session.
    """

    date: date
    exercise: ExerciseName = Field(strip_whitespace=True, min_length=1)
    sets: list[ExerciseSet] = Field(min_length=1)


class AnalysisResult(BaseModel):
    """
    Aggregated output produced by the workout analysis pipeline.
    """
    metrics: dict[str, Any] = Field(default_factory=dict)


class MetricResult(BaseModel):
    """
    Output of a single analysis metric.
    """

    model_config = ConfigDict(frozen=True)

    name: str

    value: Any


class CompressionContext(BaseModel):
    analysis: AnalysisResult
    query: WorkoutQuery