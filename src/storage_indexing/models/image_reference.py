"""ImageReference model for tracking image references in markdown documents.

This module defines the ImageReference SQLAlchemy model for markdown image metadata.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage_indexing.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.storage_indexing.models.document import Document


class ImageReference(Base, TimestampMixin):
    """ImageReference model for tracking images in markdown documents.
    
    Attributes:
        id: Primary key
        document_id: Foreign key to documents table
        image_url: Original image URL/path from markdown
        alt_text: Image alt text for accessibility/RAG
        is_local_path: True if relative/absolute file path
        is_base64: True if base64-encoded inline image
        is_external_url: True if http/https URL
        resolved_path: Resolved absolute path for local images
        file_size_bytes: Size of the image file (if available)
        ocr_pending: True if OCR processing is queued
        ocr_completed_at: Timestamp when OCR completed
        position_in_document: Order of appearance (0-based)
        created_at: Record creation timestamp
    
    Relationships:
        document: Related Document record
    
    Example:
        >>> img_ref = ImageReference(
        ...     document_id=1001,
        ...     image_url="./diagrams/architecture.png",
        ...     alt_text="System architecture diagram",
        ...     is_local_path=True,
        ...     resolved_path="/data/docs/diagrams/architecture.png",
        ...     position_in_document=0
        ... )
        >>> session.add(img_ref)
        >>> await session.commit()
    """
    
    __tablename__ = 'image_references'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(Text)
    is_local_path: Mapped[bool] = mapped_column(Boolean, default=False)
    is_base64: Mapped[bool] = mapped_column(Boolean, default=False)
    is_external_url: Mapped[bool] = mapped_column(Boolean, default=True)
    resolved_path: Mapped[str | None] = mapped_column(Text)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    ocr_pending: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    position_in_document: Mapped[int | None] = mapped_column(Integer)
    
    # Relationship
    document = relationship(
        "Document",
        back_populates="image_references"
    )
    
    __table_args__ = (
        CheckConstraint(
            '(is_local_path::int + is_base64::int + is_external_url::int) = 1',
            name='check_image_type'
        ),
    )
    
    @property
    def image_type(self) -> str:
        """Get the image type as a string.
        
        Returns:
            'local', 'base64', or 'external'
        """
        if self.is_local_path:
            return 'local'
        elif self.is_base64:
            return 'base64'
        else:
            return 'external'
