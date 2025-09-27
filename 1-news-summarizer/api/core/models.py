from pydantic import BaseModel, Field, HttpUrl


class ArticleRequest(BaseModel):
    """Pydantic model for article fetcher class."""

    url: HttpUrl = Field(..., description="The URL of the news article to summarize.")


class ArticleContent(BaseModel):
    """Pydantic model for article content returned by ArticleFetcher."""

    title: str = Field(..., description="The title of the news article.")
    text: str = Field(..., description="The full text content of the news article.")


class SummaryResponse(BaseModel):
    """Pydantic model for summary response."""

    summary: str = Field(..., description="The summarized text of the article.")
    source_url: HttpUrl | None = Field(
        None, description="The URL of the news article that was summarized."
    )
