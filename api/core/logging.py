"""
Structured logging configuration for the Agent API.

This module sets up structured logging with proper formatting,
levels, and monitoring integration for production use.
"""

import logging
import logging.config
import sys
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory
from .config import get_settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add caller information
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # JSON formatting for production
            structlog.processors.JSONRenderer() if not settings.debug 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_agent_execution(
    agent_id: str,
    execution_id: str,
    status: str,
    duration_seconds: float = None,
    error_message: str = None,
    **kwargs: Any
) -> None:
    """Log agent execution events with structured data."""
    logger = get_logger("agent_execution")
    
    log_data = {
        "agent_id": agent_id,
        "execution_id": execution_id,
        "status": status,
        **kwargs
    }
    
    if duration_seconds is not None:
        log_data["duration_seconds"] = duration_seconds
    
    if error_message:
        log_data["error_message"] = error_message
        logger.error("Agent execution failed", **log_data)
    elif status == "completed":
        logger.info("Agent execution completed", **log_data)
    elif status == "started":
        logger.info("Agent execution started", **log_data)
    else:
        logger.info("Agent execution status update", **log_data)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None,
    **kwargs: Any
) -> None:
    """Log API request events with structured data."""
    logger = get_logger("api_request")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        **kwargs
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if status_code >= 500:
        logger.error("API request failed", **log_data)
    elif status_code >= 400:
        logger.warning("API request client error", **log_data)
    else:
        logger.info("API request completed", **log_data)


def log_system_event(
    event_type: str,
    message: str,
    level: str = "info",
    **kwargs: Any
) -> None:
    """Log system events with structured data."""
    logger = get_logger("system")
    
    log_data = {
        "event_type": event_type,
        **kwargs
    }
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, **log_data) 