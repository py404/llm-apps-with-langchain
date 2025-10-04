from collections.abc import Iterable

from loguru import logger

from .document_ingestion import DocumentIngestionService


def run_ingestion_pipeline(urls: Iterable[str]) -> None:
    """Instantiate the document ingestion service and run it end-to-end."""

    try:
        service = DocumentIngestionService(urls=list(urls))
        service.run_pipeline()
    except Exception:
        logger.exception("Failed to run ingestion service pipeline")
        raise
