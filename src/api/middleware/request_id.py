"""Request ID middleware for tracking requests across the system."""

import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and attach a unique request ID to each request.

    The request ID is:
    - Generated as a UUID4
    - Added to request.state.request_id for access in route handlers
    - Added to the X-Request-ID response header for client tracking
    - Logged with all request logs for traceability

    Example:
        >>> app.add_middleware(RequestIDMiddleware)
        >>>
        >>> @app.get("/users")
        >>> async def get_users(request: Request):
        >>>     request_id = request.state.request_id
        >>>     logger.info("Fetching users", request_id=request_id)
        >>>     return []
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and inject request ID.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response: Response with X-Request-ID header
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Store in request state for access in handlers
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
