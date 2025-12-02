"""
FastAPI application entry point for Convey Backend.
Property Document Summarizer - AI-powered document analysis.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import summarize, auth, projects, documents, summaries
from app.config import settings
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for database connections"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


def is_serverless() -> bool:
    """Detect if running in serverless environment"""
    return any([
        os.getenv("VERCEL"),
        os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
        os.getenv("FUNCTIONS_EXTENSION_VERSION"),  # Azure
    ])


# Create FastAPI application with conditional lifespan
# Vercel handles ASGI natively - no Mangum wrapper needed!
app = FastAPI(
    title="Property Document Summarizer API",
    description="Analyze property documents and generate structured reports using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan if not is_serverless() else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    projects.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    summaries.router,
    prefix="/api/v1",
)

app.include_router(
    summarize.router,
    prefix="/api/v1",
    tags=["summarization"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Property Document Summarizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
