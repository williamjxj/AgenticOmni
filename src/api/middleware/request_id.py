"""Request ID middleware for tracking async operations.

This middleware generates a unique request ID for each incoming request
and adds it to the response headers and logging context.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import structlog

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request IDs to all requests.
    
    The request ID is:
    - Generated as a UUID4
    - Added to response headers as X-Request-ID
    - Added to logging context for all logs within the request
    - Accessible via request.state.request_id
    
    Example:
        >>> app.add_middleware(RequestIDMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add request ID.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response with X-Request-ID header
        """
        # Check if request already has an ID (from load balancer, etc.)
        request_id = request.headers.get("X-Request-ID")
        
        # Generate new ID if not present
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store in request state for access in route handlers
        request.state.request_id = request_id
        
        # Add to logging context
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            "Request completed",
            status_code=response.status_code,
        )
        
        # Clear logging context
        structlog.contextvars.clear_contextvars()
        
        return response
