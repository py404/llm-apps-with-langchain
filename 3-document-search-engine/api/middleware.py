import logging
import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Get the logger instance
logger = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.monotonic()

        # Get or generate a request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        user_agent = request.headers.get("user-agent", "-")

        # Clear existing context from previous requests to avoid leaking data
        structlog.contextvars.clear_contextvars()
        # Bind the request_id to the context for all logs during this request
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Create a request-specific logger with additional details
        request_logger = logger.bind(
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        request_logger.info("Incoming request")

        try:
            response = await call_next(request)
        except Exception:
            # Log unhandled exceptions with an error status
            duration_ms = (time.monotonic() - start_time) * 1000
            request_logger.error(
                "An unhandled exception occurred",
                status=500,
                duration=f"{duration_ms:.2f}ms",
                exc_info=True,
            )
            # Re-raise the exception to be handled by FastAPI's exception handler
            raise

        duration_ms = (time.monotonic() - start_time) * 1000
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        request_logger.log(
            log_level,
            "Request completed",
            status=response.status_code,
            duration=f"{duration_ms:.2f}ms",
        )

        return response
