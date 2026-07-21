from pydantic import BaseModel, Field

from app.workout_analysis.workout_schemas import ExerciseEntry, ExerciseHistory

class ChatRequest(BaseModel):
    previous_response_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    previous_response_id: str
    answer: str

class RAGSearchRequest(BaseModel):
    query: str

class UserProfile(BaseModel):
    name: str
    profile: str | None = None
    workouts: list[ExerciseEntry]

class WorkoutAnalyzeRequest(BaseModel):
    query: str
    user_profile: UserProfile

class WorkoutAnalyzeResponse(BaseModel):
    response: str
    user_id: str | None = None

