"""
Abstract interfaces (ABCs) for the core RAG MVP.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from api.core.models import IngestionResult, SearchItem, SourceItem


class IngestionService(ABC):
    """Abstract interface for ingestion use cases (URL and PDF)."""

    @abstractmethod
    async def ingest_url(self, url: str) -> IngestionResult:
        """Ingest a public URL (web page) and index chunks into the vector store."""
        raise NotImplementedError

    @abstractmethod
    async def ingest_pdf_bytes(
        self, content: bytes, filename: str | None = None
    ) -> IngestionResult:
        """Ingest a PDF from bytes and index chunks into the vector store."""
        raise NotImplementedError


class RetrievalService(ABC):
    """Abstract interface for semantic retrieval-only use cases."""

    @abstractmethod
    async def search(self, query: str, k: int = 5) -> Sequence[SearchItem]:
        """Return top-k chunks with scores and metadata for a query."""
        raise NotImplementedError


class ChatService(ABC):
    """Abstract interface for conversational RAG operations."""

    @abstractmethod
    async def chat(self, session_id: str, question: str) -> tuple[str, Sequence[SourceItem]]:
        """Return assistant answer and retrieved source snippets for citations."""
        raise NotImplementedError
