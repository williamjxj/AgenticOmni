"""MarkdownMetadata model for storing markdown-specific metadata.

This module defines the MarkdownMetadata SQLAlchemy model for markdown document metadata.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text, TIMESTAMP, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage_indexing.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.storage_indexing.models.document import Document


class MarkdownMetadata(Base):
    """MarkdownMetadata model for markdown-specific metadata.
    
    Attributes:
        id: Primary key
        document_id: Foreign key to documents table (one-to-one)
        frontmatter: Parsed YAML frontmatter as JSONB
        heading_count: Count of headings (H1-H6)
        code_block_count: Count of code blocks
        mermaid_diagram_count: Count of Mermaid diagrams
        table_count: Count of markdown tables
        link_count: Count of hyperlinks
        image_count: Count of image references
        link_urls: Array of extracted URLs
        has_yaml_frontmatter: Quick check for frontmatter presence
        created_at: Metadata creation timestamp
    
    Relationships:
        document: Related Document record
    
    Example:
        >>> metadata = MarkdownMetadata(
        ...     document_id=1001,
        ...     frontmatter={"title": "API Docs", "author": "John"},
        ...     heading_count=12,
        ...     code_block_count=8,
        ...     has_yaml_frontmatter=True
        ... )
        >>> session.add(metadata)
        >>> await session.commit()
    """
    
    __tablename__ = 'markdown_metadata'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    frontmatter: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    heading_count: Mapped[int] = mapped_column(Integer, default=0)
    code_block_count: Mapped[int] = mapped_column(Integer, default=0)
    mermaid_diagram_count: Mapped[int] = mapped_column(Integer, default=0)
    table_count: Mapped[int] = mapped_column(Integer, default=0)
    link_count: Mapped[int] = mapped_column(Integer, default=0)
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    link_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    has_yaml_frontmatter: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationship
    document = relationship(
        "Document",
        back_populates="markdown_metadata",
        uselist=False
    )
    
    __table_args__ = (
        CheckConstraint(
            'heading_count >= 0 AND code_block_count >= 0 AND mermaid_diagram_count >= 0 AND table_count >= 0',
            name='check_counts_positive'
        ),
    )
