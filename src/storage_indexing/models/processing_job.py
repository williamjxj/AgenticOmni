"""ProcessingJob model for background task tracking."""

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base, TenantScopedMixin


class JobStatus(str, Enum):
    """Job status enumeration with 6-state state machine.

    State transitions:
    - pending → processing
    - processing → completed | failed | retrying
    - retrying → processing | failed | cancelled
    - failed → (terminal, no auto-transition)
    - completed → (terminal)
    - cancelled → (terminal)
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobType(str, Enum):
    """Job type enumeration."""

    DOCUMENT_PARSING = "document_parsing"
    EMBEDDING_GENERATION = "embedding_generation"
    OCR_PROCESSING = "ocr_processing"
    AUDIO_TRANSCRIPTION = "audio_transcription"


class ProcessingJob(Base, TenantScopedMixin):
    """Processing job entity for background task tracking.

    Each job represents a background task like document parsing,
    embedding generation, or OCR processing.

    Attributes:
        job_id: Primary key, unique job identifier
        document_id: Foreign key to documents table
        tenant_id: Foreign key to tenants table (row-level isolation)
        job_type: Type of job (document_parsing, embedding_generation, etc.)
        status: Current job status (6-state state machine)
        retry_count: Number of retry attempts
        max_retries: Maximum number of retries allowed
        started_at: Job start timestamp
        completed_at: Job completion timestamp
        error_message: Error message if job failed
        created_at: Record creation timestamp
    """

    __tablename__ = "processing_jobs"

    job_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique job identifier",
    )

    document_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Foreign key to documents (nullable for non-document jobs)",
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenants (row-level isolation)",
    )

    job_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type of job (document_parsing, embedding_generation, etc.)",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=JobStatus.PENDING.value,
        index=True,
        comment="Current job status (pending, processing, completed, failed, cancelled, retrying)",
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of retry attempts",
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum number of retries allowed",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Job start timestamp",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Job completion timestamp",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if job failed",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="Record creation timestamp",
    )

    def __repr__(self) -> str:
        """String representation of ProcessingJob."""
        return (
            f"<ProcessingJob(job_id={self.job_id}, type='{self.job_type}', status='{self.status}')>"
        )
