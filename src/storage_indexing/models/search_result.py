"""SearchResult model for storing individual search results.

Feature: 004-ocr-embedding-pipeline
Task: T020
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base


class SearchResult(Base):
    """SearchResult entity for storing individual search results.

    Each SearchResult record represents a single result from a search operation,
    including the matching chunk, document, and similarity score.

    Attributes:
        result_id: Primary key, unique identifier
        query_id: Foreign key to search_queries table
        chunk_id: Foreign key to document_chunks table
        document_id: Foreign key to documents table
        similarity_score: Cosine similarity score (0.0-1.0)
        rank_position: Result position (1-based)
        result_snippet: Text snippet for preview
        created_at: When result was captured
    """

    __tablename__ = "search_results"

    result_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier",
    )

    query_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("search_queries.query_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Associated search query",
    )

    chunk_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document_chunks.chunk_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Matching chunk",
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Matching document",
    )

    similarity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Cosine similarity score",
    )

    rank_position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Result position (1-based)",
    )

    result_snippet: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Text snippet for preview",
    )

    created_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default="NOW()",
        comment="When result was captured",
    )

    # Add table args for check constraints
    __table_args__ = (
        CheckConstraint(
            "similarity_score >= 0 AND similarity_score <= 1",
            name="chk_similarity_score",
        ),
        CheckConstraint(
            "rank_position >= 1",
            name="chk_rank_position",
        ),
    )

    def __repr__(self) -> str:
        """String representation of SearchResult."""
        return (
            f"<SearchResult(result_id={self.result_id}, "
            f"query_id={self.query_id}, rank={self.rank_position}, "
            f"score={self.similarity_score:.3f})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert SearchResult to dictionary.

        Returns:
            Dictionary representation of the search result
        """
        return {
            "result_id": self.result_id,
            "query_id": self.query_id,
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "rank_position": self.rank_position,
            "result_snippet": self.result_snippet,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
