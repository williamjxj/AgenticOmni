"""Repository for ExtractedText data access.

Feature: 004-ocr-embedding-pipeline
Task: T022
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.extracted_text import ExtractedText


class ExtractedTextRepository:
    """Repository for ExtractedText data access operations.

    Handles database operations for extracted text records, including
    creating, retrieving, and querying extracted text from documents.

    Attributes:
        session: Async SQLAlchemy database session
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ExtractedTextRepository with database session.

        Args:
            session: Async SQLAlchemy database session
        """
        self.session = session

    async def create(
        self,
        document_id: int,
        page_number: int,
        extraction_method: str,
        text_content: str,
        confidence_score: float | None = None,
        bounding_boxes: dict[str, Any] | None = None,
        structural_metadata: dict[str, Any] | None = None,
    ) -> ExtractedText:
        """Create a new extracted text record.

        Args:
            document_id: Foreign key to documents table
            page_number: Page number (1-indexed)
            extraction_method: Method used (native, ocr_paddleocr, ocr_tesseract)
            text_content: Extracted text content
            confidence_score: Optional OCR confidence score (0.0-1.0)
            bounding_boxes: Optional bounding box coordinates (JSONB)
            structural_metadata: Optional document structure info (JSONB)

        Returns:
            Created ExtractedText instance

        Raises:
            ValueError: If text_content is empty
            SQLAlchemyError: For database errors
        """
        if not text_content or not text_content.strip():
            raise ValueError("text_content cannot be empty")

        extracted_text = ExtractedText(
            document_id=document_id,
            page_number=page_number,
            extraction_method=extraction_method,
            text_content=text_content,
            confidence_score=confidence_score,
            bounding_boxes=bounding_boxes,
            structural_metadata=structural_metadata,
            character_count=len(text_content),
        )

        self.session.add(extracted_text)
        await self.session.flush()
        await self.session.refresh(extracted_text)

        return extracted_text

    async def get_by_id(self, extracted_text_id: int) -> ExtractedText | None:
        """Retrieve extracted text by ID.

        Args:
            extracted_text_id: Unique identifier

        Returns:
            ExtractedText instance if found, None otherwise
        """
        stmt = select(ExtractedText).where(
            ExtractedText.extracted_text_id == extracted_text_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_document(self, document_id: int) -> list[ExtractedText]:
        """Retrieve all extracted texts for a document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            List of ExtractedText instances ordered by page_number
        """
        stmt = (
            select(ExtractedText)
            .where(ExtractedText.document_id == document_id)
            .order_by(ExtractedText.page_number)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_document_page(
        self, document_id: int, page_number: int
    ) -> ExtractedText | None:
        """Retrieve extracted text for a specific document page.

        Args:
            document_id: Foreign key to documents table
            page_number: Page number (1-indexed)

        Returns:
            ExtractedText instance if found, None otherwise
        """
        stmt = select(ExtractedText).where(
            ExtractedText.document_id == document_id,
            ExtractedText.page_number == page_number,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_extraction_method(
        self, extraction_method: str
    ) -> list[ExtractedText]:
        """Retrieve all extracted texts by extraction method.

        Args:
            extraction_method: Method used (native, ocr_paddleocr, ocr_tesseract)

        Returns:
            List of ExtractedText instances
        """
        stmt = select(ExtractedText).where(
            ExtractedText.extraction_method == extraction_method
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_full_document_text(self, document_id: int) -> str:
        """Retrieve and concatenate all extracted text for a document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            Concatenated text content from all pages

        Raises:
            ValueError: If no extracted text found for document
        """
        extracted_texts = await self.get_by_document(document_id)

        if not extracted_texts:
            raise ValueError(f"No extracted text found for document {document_id}")

        return "\n\n".join(et.text_content for et in extracted_texts)

    async def delete_by_document(self, document_id: int) -> int:
        """Delete all extracted texts for a document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            Number of records deleted
        """
        extracted_texts = await self.get_by_document(document_id)
        count = len(extracted_texts)

        for extracted_text in extracted_texts:
            await self.session.delete(extracted_text)

        await self.session.flush()
        return count

    async def count_by_document(self, document_id: int) -> int:
        """Count extracted text records for a document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            Number of extracted text records
        """
        extracted_texts = await self.get_by_document(document_id)
        return len(extracted_texts)

    async def get_avg_confidence_by_document(self, document_id: int) -> float | None:
        """Calculate average OCR confidence for a document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            Average confidence score (0.0-1.0), None if no scores available
        """
        extracted_texts = await self.get_by_document(document_id)

        # Filter out None confidence scores (native extraction)
        scores = [
            et.confidence_score
            for et in extracted_texts
            if et.confidence_score is not None
        ]

        if not scores:
            return None

        return sum(scores) / len(scores)
