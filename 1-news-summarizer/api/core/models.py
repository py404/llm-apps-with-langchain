from pydantic import BaseModel, Field, HttpUrl
from typing import List


class ArticleRequest(BaseModel):
    """Pydantic model for article fetcher class."""

    url: HttpUrl = Field(..., description="The URL of the news article to summarize.")


class ArticleContent(BaseModel):
    """Pydantic model for article content returned by ArticleFetcher."""

    title: str = Field(..., description="The title of the news article.")
    text: str = Field(..., description="The full text content of the news article.")


class StructuredSummary(BaseModel):
    """Structured summary returned by the summarizer"""

    tl_dr: str | None = Field(None, description="A one liner TL;DR of the article.")
    bullets: List[str] = Field(..., description="Bulleted summary points.")
    keywords: List[str] | None = Field(None, description="Optional keywords extracted from the article.")


class SummaryResponse(BaseModel):
    """Pydantic model for summary response."""

    summary: str = Field(..., description="The summarized text of the article.")
    structured_summary: StructuredSummary | None = Field(
        None, description="Optional structured summary"
    )
    source_url: HttpUrl | None = Field(
        None, description="The URL of the news article that was summarized."
    )
