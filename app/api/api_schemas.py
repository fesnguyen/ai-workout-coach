from pydantic import BaseModel, Field

from app.workout_analysis.workout_schemas import ExerciseEntry, ExerciseHistory

class ChatRequest(BaseModel):
    previous_response_id: str | None = None
    message: str
    history: ExerciseHistory | None = None

class ChatResponse(BaseModel):
    previous_response_id: str
    answer: str

class RAGSearchRequest(BaseModel):
    query: str

class WorkoutAnalyzeRequest(BaseModel):
    query: str
    history: list[ExerciseEntry]