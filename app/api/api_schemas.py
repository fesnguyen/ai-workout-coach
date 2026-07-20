from pydantic import BaseModel, Field

from app.workout_analysis.workout_schemas import ExerciseEntry, ExerciseHistory

class ChatRequest(BaseModel):
    message: str

class WorkoutAnalyzeRequest(BaseModel):
    query: str
    history: list[ExerciseEntry]