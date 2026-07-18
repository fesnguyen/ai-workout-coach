from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and clean up application resources.
    """
    # Startup
    # e.g. initialize database, vector store, AI models

    yield

    # Shutdown
    # e.g. close database connections, release resources


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
    return {"status": "Hello"}