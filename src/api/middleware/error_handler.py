"""Global exception handler for FastAPI application."""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.shared.exceptions import (
    AgenticOmniException,
    ConfigurationError,
    DatabaseError,
)

logger = structlog.get_logger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application.

    Handles:
    - Custom application exceptions (AgenticOmniException)
    - Database errors (SQLAlchemyError)
    - Validation errors (Pydantic ValidationError)
    - Generic exceptions (catch-all)

    All errors are logged with structured logging and return consistent JSON responses.

    Args:
        app: FastAPI application instance

    Example:
        >>> app = FastAPI()
        >>> add_exception_handlers(app)
    """

    @app.exception_handler(AgenticOmniException)
    async def handle_agenti_exception(request: Request, exc: AgenticOmniException) -> JSONResponse:
        """Handle custom application exceptions.

        Args:
            request: Incoming request
            exc: Custom exception

        Returns:
            JSONResponse: Error response with appropriate status code
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            "application_error",
            request_id=request_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
        )

        # Map exception types to HTTP status codes
        status_code_map = {
            ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DatabaseError: status.HTTP_503_SERVICE_UNAVAILABLE,
        }

        status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(
            status_code=status_code,
            content={
                "error": type(exc).__name__,
                "message": str(exc),
                "request_id": request_id,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle database errors.

        Args:
            request: Incoming request
            exc: SQLAlchemy exception

        Returns:
            JSONResponse: Error response with 503 status
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            "database_error",
            request_id=request_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "DatabaseError",
                "message": "Database operation failed. Please try again later.",
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors.

        Args:
            request: Incoming request
            exc: Pydantic validation exception

        Returns:
            JSONResponse: Error response with 422 status
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            "validation_error",
            request_id=request_id,
            errors=exc.errors(),
            path=request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": exc.errors(),
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions.

        Args:
            request: Incoming request
            exc: Generic exception

        Returns:
            JSONResponse: Error response with 500 status
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.exception(
            "unhandled_exception",
            request_id=request_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": request_id,
            },
        )
