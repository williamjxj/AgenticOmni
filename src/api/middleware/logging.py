"""Logging middleware for structured request/response logging."""

import time
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with structured logging.

    Logs include:
    - Request method, path, query parameters
    - Request ID (from RequestIDMiddleware)
    - Response status code
    - Request duration in milliseconds
    - Client IP address

    Uses structlog for JSON-formatted logs with consistent structure.

    Example:
        >>> app.add_middleware(LoggingMiddleware)
        >>> # Logs will include:
        >>> # {"event": "request_completed", "method": "GET", "path": "/api/v1/health",
        >>> #  "status_code": 200, "duration_ms": 15.2, "request_id": "..."}
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response: Response from handler
        """
        # Start timer
        start_time = time.time()

        # Extract request details
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else "unknown"

        # Bind request context to logger
        log = logger.bind(
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
        )

        # Log incoming request
        log.info(
            "request_started",
            query_params=query_params,
        )

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            log.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            log.error(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2),
            )

            # Re-raise to be handled by exception handler
            raise
