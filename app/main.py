from contextlib import asynccontextmanager
import json

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from openai import BadRequestError

from app.api.api_schemas import ChatRequest, ChatResponse, RAGSearchRequest, UserProfile, WorkoutAnalyzeRequest, WorkoutAnalyzeResponse
from app.api.exceptions import InvalidPreviousResponseError
from app.application_container import ApplicationContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and clean up application resources.
    """
    container = ApplicationContainer()

    await container.initialize()

    app.state.container = container

    try:
        yield
    finally:
        await container.shutdown()


app = FastAPI(
    title="AI Workout Coach API",
    description="Backend service for AI-powered workout coaching and fitness knowledge retrieval.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check api endpoint"""
    return {"status": "Hello"}



@app.post("/chat", tags=["Chat"])
async def chat(
    body: ChatRequest,
    request: Request,
)-> ChatResponse:
    """
    Chat with the agent
    """

    agent = request.app.state.container.agent

    try:
        response = await agent.chat(body)
        return response

    except InvalidPreviousResponseError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )


@app.post("/rag/search", tags=["Chat"])
async def rag_request(
    body: RAGSearchRequest,
    request: Request,
):
    """
    Chat with the rag
    """

    rag_service = request.app.state.container.rag_service

    response = await rag_service.search(
        body.query,
    )

    return {
        "response": response,
    }


@app.post("/workout/analyze", tags=["Chat"])
async def workout_analyze_request(
    file: UploadFile = File(...),
    query: str = Form(...),
    request: Request = None,
):
    """
    Chat with the rag
    """

    workout_service = request.app.state.container.workout_service

    payload: UserProfile = json.loads(await file.read())

    body = WorkoutAnalyzeRequest(
        query=query,
        user_profile=payload,
    )

    response: WorkoutAnalyzeResponse = await workout_service.analyze(body)

    return response