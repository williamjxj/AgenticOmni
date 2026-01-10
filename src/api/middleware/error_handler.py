"""Global error handler middleware for standardized error responses.

This middleware catches all exceptions and returns standardized JSON error
responses with appropriate HTTP status codes.
"""

from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import structlog

from src.shared.exceptions import (
    AgenticOmniException,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConflictError,
    DatabaseError,
    DocumentProcessingError,
    ExternalServiceError,
    FileTooLargeError,
    FileTypeNotAllowedError,
    MalwareScanFailedError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    TenantIsolationError,
    ValidationError,
)

logger = structlog.get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for standardized error handling.
    
    Catches all exceptions and returns JSON responses with:
    - Appropriate HTTP status codes
    - Consistent error structure
    - Request ID for tracking
    - Detailed logging
    
    Example:
        >>> app.add_middleware(ErrorHandlerMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response or JSONResponse with error details
        """
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            return await self._handle_exception(request, exc)

    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle exception and return standardized error response.
        
        Args:
            request: Incoming request
            exc: Exception that was raised
            
        Returns:
            JSONResponse with error details
        """
        # Get request ID from request state
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Map exception types to HTTP status codes
        status_code = 500
        error_type = "internal_error"
        error_message = "An internal server error occurred"
        error_details = {}
        
        if isinstance(exc, ValidationError):
            status_code = 400
            error_type = "validation_error"
            error_message = str(exc)
            error_details = getattr(exc, "details", {})
            
        elif isinstance(exc, FileTypeNotAllowedError):
            status_code = 400
            error_type = "file_type_not_allowed"
            error_message = str(exc)
            error_details = {
                "file_type": exc.file_type,
                "allowed_types": exc.allowed_types,
            }
            
        elif isinstance(exc, FileTooLargeError):
            status_code = 413
            error_type = "file_too_large"
            error_message = str(exc)
            error_details = {
                "file_size": exc.file_size,
                "max_size": exc.max_size,
            }
            
        elif isinstance(exc, QuotaExceededError):
            status_code = 413
            error_type = "quota_exceeded"
            error_message = str(exc)
            error_details = {
                "used_bytes": exc.used_bytes,
                "quota_bytes": exc.quota_bytes,
            }
            
        elif isinstance(exc, MalwareScanFailedError):
            status_code = 400
            error_type = "malware_detected"
            error_message = str(exc)
            error_details = {"virus_name": exc.virus_name}
            
        elif isinstance(exc, AuthenticationError):
            status_code = 401
            error_type = "authentication_error"
            error_message = str(exc)
            
        elif isinstance(exc, AuthorizationError):
            status_code = 403
            error_type = "authorization_error"
            error_message = str(exc)
            
        elif isinstance(exc, NotFoundError):
            status_code = 404
            error_type = "not_found"
            error_message = str(exc)
            
        elif isinstance(exc, ConflictError):
            status_code = 409
            error_type = "conflict"
            error_message = str(exc)
            
        elif isinstance(exc, RateLimitError):
            status_code = 429
            error_type = "rate_limit_exceeded"
            error_message = str(exc)
            
        elif isinstance(exc, TenantIsolationError):
            status_code = 403
            error_type = "tenant_isolation_violation"
            error_message = "Access denied"
            # Log critical security error
            logger.critical(
                "Tenant isolation violation",
                request_id=request_id,
                path=request.url.path,
                error=str(exc),
            )
            
        elif isinstance(exc, (DatabaseError, ConfigurationError, ExternalServiceError, DocumentProcessingError)):
            status_code = 500
            error_type = "internal_error"
            error_message = "An internal server error occurred"
            # Don't expose internal error details to client
            
        elif isinstance(exc, AgenticOmniException):
            # Generic application exception
            status_code = 500
            error_type = "application_error"
            error_message = str(exc)
        
        # Log the error
        log_level = "error" if status_code >= 500 else "warning"
        log_func = getattr(logger, log_level)
        log_func(
            "Request failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            error_type=error_type,
            error_message=str(exc),
            exception_type=type(exc).__name__,
        )
        
        # Build error response
        error_response = {
            "error": {
                "type": error_type,
                "message": error_message,
                "request_id": request_id,
            }
        }
        
        # Add details if present
        if error_details:
            error_response["error"]["details"] = error_details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )
