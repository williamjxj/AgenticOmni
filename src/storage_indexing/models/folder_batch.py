"""FolderBatch model for tracking batch folder uploads.

This module defines the FolderBatch SQLAlchemy model for tracking folder upload progress.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage_indexing.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.storage_indexing.models.document import Document
    from src.storage_indexing.models.tenant import Tenant
    from src.storage_indexing.models.user import User


class FolderBatch(Base, TimestampMixin):
    """FolderBatch model for tracking batch folder uploads.
    
    Attributes:
        id: Primary key
        tenant_id: Foreign key to tenants table
        user_id: Foreign key to users table
        folder_path: Absolute path to uploaded folder
        original_folder_name: Original folder name from upload
        total_files_discovered: Count of markdown files discovered
        files_processed: Count of successfully processed files
        files_failed: Count of failed files
        status: Batch processing status (discovering, processing, completed, partial_failure, failed)
        error_message: Error details if batch failed
        created_at: Batch creation timestamp
        updated_at: Last update timestamp
        completed_at: Batch completion timestamp
    
    Relationships:
        documents: Related Document records
        tenant: Related Tenant
        user: Related User
    
    Example:
        >>> batch = FolderBatch(
        ...     tenant_id=1,
        ...     user_id=42,
        ...     folder_path="/uploads/tenant_1/batch_123/",
        ...     original_folder_name="docs",
        ...     status="discovering"
        ... )
        >>> session.add(batch)
        >>> await session.commit()
    """
    
    __tablename__ = 'folder_batches'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete='SET NULL'))
    folder_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_folder_name: Mapped[str] = mapped_column(String(500), nullable=False)
    total_files_discovered: Mapped[int] = mapped_column(Integer, default=0)
    files_processed: Mapped[int] = mapped_column(Integer, default=0)
    files_failed: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='discovering')
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    
    # Relationships
    documents: Mapped[list["Document"]] = relationship('Document', back_populates='folder_batch', lazy='dynamic')
    tenant = relationship('Tenant', back_populates='folder_batches')
    user = relationship('User', back_populates='folder_batches')
    
    __table_args__ = (
        CheckConstraint('files_processed <= total_files_discovered', name='check_files_counts'),
        CheckConstraint(
            "status IN ('discovering', 'processing', 'completed', 'partial_failure', 'failed')",
            name='check_folder_batch_status'
        ),
    )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage.
        
        Returns:
            Progress as percentage (0.0 to 100.0)
        
        Example:
            >>> batch.total_files_discovered = 100
            >>> batch.files_processed = 47
            >>> batch.progress_percentage
            47.0
        """
        if self.total_files_discovered == 0:
            return 0.0
        return (self.files_processed / self.total_files_discovered) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if batch processing is complete.
        
        Returns:
            True if status is terminal (completed, partial_failure, failed)
        
        Example:
            >>> batch.status = "completed"
            >>> batch.is_complete
            True
        """
        return self.status in ('completed', 'partial_failure', 'failed')
    
    @property
    def has_failures(self) -> bool:
        """Check if batch has any failed files.
        
        Returns:
            True if files_failed > 0
        
        Example:
            >>> batch.files_failed = 3
            >>> batch.has_failures
            True
        """
        return self.files_failed > 0
    
    def __repr__(self) -> str:
        """String representation of FolderBatch."""
        return (
            f"<FolderBatch(id={self.id}, folder_name='{self.original_folder_name}', "
            f"status='{self.status}', progress={self.progress_percentage:.1f}%)>"
        )
