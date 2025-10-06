from fastapi import APIRouter, HTTPException
from loguru import logger

from api.routes.models import QARequest, QAResponse
from api.services.qa_service import QAService

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", response_model=QAResponse)
async def ask_question(payload: QARequest) -> QAResponse:
    """Answer a question using retrieved context from the vector store."""
    try:
        logger.info(f"QA query received: {payload.question}")
        service = QAService(
            top_k=payload.top_k or 4, max_context_chars=payload.max_context or 1800
        )
        result = await service.answer_question(payload.question)
        return QAResponse(**result)
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"QA failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to answer question")
