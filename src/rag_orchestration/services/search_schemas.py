"""Pydantic schemas for vector search operations.

Feature: 004-ocr-embedding-pipeline
Task: T028
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic search.

    Attributes:
        query_text: Search query text
        tenant_id: Tenant ID for filtering
        top_k: Number of results to return (default: 10, max: 50)
        filters: Optional metadata filters (date, folder, etc.)
    """

    query_text: str = Field(..., min_length=1, max_length=1000)
    tenant_id: int = Field(..., gt=0)
    top_k: int = Field(default=10, gt=0, le=50)
    filters: dict[str, Any] | None = Field(default=None)


class SearchResultItem(BaseModel):
    """Schema for a single search result.

    Attributes:
        chunk_id: Matching chunk ID
        document_id: Matching document ID
        similarity_score: Cosine similarity score (0.0-1.0)
        rank_position: Result rank (1-based)
        text_snippet: Text preview
        document_title: Document filename
        page_number: Page number if available
    """

    chunk_id: int
    document_id: int
    similarity_score: float
    rank_position: int
    text_snippet: str
    document_title: str | None = None
    page_number: int | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class SemanticSearchResponse(BaseModel):
    """Response schema for semantic search.

    Attributes:
        query_id: Search query ID for tracking
        query_text: Original query text
        results: List of search results
        total_results: Total number of results
        search_duration_ms: Search execution time
        created_at: When search was executed
    """

    query_id: int
    query_text: str
    results: list[SearchResultItem]
    total_results: int
    search_duration_ms: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SimilarDocumentsRequest(BaseModel):
    """Request schema for finding similar documents.

    Attributes:
        document_id: Source document ID
        tenant_id: Tenant ID for filtering
        top_k: Number of similar documents to return
        exclude_source: Whether to exclude the source document
    """

    document_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)
    top_k: int = Field(default=5, gt=0, le=20)
    exclude_source: bool = Field(default=True)


class SimilarDocumentsResponse(BaseModel):
    """Response schema for finding similar documents.

    Attributes:
        source_document_id: Source document ID
        similar_documents: List of similar documents
        search_duration_ms: Search execution time
    """

    source_document_id: int
    similar_documents: list[SearchResultItem]
    search_duration_ms: int

    class Config:
        """Pydantic config."""

        from_attributes = True
