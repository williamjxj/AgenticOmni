"""Unit tests for OCR Service.

Feature: 004-ocr-embedding-pipeline
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from config.settings import Settings
from src.ingestion_parsing.parsers.ocr.base import OcrResult
from src.ingestion_parsing.services.ocr_exceptions import (
    DocumentAlreadyProcessedError,
    DocumentNotFoundError,
    OcrEngineNotAvailableError,
)
from src.ingestion_parsing.services.ocr_service import OcrService
from src.storage_indexing.models.document import Document, OcrStatus


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings."""
    settings = MagicMock(spec=Settings)
    settings.ocr_engine = "paddleocr"
    settings.ocr_languages = ["en"]
    return settings


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def ocr_service(mock_session: AsyncMock, mock_settings: Settings) -> OcrService:
    """Create OcrService instance with mocks."""
    return OcrService(mock_session, mock_settings)


class TestOcrService:
    """Test OcrService business logic."""

    @pytest.mark.asyncio
    async def test_process_document_not_found(
        self, ocr_service: OcrService, mock_session: AsyncMock
    ) -> None:
        """Test processing non-existent document raises error."""
        # Mock database query returning None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(DocumentNotFoundError) as exc_info:
            await ocr_service.process_document(document_id=999)

        assert exc_info.value.document_id == 999

    @pytest.mark.asyncio
    async def test_process_document_already_processed(
        self, ocr_service: OcrService, mock_session: AsyncMock
    ) -> None:
        """Test processing already completed document without force flag."""
        # Mock document that's already processed
        mock_document = MagicMock(spec=Document)
        mock_document.document_id = 1
        mock_document.ocr_status = OcrStatus.COMPLETED.value

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        mock_session.execute.return_value = mock_result

        with pytest.raises(DocumentAlreadyProcessedError) as exc_info:
            await ocr_service.process_document(document_id=1, force_reprocess=False)

        assert exc_info.value.document_id == 1

    @pytest.mark.asyncio
    @patch("src.ingestion_parsing.services.ocr_service.Path")
    @patch("src.ingestion_parsing.services.ocr_service.PaddleOcrEngine")
    async def test_process_document_success(
        self,
        mock_paddle: MagicMock,
        mock_path: MagicMock,
        ocr_service: OcrService,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful document processing."""
        # Mock document
        mock_document = MagicMock(spec=Document)
        mock_document.document_id = 1
        mock_document.ocr_status = OcrStatus.NOT_STARTED.value
        mock_document.storage_path = "/tmp/test_doc.pdf"
        mock_document.file_type = "application/pdf"

        # Mock file exists
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        mock_session.execute.return_value = mock_result

        # Mock OCR engine
        mock_engine_instance = MagicMock()
        mock_engine_instance.extract_from_pdf.return_value = [
            OcrResult(
                text="Page 1 content",
                confidence=0.95,
                page_number=1,
                language="en",
                metadata={"engine": "paddleocr"},
            ),
            OcrResult(
                text="Page 2 content",
                confidence=0.92,
                page_number=2,
                language="en",
                metadata={"engine": "paddleocr"},
            ),
        ]
        mock_paddle.return_value = mock_engine_instance

        # Process document
        result = await ocr_service.process_document(document_id=1)

        # Assertions
        assert result["document_id"] == 1
        assert result["ocr_status"] == OcrStatus.COMPLETED.value
        assert result["pages_processed"] == 2
        assert result["confidence_score"] == pytest.approx(0.935, rel=0.01)
        assert "processing_time_ms" in result

        # Verify document status updated
        assert mock_document.ocr_status == OcrStatus.COMPLETED.value
        assert mock_document.page_count == 2
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_document_text(
        self, ocr_service: OcrService, mock_session: AsyncMock
    ) -> None:
        """Test retrieving full document text."""
        # Mock extracted text repository
        ocr_service.extracted_text_repo.get_full_document_text = AsyncMock(
            return_value="Full document text content"
        )

        result = await ocr_service.get_document_text(document_id=1)

        assert result == "Full document text content"
        ocr_service.extracted_text_repo.get_full_document_text.assert_called_once_with(
            1
        )

    @pytest.mark.asyncio
    async def test_get_ocr_status(
        self, ocr_service: OcrService, mock_session: AsyncMock
    ) -> None:
        """Test getting OCR status for a document."""
        # Mock document with OCR info
        mock_document = MagicMock(spec=Document)
        mock_document.document_id = 1
        mock_document.ocr_status = OcrStatus.COMPLETED.value
        mock_document.ocr_confidence = 0.93
        mock_document.page_count = 5
        mock_document.ocr_engine_used = "paddleocr"
        mock_document.language_detected = "en"
        mock_document.has_scanned_content = True

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_document
        mock_session.execute.return_value = mock_result

        status = await ocr_service.get_ocr_status(document_id=1)

        assert status["document_id"] == 1
        assert status["ocr_status"] == OcrStatus.COMPLETED.value
        assert status["ocr_confidence"] == 0.93
        assert status["page_count"] == 5
        assert status["ocr_engine_used"] == "paddleocr"
        assert status["language_detected"] == "en"
        assert status["has_scanned_content"] is True

    @pytest.mark.asyncio
    @patch("src.ingestion_parsing.services.ocr_service.PaddleOcrEngine")
    def test_get_ocr_engine_paddleocr(
        self, mock_paddle: MagicMock, ocr_service: OcrService
    ) -> None:
        """Test OCR engine selection - PaddleOCR."""
        mock_engine = MagicMock()
        mock_paddle.return_value = mock_engine

        engine = ocr_service._get_ocr_engine(languages=["en", "zh"])

        assert engine == mock_engine
        mock_paddle.assert_called_once_with(languages=["en", "zh"])

    @pytest.mark.asyncio
    @patch("src.ingestion_parsing.services.ocr_service.TesseractEngine")
    @patch(
        "src.ingestion_parsing.services.ocr_service.PaddleOcrEngine",
        side_effect=OcrEngineNotAvailableError("paddleocr"),
    )
    def test_get_ocr_engine_fallback_to_tesseract(
        self,
        mock_paddle: MagicMock,
        mock_tesseract: MagicMock,
        ocr_service: OcrService,
    ) -> None:
        """Test OCR engine fallback from PaddleOCR to Tesseract."""
        mock_engine = MagicMock()
        mock_tesseract.return_value = mock_engine

        engine = ocr_service._get_ocr_engine(languages=["en"])

        assert engine == mock_engine
        mock_paddle.assert_called_once()
        mock_tesseract.assert_called_once_with(languages=["en"])

    @pytest.mark.asyncio
    @patch(
        "src.ingestion_parsing.services.ocr_service.TesseractEngine",
        side_effect=OcrEngineNotAvailableError("tesseract"),
    )
    @patch(
        "src.ingestion_parsing.services.ocr_service.PaddleOcrEngine",
        side_effect=OcrEngineNotAvailableError("paddleocr"),
    )
    def test_get_ocr_engine_no_engine_available(
        self,
        mock_paddle: MagicMock,
        mock_tesseract: MagicMock,
        ocr_service: OcrService,
    ) -> None:
        """Test error when no OCR engine is available."""
        with pytest.raises(OcrEngineNotAvailableError) as exc_info:
            ocr_service._get_ocr_engine()

        assert "No OCR engine available" in str(exc_info.value)
