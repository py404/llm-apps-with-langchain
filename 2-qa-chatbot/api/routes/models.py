from typing import Optional

from pydantic import BaseModel, HttpUrl


class IngestRequest(BaseModel):
    urls: list[HttpUrl]


class IngestResponse(BaseModel):
    count: int
    detail: str
    request_id: Optional[str] = None
    results: Optional[list[dict]] = None


class QARequest(BaseModel):
    question: str
    top_k: Optional[int] = 4
    max_context: Optional[int] = 1800


class QAResponse(BaseModel):
    query: str
    answer: str
    context: str
    sources: list[Optional[str]]
