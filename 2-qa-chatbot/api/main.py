from fastapi import FastAPI
from loguru import logger

app = FastAPI(
    title="QA Chatbot API",
    description="API for a Question-Answering Chatbot",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
def index():
    logger.info("Index endpoint called")
    return {"message": "Welcome to the QA Chatbot API!"}
