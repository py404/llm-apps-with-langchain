from _app import create_app
from fastapi import FastAPI
from loguru import logger

app: FastAPI = create_app()


@app.get("/")
def index():
    logger.info("Index endpoint called")
    return {"message": "Welcome to the QA Chatbot API!"}
