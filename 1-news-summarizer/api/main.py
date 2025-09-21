from fastapi import Depends, FastAPI, HTTPException, status
from loguru import logger
from openai import OpenAIError

from core.article_fetcher import ArticleFetcher
from core.chat_client import ChatClient
from core.config import EnvSettings, get_settings
from core.models import ArticleRequest, SummaryResponse
from core.summarizer import NewsArticleSummarizer

app = FastAPI(
    title="News Summarizer API",
    description="An API to summarize news articles using LangChain and LLMs.",
    version="0.1.0",
    docs_url="/docs",
)


@app.get("/")
def index():
    logger.info("Index endpoint called")
    return {"message": "Hello, FastAPI!"}


@app.post("/summarize")
async def summarize_article(
    request: ArticleRequest, settings: EnvSettings = Depends(lambda: get_settings())
) -> SummaryResponse:
    """
    Endpoint to summarize a news article given its URL or text.
    """
    try:
        fetcher = ArticleFetcher(
            url="https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing"
        )
        article = fetcher.fetch_article()
        print(f"Title: {article.title}")
        print(f"Text: {article.text[:200]}...")  # Print first

        if not article.text or article.text.strip() == "":
            logger.error("No article text available for summarization")
            raise HTTPException(status_code=400, detail="No article text provided")
        logger.info(f"Article text length: {len(article.text)} characters")

        logger.info("Starting summarization...")
        openai_client = ChatClient(
            api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0
        ).client
        summarizer = NewsArticleSummarizer(llm=openai_client)

        logger.info(f"Article Title: {article.title}")
        logger.info(f"Article Text: {article.text[:100]}...")  # Log first 100 chars
        summary = await summarizer.summarize(
            article_title=article.title, article_text=article.text
        )
        logger.info(f"Summary: {summary}")
        logger.info("Summarization completed successfully")

        return SummaryResponse(summary=summary, source_url=request.url)

    except OpenAIError as e:
        logger.error(f"OpenAI API Error: {e}")

    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
