from typing import Optional

from pydantic import BaseModel, HttpUrl


class IngestRequest(BaseModel):
    urls: list[HttpUrl]


class IngestResponse(BaseModel):
    count: int
    detail: str
    request_id: Optional[str] = None
    results: Optional[list[dict]] = None
