from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, Request

from time import perf_counter

from app.application_container import ApplicationContainer
from app.llm.schemas import (
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

# Defind system routes
router = APIRouter(prefix="/system", tags=["System"])

# Include system routes
app.include_router(router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check api endpoint"""
    return {"status": "Hello"}


@router.get("/model/check")
async def model_check(request: Request):
    """
    Verify the configured LLM is reachable and report basic diagnostics.
    """
    container = request.app.state.container
    generator = container.generator

    start = perf_counter()

    try:
        response = await generator.generate(
            GenerationRequest(
                messages=[
                    Message(
                        role="user",
                        content="Reply with exactly: OK"
                    )
                ]
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"LLM unavailable: {exc}"
        ) from exc

    latency_ms = round((perf_counter() - start) * 1000, 2)

    return {
        "status": "ok",
        "model": getattr(generator, "_model", "unknown"),
        "latency_ms": latency_ms,
        "response": response.content,
        "usage": {
            "input_tokens": response.usage.input_tokens if response.usage else None,
            "output_tokens": response.usage.output_tokens if response.usage else None,
            "total_tokens": response.usage.total_tokens if response.usage else None,
        },
        "finish_reason": response.finish_reason,
    }