"""Async HTTP client helpers for talking to the QA Chatbot API."""

import os
from typing import Any

import httpx


def _base_url() -> str:
    return os.getenv("QA_API_BASE", "http://localhost:8000").rstrip("/")


async def _post(
    path: str,
    json: dict[str, Any],
    *,
    base_url: str | None = None,
) -> dict[str, Any]:
    """POST JSON with a short lived AsyncClient bound to the current event loop.

    Streamlit re-runs can create new loops; a fresh client avoids cross-loop errors.
    """
    async with httpx.AsyncClient(
        base_url=(base_url or _base_url()),
        timeout=httpx.Timeout(15.0, read=60.0),
    ) as client:
        resp = await client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()


async def ingest_urls(
    urls: list[str], *, base_url: str | None = None
) -> dict[str, Any]:
    """POST /ingest with a list of URLs and return parsed JSON."""

    data = await _post("/ingest", json={"urls": urls}, base_url=base_url)
    # Normalize keys expected by UI
    data.setdefault("count", len(urls))
    data.setdefault("results", [])
    data.setdefault("request_id", None)
    return data


async def ask_question(
    question: str,
    *,
    top_k: int = 4,
    max_context: int = 1800,
    base_url: str | None = None,
) -> dict[str, Any]:
    """POST /qa with a question and return parsed JSON."""

    payload = {"question": question, "top_k": top_k, "max_context": max_context}
    data = await _post("/qa", json=payload, base_url=base_url)
    # Normalize keys expected by UI
    data.setdefault("query", question)
    data.setdefault("answer", "")
    data.setdefault("context", "")
    data.setdefault("sources", [])
    return data
