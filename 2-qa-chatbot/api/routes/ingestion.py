import uuid
from time import monotonic

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.routes.models import IngestRequest, IngestResponse
from api.services.run_ingestion_pipeline import run_ingestion_pipeline

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("", response_model=IngestResponse)
async def ingest_urls(payload: IngestRequest) -> IngestResponse:
    """Trigger the ingestion pipeline for the provided URLs."""
    try:
        request_id = uuid.uuid4().hex
        started = monotonic()
        urls = [str(u) for u in payload.urls]

        logger.info(f"[{request_id}] Starting ingestion for {len(urls)} URL(s)")

        # TODO: Basic per-URL feedback scaffold (expand later if pipeline exposes details)
        results: list[dict] = []
        try:
            run_ingestion_pipeline(urls)
            for u in urls:
                results.append({"url": u, "status": "ok", "message": "ingested"})
            elapsed = monotonic() - started
            logger.info(f"[{request_id}] Ingestion completed in {elapsed:.2f}s")
            return IngestResponse(
                count=len(urls),
                detail=f"Ingestion completed in {elapsed:.2f}s",
                request_id=request_id,
                results=results,
            )
        except Exception as ex:
            logger.exception(f"[{request_id}] Ingestion failed: {ex}")
            for u in urls:
                results.append({"url": u, "status": "error", "message": str(ex)})
            raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to ingest URLs: {ex}")
