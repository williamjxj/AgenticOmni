"""SearchQuery model for search analytics and logging.

Feature: 004-ocr-embedding-pipeline
Task: T019
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base


class QueryType(str, Enum):
    """Search query type enumeration."""

    SEMANTIC_SEARCH = "semantic_search"
    SIMILAR_DOCUMENTS = "similar_documents"


class SearchQuery(Base):
    """SearchQuery entity for logging search queries and analytics.

    Each SearchQuery record represents a search operation performed by a user,
    including the query text, filters, and performance metrics.

    Attributes:
        query_id: Primary key, unique identifier
        tenant_id: Foreign key to tenants table
        user_id: Foreign key to users table (nullable)
        query_text: Original search query text
        query_type: Type of query (semantic_search, similar_documents)
        source_document_id: For "find similar" queries
        filters_applied: Metadata filters used (JSONB)
        result_count: Number of results returned
        search_duration_ms: Query execution time in milliseconds
        created_at: When query was executed
    """

    __tablename__ = "search_queries"

    query_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier",
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenants",
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed search",
    )

    query_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original search query text",
    )

    query_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type: semantic_search, similar_documents",
    )

    source_document_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("documents.document_id", ondelete="SET NULL"),
        nullable=True,
        comment="For find similar queries",
    )

    filters_applied: Mapped[dict[str, Any] | None] = mapped_column(
        postgresql.JSONB,
        nullable=True,
        comment="Metadata filters used (date, folder, etc.)",
    )

    result_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of results returned",
    )

    search_duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Query execution time in milliseconds",
    )

    created_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default="NOW()",
        comment="When query was executed",
    )

    # Add table args for check constraints
    __table_args__ = (
        CheckConstraint(
            "query_type IN ('semantic_search', 'similar_documents')",
            name="chk_query_type",
        ),
        CheckConstraint(
            "result_count IS NULL OR result_count >= 0",
            name="chk_result_count",
        ),
        CheckConstraint(
            "search_duration_ms IS NULL OR search_duration_ms >= 0",
            name="chk_search_duration",
        ),
    )

    def __repr__(self) -> str:
        """String representation of SearchQuery."""
        return (
            f"<SearchQuery(query_id={self.query_id}, "
            f"type={self.query_type}, tenant_id={self.tenant_id})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert SearchQuery to dictionary.

        Returns:
            Dictionary representation of the search query
        """
        return {
            "query_id": self.query_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "query_text": self.query_text,
            "query_type": self.query_type,
            "source_document_id": self.source_document_id,
            "filters_applied": self.filters_applied,
            "result_count": self.result_count,
            "search_duration_ms": self.search_duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
