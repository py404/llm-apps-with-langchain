from fastapi import FastAPI
from loguru import logger

from api._app import create_app
from api.routes.ingestion import router as ingestion_router
from api.routes.qa import router as qa_router

app: FastAPI = create_app()


@app.get("/")
def index():
    logger.info("Index endpoint called")
    return {"message": "Welcome to the QA Chatbot API!"}


# Routers
app.include_router(ingestion_router)
app.include_router(qa_router)
