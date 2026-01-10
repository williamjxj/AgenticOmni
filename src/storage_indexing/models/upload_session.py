"""UploadSession model for resumable uploads."""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base


class UploadStatus(str, Enum):
    """Upload session status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class UploadSession(Base):
    """Upload session entity for resumable uploads.

    Each session tracks the progress of a resumable upload for large files.
    Sessions expire after 24 hours of inactivity.

    Attributes:
        session_id: Primary key, unique session identifier (UUID)
        tenant_id: Foreign key to tenants table
        user_id: Foreign key to users table
        filename: Original filename
        mime_type: Detected MIME type
        total_size_bytes: Total file size in bytes
        uploaded_size_bytes: Bytes uploaded so far
        chunk_size_bytes: Chunk size in bytes (default 5MB)
        storage_path: Temporary storage location
        status: Session status (active, completed, cancelled, expired)
        expires_at: Session expiration timestamp (24 hours)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "upload_sessions"

    session_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        comment="Primary key, unique session identifier (UUID)",
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenants",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename",
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Detected MIME type",
    )

    total_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Total file size in bytes",
    )

    uploaded_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Bytes uploaded so far",
    )

    chunk_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5242880,  # 5MB
        comment="Chunk size in bytes (default 5MB)",
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Temporary storage location",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UploadStatus.ACTIVE.value,
        index=True,
        comment="Session status (active, completed, cancelled, expired)",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Session expiration timestamp (24 hours)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        comment="Record last update timestamp",
    )

    def __repr__(self) -> str:
        """String representation of UploadSession."""
        return f"<UploadSession(session_id={self.session_id}, filename='{self.filename}', status='{self.status}')>"
