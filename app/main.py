from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Request

from time import perf_counter

from app.api.api_schemas import ChatRequest
from app.application_container import ApplicationContainer
from app.llm.llm_schemas import (
    GenerationRequest,
    Message,
)

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
):
    """
    Chat with the agent
    """

    agent = request.app.state.container.agent

    response = await agent.invoke(
        messages=[
            Message(
                role="user",
                content=body.message,
            )
        ]
    )

    return {
        "response": response,
    }