"""Pydantic schemas for embedding generation.

Feature: 004-ocr-embedding-pipeline
Task: T027
"""

from datetime import datetime

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Request schema for embedding generation.

    Attributes:
        document_id: Document ID to generate embeddings for
        force_regenerate: Force regeneration even if embeddings exist
    """

    document_id: int = Field(..., gt=0)
    force_regenerate: bool = Field(default=False)


class EmbeddingResponse(BaseModel):
    """Response schema for embedding generation.

    Attributes:
        document_id: Document ID processed
        embedding_status: Status (not_started, in_progress, completed, failed)
        chunks_created: Number of chunks created
        embedding_model: Model used (multilingual-e5-base)
        processing_time_ms: Processing time in milliseconds
        created_at: When processing started
    """

    document_id: int
    embedding_status: str
    chunks_created: int | None = None
    embedding_model: str | None = None
    processing_time_ms: int | None = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ChunkResponse(BaseModel):
    """Response schema for document chunk.

    Attributes:
        chunk_id: Unique identifier
        document_id: Foreign key to documents
        content_text: Text content
        chunk_sequence: Sequence number (0-indexed)
        token_count: Number of tokens
        section_heading: Section context
        embedding_model: Model used for embedding
    """

    chunk_id: int
    document_id: int
    content_text: str
    chunk_sequence: int
    token_count: int | None = None
    section_heading: str | None = None
    embedding_model: str | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True
