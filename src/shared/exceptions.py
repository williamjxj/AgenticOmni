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


# ============================================================================
# Document Upload Exceptions (T016)
# ============================================================================


class FileTypeNotAllowedError(ValidationError):
    """Raised when uploaded file type is not in allowed list."""

    def __init__(self, message: str, *, file_type: str | None = None, allowed_types: list[str] | None = None) -> None:
        """Initialize with file type information."""
        super().__init__(message, details={"file_type": file_type, "allowed_types": allowed_types})
        self.file_type = file_type
        self.allowed_types = allowed_types


class FileTooLargeError(ValidationError):
    """Raised when uploaded file exceeds maximum size limit."""

    def __init__(self, message: str, *, file_size: int | None = None, max_size: int | None = None) -> None:
        """Initialize with file size information."""
        super().__init__(message, details={"file_size": file_size, "max_size": max_size})
        self.file_size = file_size
        self.max_size = max_size


class QuotaExceededError(ValidationError):
    """Raised when upload would exceed tenant storage quota."""

    def __init__(self, message: str, *, used_bytes: int | None = None, quota_bytes: int | None = None) -> None:
        """Initialize with quota information."""
        super().__init__(message, details={"used_bytes": used_bytes, "quota_bytes": quota_bytes})
        self.used_bytes = used_bytes
        self.quota_bytes = quota_bytes


class MalwareScanFailedError(ValidationError):
    """Raised when malware is detected in uploaded file."""

    def __init__(self, message: str, *, virus_name: str | None = None) -> None:
        """Initialize with malware information."""
        super().__init__(message, details={"virus_name": virus_name})
        self.virus_name = virus_name
