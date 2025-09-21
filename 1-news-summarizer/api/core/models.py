from pydantic import BaseModel, Field, HttpUrl, model_validator


class ArticleRequest(BaseModel):
    """Pydantic model for article fetcher class."""

    url: HttpUrl | None = Field(
        None, description="The URL of the news article to summarize."
    )
    text: str | None = Field(
        None, description="The text of the news article to summarize."
    )

    @model_validator(mode="after")
    def check_url_or_text(self):
        """Ensure that either 'url' or 'text' is provided."""
        if not (self.url or self.text):
            raise ValueError("Either 'url' or 'text' must be provided.")
        return self


class SummaryResponse(BaseModel):
    """Pydantic model for summary response."""

    summary: str = Field(..., description="The summarized text of the article.")
    source_url: HttpUrl | None = Field(
        None, description="The URL of the news article that was summarized."
    )
