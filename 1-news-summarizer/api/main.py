from core.config import EnvSettings, get_settings
from core.openai import AOAIClient
from fastapi import Depends, FastAPI, status
from loguru import logger

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


@app.get("/openai_health")
async def openai_health(settings: EnvSettings = Depends(lambda: get_settings())):
    try:
        client = AOAIClient(api_key=settings.openai_api_key)
        response = await client.response(prompt="Hello, OpenAI!")
        logger.info("OpenAI health check successful")
        return {"openai_response": response, "status": status.HTTP_200_OK}
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return {"error": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}
