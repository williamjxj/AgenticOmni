"""DocumentChunk model for vector embeddings."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.config import settings
from src.storage_indexing.models.base import Base


class ChunkType(str, Enum):
    """Chunk type enumeration."""

    TEXT = "text"
    TABLE = "table"
    LIST = "list"
    HEADING = "heading"
    CODE = "code"


class DocumentChunk(Base):
    """Document chunk entity for vector embeddings.

    Each chunk represents a segment of a document with its text content
    and vector embedding for semantic search.

    Attributes:
        chunk_id: Primary key, unique chunk identifier
        document_id: Foreign key to documents table
        content_text: Text content of the chunk
        embedding_vector: Vector embedding (1536 dimensions for OpenAI)
        chunk_order: Order of chunk within document (0-indexed)
        chunk_metadata: JSON field for chunk-specific metadata
        created_at: Record creation timestamp
    """

    __tablename__ = "document_chunks"

    chunk_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique chunk identifier",
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to documents",
    )

    content_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Text content of the chunk",
    )

    embedding_vector: Mapped[Any] = mapped_column(
        Vector(settings.vector_dimensions),  # OpenAI text-embedding-3-small dimension
        nullable=True,
        comment=f"Vector embedding ({settings.vector_dimensions} dimensions)",
    )

    chunk_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Order of chunk within document (0-indexed)",
    )

    # New fields for document parsing
    chunk_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ChunkType.TEXT.value,
        index=True,
        comment="Type of chunk (text, table, list, heading, code)",
    )

    start_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Starting page number (1-indexed)",
    )

    end_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Ending page number",
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Approximate token count for LLM context",
    )

    parent_heading: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Section heading for context",
    )

    chunk_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Chunk-specific metadata (JSONB)",
    )

    # Embedding fields (Feature 004-ocr-embedding-pipeline, Task T017)
    chunk_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Sequence number within document (0-indexed)",
    )

    char_offset_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Character offset in original text",
    )

    char_offset_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Character offset in original text (end)",
    )

    section_heading: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nearest section/heading for context",
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Model used: multilingual-e5-base, multilingual-e5-large",
    )

    embedding_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When embedding was created",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="Record creation timestamp",
    )

    def __repr__(self) -> str:
        """String representation of DocumentChunk."""
        return f"<DocumentChunk(chunk_id={self.chunk_id}, document_id={self.document_id}, order={self.chunk_order})>"
