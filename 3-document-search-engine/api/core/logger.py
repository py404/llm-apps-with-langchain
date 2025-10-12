import logging
import sys

import structlog
from structlog.stdlib import (
    LoggerFactory,
    ProcessorFormatter,
)


class LogConfig:
    def __init__(self, is_production: bool = False):
        self.is_production = is_production
        self._configure()

    def _get_processors(self):
        """Returns the list of structlog processors based on the environment."""
        shared_processors = [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ]

        if self.is_production:
            return shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        else:
            return shared_processors + [
                structlog.processors.StackInfoRenderer(),
                structlog.dev.ConsoleRenderer(),
            ]

    def _configure(self):
        """Applies the structlog and standard logging configuration."""
        processors = self._get_processors()
        renderer = processors[-1]

        # 1. Configure structlog's core processors
        structlog.configure(
            processors=processors,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # 2. Configure standard library logging to use structlog's formatter
        handler = logging.StreamHandler(sys.stdout)
        formatter = ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
            ],
        )
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        # Set the root logger to DEBUG to capture all levels
        root_logger.setLevel(logging.DEBUG)

        for _log in ["uvicorn", "uvicorn.error"]:
            # Make sure the logs are handled by the root logger
            logging.getLogger(_log).handlers.clear()
            logging.getLogger(_log).propagate = True
