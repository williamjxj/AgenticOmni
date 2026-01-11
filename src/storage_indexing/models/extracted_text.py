"""ExtractedText model for OCR and native text extraction.

Feature: 004-ocr-embedding-pipeline
Task: T016
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base


class ExtractionMethod(str, Enum):
    """Text extraction method enumeration."""

    NATIVE = "native"
    OCR_PADDLEOCR = "ocr_paddleocr"
    OCR_TESSERACT = "ocr_tesseract"


class ExtractedText(Base):
    """ExtractedText entity for storing OCR and native text extraction.

    Each ExtractedText record represents text extracted from a specific page
    of a document, along with metadata about the extraction process.

    Attributes:
        extracted_text_id: Primary key, unique identifier
        document_id: Foreign key to documents table
        page_number: Page number (1-indexed)
        extraction_method: Method used (native, ocr_paddleocr, ocr_tesseract)
        text_content: Extracted text content
        confidence_score: OCR confidence score (0.0-1.0), NULL for native extraction
        bounding_boxes: Bounding box coordinates for OCR text regions (JSONB)
        structural_metadata: Document structure info (headings, paragraphs, tables) (JSONB)
        character_count: Number of characters in text_content
        created_at: Extraction timestamp
    """

    __tablename__ = "extracted_texts"

    extracted_text_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique identifier for extracted text",
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to documents table",
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Page number (1-indexed)",
    )

    extraction_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Method used: native, ocr_paddleocr, ocr_tesseract",
    )

    text_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Extracted text content",
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="OCR confidence score (0.0-1.0), NULL for native extraction",
    )

    bounding_boxes: Mapped[dict[str, Any] | None] = mapped_column(
        postgresql.JSONB,
        nullable=True,
        comment="Bounding box coordinates for OCR text regions",
    )

    structural_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        postgresql.JSONB,
        nullable=True,
        comment="Headings, paragraphs, tables, lists detected",
    )

    character_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of characters in text_content",
    )

    created_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default="NOW()",
        comment="Extraction timestamp",
    )

    # Add table args for check constraints
    __table_args__ = (
        CheckConstraint("page_number >= 1", name="chk_page_number_positive"),
        CheckConstraint(
            "extraction_method IN ('native', 'ocr_paddleocr', 'ocr_tesseract')",
            name="chk_extraction_method",
        ),
        CheckConstraint("text_content != ''", name="chk_text_not_empty"),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="chk_confidence_score",
        ),
        CheckConstraint("character_count > 0", name="chk_character_count"),
    )

    def __repr__(self) -> str:
        """String representation of ExtractedText."""
        return (
            f"<ExtractedText(id={self.extracted_text_id}, "
            f"document_id={self.document_id}, page={self.page_number}, "
            f"method={self.extraction_method})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedText to dictionary.

        Returns:
            Dictionary representation of the extracted text
        """
        return {
            "extracted_text_id": self.extracted_text_id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "extraction_method": self.extraction_method,
            "text_content": self.text_content,
            "confidence_score": self.confidence_score,
            "bounding_boxes": self.bounding_boxes,
            "structural_metadata": self.structural_metadata,
            "character_count": self.character_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
