from typing import Optional, Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger


def create_app(
    *,
    cors_origins: Optional[Sequence[str]] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    - cors_origins: list of allowed origins for CORS (for the UI)
    """
    # Create FastAPI app
    app = FastAPI(
        title="QA Chatbot API",
        description="API for a Question-Answering Chatbot",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Simple CORS defaults
    if cors_origins is None:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("QA Chatbot API initialized...")
    return app


# Create the FastAPI app instance
app = create_app()
