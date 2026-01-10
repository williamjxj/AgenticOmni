"""JSON structured logging configuration using structlog.

This module sets up structlog with JSON output for production-ready logging.
All logs include standard fields: timestamp, log_level, module, message, and
contextual information like tenant_id and request_id when available.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application-level context to log events.

    Args:
        logger: The logger instance
        method_name: The name of the log method called
        event_dict: The event dictionary

    Returns:
        Modified event dictionary with app context
    """
    event_dict["app"] = "agenticomni"
    event_dict["version"] = "0.1.0"
    return event_dict


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structured logging with structlog.

    This function sets up structlog with appropriate processors for
    development or production use.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ("json" for production, "console" for development)
    """
    # Set log level for standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Common processors for all environments
    common_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Choose renderer based on format
    if log_format == "json":
        # JSON renderer for production
        renderer = structlog.processors.JSONRenderer()
    else:
        # Console renderer for development (colored, human-readable)
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Configure structlog
    structlog.configure(
        processors=common_processors + [renderer],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance for a module.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured structlog logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("application_started", version="0.1.0")
        >>> logger.error("database_error", error="Connection refused")
    """
    return structlog.get_logger(name)


# Standard log fields that should be included in logs:
# - timestamp: ISO 8601 timestamp (added by TimeStamper)
# - log_level: DEBUG, INFO, WARNING, ERROR, CRITICAL (added by add_log_level)
# - module: Logger name (added by add_logger_name)
# - message: Log message (the event name in structlog)
# - app: Application name (added by add_app_context)
# - version: Application version (added by add_app_context)
# - tenant_id: Tenant ID (bind in request context)
# - request_id: Request ID (bind in request context)
# - user_id: User ID (bind in request context)
# - error: Error message (for error logs)
# - duration_ms: Duration in milliseconds (for performance logs)
