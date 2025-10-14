"""
Shared DTO (data transfer objects) models for responses and internal data passing.
"""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, Field


class IngestionResult(BaseModel):
    """Minimal response after ingestion completes."""

    chunks: int = Field(..., description="Number of text chunks created")
    vectors: int = Field(..., description="Number of embeddings added to the vector store")


class SearchItem(BaseModel):
    """One ranked result from semantic search/retrieval."""

    content: str
    metadata: Mapping[str, Any] = Field(default_factory=dict)
    score: float | None = Field(default=None, description="Similarity/relevance score if available")


class SourceItem(BaseModel):
    """A source document chunk for RAG citations."""

    content: str
    metadata: Mapping[str, Any] = Field(default_factory=dict)
