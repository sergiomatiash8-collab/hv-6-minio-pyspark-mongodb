"""
Structured logging configuration using structlog. 
Provides JSON output for log aggregation.
"""

import structlog
import logging
import sys

def configure_logging(log_level: str = "INFO"):
    """Configure structured logging for the application."""
    
    # Базова конфігурація стандартного logging для перехоплення системних повідомлень
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            # Додаємо форматтер для обробки винятків у JSON
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()