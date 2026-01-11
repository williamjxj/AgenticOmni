from src.shared.exceptions import (
    AgenticOmniException,
    ExternalServiceError,
    ValidationError,
    DatabaseError,
    NotFoundError,
)


class EmbeddingError(AgenticOmniException):
    """Base exception for embedding-related errors."""

    pass


class EmbeddingProviderError(ExternalServiceError, EmbeddingError):
    """Raised when an external embedding provider fails."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        """Initialize exception with message and provider."""
        self.provider = provider
        super().__init__(message, details={"provider": provider})


class EmbeddingModelNotLoadedError(EmbeddingError):
    """Raised when embedding model is not loaded."""

    def __init__(self, model_name: str) -> None:
        """Initialize exception with model name."""
        self.model_name = model_name
        super().__init__(f"Embedding model not loaded: {model_name}", details={"model_name": model_name})


class EmbeddingGenerationError(EmbeddingError):
    """Raised when embedding generation fails."""

    def __init__(self, document_id: int, reason: str) -> None:
        """Initialize exception with document ID and reason."""
        self.document_id = document_id
        self.reason = reason
        super().__init__(
            f"Embedding generation failed for document {document_id}: {reason}",
            details={"document_id": document_id, "reason": reason}
        )


class ChunkingError(EmbeddingError):
    """Raised when document chunking fails."""

    def __init__(self, document_id: int, reason: str) -> None:
        """Initialize exception with document ID and reason."""
        self.document_id = document_id
        self.reason = reason
        super().__init__(f"Chunking failed for document {document_id}: {reason}", details={"document_id": document_id, "reason": reason})


class NoTextContentError(EmbeddingError):
    """Raised when document has no text content for embedding."""

    def __init__(self, document_id: int) -> None:
        """Initialize exception with document ID."""
        self.document_id = document_id
        super().__init__(
            f"No text content available for document {document_id}. Run OCR first.",
            details={"document_id": document_id}
        )


class SearchError(AgenticOmniException):
    """Base exception for search-related errors."""

    pass


class VectorSearchError(DatabaseError, SearchError):
    """Raised when vector similarity search fails."""

    def __init__(self, query: str, reason: str) -> None:
        """Initialize exception with query and reason."""
        self.query = query
        self.reason = reason
        super().__init__(f"Vector search failed for query '{query}': {reason}", details={"query": query, "reason": reason})


class NoEmbeddingsAvailableError(NotFoundError, SearchError):
    """Raised when no embeddings are available for search."""

    def __init__(self, tenant_id: int) -> None:
        """Initialize exception with tenant ID."""
        self.tenant_id = tenant_id
        super().__init__(
            f"No embeddings available for tenant {tenant_id}. Generate embeddings first.",
            details={"tenant_id": tenant_id}
        )


class InvalidSearchQueryError(ValidationError, SearchError):
    """Raised when search query is invalid."""

    def __init__(self, query: str, reason: str) -> None:
        """Initialize exception with query and reason."""
        self.query = query
        self.reason = reason
        super().__init__(f"Invalid search query '{query}': {reason}", details={"query": query, "reason": reason})
