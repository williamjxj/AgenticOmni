"""Custom exception classes for AgenticOmni.

This module defines application-specific exceptions for better error handling
and reporting.
"""


class AgenticOmniException(Exception):
    """Base exception for all AgenticOmni errors."""

    def __init__(self, message: str, *, details: dict[str, any] | None = None) -> None:
        """Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional context (e.g., field names, values, constraints)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(AgenticOmniException):
    """Raised when configuration is invalid or missing.

    This exception is raised during application startup if required
    environment variables are missing or have invalid values.

    Example:
        >>> raise ConfigurationError(
        ...     "Missing required environment variable",
        ...     details={"variable": "DATABASE_URL"}
        ... )
    """


class DatabaseError(AgenticOmniException):
    """Raised when database operations fail.

    This includes connection errors, query failures, migration issues, etc.
    """


class AuthenticationError(AgenticOmniException):
    """Raised when authentication fails.

    This includes invalid credentials, expired tokens, etc.
    """


class AuthorizationError(AgenticOmniException):
    """Raised when authorization fails.

    This includes insufficient permissions, denied access, etc.
    """


class TenantIsolationError(AgenticOmniException):
    """Raised when tenant isolation is violated.

    This is a critical security error indicating a potential data leak
    across tenant boundaries.
    """


class DocumentProcessingError(AgenticOmniException):
    """Raised when document processing fails.

    This includes OCR errors, parsing failures, format detection issues, etc.
    """


class ValidationError(AgenticOmniException):
    """Raised when data validation fails.

    This includes invalid input data, constraint violations, etc.
    """


class NotFoundError(AgenticOmniException):
    """Raised when a requested resource is not found."""


class ConflictError(AgenticOmniException):
    """Raised when an operation conflicts with existing data.

    Example: Creating a user with an email that already exists.
    """


class RateLimitError(AgenticOmniException):
    """Raised when rate limits are exceeded."""


class ExternalServiceError(AgenticOmniException):
    """Raised when an external service (LLM API, OCR service) fails."""
