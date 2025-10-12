import os

import structlog
from fastapi import FastAPI

from api.core.logger import LogConfig
from api.middleware import RequestContextMiddleware

# Call structlog configuration function
is_prod = os.getenv("ENVIRONMENT") == "production"
LogConfig(is_production=is_prod)

# Get the logger instance
logger = structlog.get_logger(__name__)

app = FastAPI()


app.add_middleware(RequestContextMiddleware)


@app.get("/")
async def index():
    logger.debug("Index endpoint called")
    logger.debug("This is a debug log")
    logger.info("Handling root endpoint")
    logger.warning("This is a warning log")
    logger.error("This is an error log")
    return {"message": "Welcome to the Document Search Engine API!"}
