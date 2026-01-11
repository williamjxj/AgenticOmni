"""OCR Service for document text extraction.

Feature: 004-ocr-embedding-pipeline

Core service that orchestrates OCR processing, engine selection,
and database persistence.
"""

import logging
import time
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine, OcrResult
from src.ingestion_parsing.parsers.ocr.paddleocr_engine import PaddleOcrEngine
from src.ingestion_parsing.parsers.ocr.tesseract_engine import TesseractEngine
from src.ingestion_parsing.services.ocr_exceptions import (
    DocumentAlreadyProcessedError,
    DocumentNotFoundError,
    OcrEngineNotAvailableError,
    OcrProcessingError,
)
from src.storage_indexing.models.document import Document, OcrStatus
from src.storage_indexing.models.extracted_text import ExtractedText
from src.storage_indexing.repositories.extracted_text_repository import (
    ExtractedTextRepository,
)

logger = logging.getLogger(__name__)


class OcrService:
    """Service for OCR text extraction operations.

    Handles engine selection, document processing, and result persistence.
    
    Attributes:
        session: Async database session
        settings: Application settings
        extracted_text_repo: Repository for extracted text data
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Initialize OCR service.

        Args:
            session: Async database session
            settings: Application settings
        """
        self.session = session
        self.settings = settings
        self.extracted_text_repo = ExtractedTextRepository(session)
        self._ocr_engine: BaseOcrEngine | None = None

    def _get_ocr_engine(self, languages: list[str] | None = None) -> BaseOcrEngine:
        """Get OCR engine instance.

        Args:
            languages: Optional list of language codes

        Returns:
            BaseOcrEngine instance

        Raises:
            OcrEngineNotAvailableError: If no OCR engine is available
        """
        if self._ocr_engine is not None:
            return self._ocr_engine

        # Use settings or fallback to English
        langs = languages or self.settings.ocr_languages or ["en"]

        # Try PaddleOCR first (primary engine)
        if self.settings.ocr_engine == "paddleocr":
            try:
                logger.info("Initializing PaddleOCR engine")
                self._ocr_engine = PaddleOcrEngine(languages=langs)
                return self._ocr_engine
            except OcrEngineNotAvailableError as e:
                logger.warning(f"PaddleOCR not available: {e}, trying Tesseract")

        # Fall back to Tesseract
        try:
            logger.info("Initializing Tesseract engine")
            self._ocr_engine = TesseractEngine(languages=langs)
            return self._ocr_engine
        except OcrEngineNotAvailableError as e:
            logger.error(f"Tesseract not available: {e}")
            raise OcrEngineNotAvailableError("No OCR engine available") from e

    async def process_document(
        self,
        document_id: int,
        force_reprocess: bool = False,
        languages: list[str] | None = None,
    ) -> dict[str, Any]:
        """Process a document with OCR.

        Args:
            document_id: Document ID to process
            force_reprocess: Force reprocessing even if already completed
            languages: Optional list of language codes

        Returns:
            Dictionary with processing results

        Raises:
            DocumentNotFoundError: If document not found
            DocumentAlreadyProcessedError: If already processed and force_reprocess=False
            OcrProcessingError: If OCR processing fails
        """
        start_time = time.time()

        # Fetch document
        from sqlalchemy import select

        stmt = select(Document).where(Document.document_id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise DocumentNotFoundError(document_id)

        # Check if already processed
        if document.ocr_status == OcrStatus.COMPLETED.value and not force_reprocess:
            raise DocumentAlreadyProcessedError(document_id)

        # Update status to in_progress
        document.ocr_status = OcrStatus.IN_PROGRESS.value
        await self.session.flush()

        try:
            # Get OCR engine
            ocr_engine = self._get_ocr_engine(languages)

            # Process document based on file type
            file_path = document.storage_path

            if not Path(file_path).exists():
                raise OcrProcessingError(
                    document_id, f"File not found: {file_path}"
                )

            logger.info(
                f"Processing document {document_id} with {ocr_engine.__class__.__name__}"
            )

            # Determine if scanned content
            # For MVP, assume PDF/images need OCR
            is_scanned = document.file_type.lower() in [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/tiff",
            ]

            document.has_scanned_content = is_scanned

            # Extract text
            if document.file_type == "application/pdf":
                ocr_results = ocr_engine.extract_from_pdf(file_path)
            else:
                # Single image
                ocr_result = ocr_engine.extract_text(file_path, page_number=1)
                ocr_results = [ocr_result]

            # Save extracted texts to database
            for ocr_result in ocr_results:
                await self.extracted_text_repo.create(
                    document_id=document_id,
                    page_number=ocr_result.page_number,
                    extraction_method=f"ocr_{ocr_engine.__class__.__name__.lower().replace('engine', '')}",
                    text_content=ocr_result.text,
                    confidence_score=ocr_result.confidence,
                    bounding_boxes={"boxes": ocr_result.bounding_boxes}
                    if ocr_result.bounding_boxes
                    else None,
                    structural_metadata=ocr_result.metadata,
                )

            # Calculate average confidence
            avg_confidence = (
                sum(r.confidence for r in ocr_results) / len(ocr_results)
                if ocr_results
                else 0.0
            )

            # Update document
            document.ocr_status = OcrStatus.COMPLETED.value
            document.ocr_confidence = avg_confidence
            document.page_count = len(ocr_results)
            document.ocr_engine_used = ocr_engine.__class__.__name__.lower().replace(
                "engine", ""
            )

            # Detect language from first page if available
            if ocr_results and ocr_results[0].language:
                document.language_detected = ocr_results[0].language

            await self.session.commit()

            processing_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Document {document_id} processed successfully in {processing_time_ms}ms. "
                f"Confidence: {avg_confidence:.3f}, Pages: {len(ocr_results)}"
            )

            return {
                "document_id": document_id,
                "ocr_status": OcrStatus.COMPLETED.value,
                "confidence_score": avg_confidence,
                "pages_processed": len(ocr_results),
                "extraction_method": document.ocr_engine_used,
                "language_detected": document.language_detected,
                "processing_time_ms": processing_time_ms,
            }

        except Exception as e:
            # Update status to failed
            document.ocr_status = OcrStatus.FAILED.value
            await self.session.commit()

            logger.error(f"OCR processing failed for document {document_id}: {e}")
            raise OcrProcessingError(document_id, str(e)) from e

    async def get_document_text(self, document_id: int) -> str:
        """Get full extracted text for a document.

        Args:
            document_id: Document ID

        Returns:
            Concatenated text from all pages

        Raises:
            DocumentNotFoundError: If document not found
            ValueError: If no extracted text available
        """
        return await self.extracted_text_repo.get_full_document_text(document_id)

    async def get_extracted_texts(self, document_id: int) -> list[ExtractedText]:
        """Get all extracted text records for a document.

        Args:
            document_id: Document ID

        Returns:
            List of ExtractedText instances
        """
        return await self.extracted_text_repo.get_by_document(document_id)

    async def get_ocr_status(self, document_id: int) -> dict[str, Any]:
        """Get OCR processing status for a document.

        Args:
            document_id: Document ID

        Returns:
            Dictionary with OCR status information

        Raises:
            DocumentNotFoundError: If document not found
        """
        from sqlalchemy import select

        stmt = select(Document).where(Document.document_id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise DocumentNotFoundError(document_id)

        return {
            "document_id": document_id,
            "ocr_status": document.ocr_status,
            "ocr_confidence": document.ocr_confidence,
            "page_count": document.page_count,
            "ocr_engine_used": document.ocr_engine_used,
            "language_detected": document.language_detected,
            "has_scanned_content": document.has_scanned_content,
        }
