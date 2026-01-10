"""Document model for uploaded files."""

from enum import Enum
from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base, TenantScopedMixin, TimestampMixin


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base, TenantScopedMixin, TimestampMixin):
    """Document entity for uploaded files.

    Each document represents an uploaded file (PDF, DOCX, image, etc.)
    that will be processed and indexed for retrieval.

    Attributes:
        document_id: Primary key, unique document identifier
        tenant_id: Foreign key to tenants table (row-level isolation)
        filename: Original filename
        file_type: File MIME type or extension
        file_size: File size in bytes
        storage_path: Path to stored file (local or cloud storage)
        processing_status: Processing status (pending, processing, completed, failed)
        document_metadata: JSON field for document-specific metadata
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique document identifier",
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenants (row-level isolation)",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename",
    )

    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="File MIME type or extension",
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes",
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Path to stored file (local or cloud)",
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ProcessingStatus.PENDING.value,
        index=True,
        comment="Processing status (pending, processing, completed, failed)",
    )

    document_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Document-specific metadata (JSONB)",
    )

    def __repr__(self) -> str:
        """String representation of Document."""
        return f"<Document(document_id={self.document_id}, filename='{self.filename}', status='{self.processing_status}')>"
