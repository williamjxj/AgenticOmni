"""Unit tests for OCR engines.

Feature: 004-ocr-embedding-pipeline
"""

import pytest
from unittest.mock import MagicMock, patch

from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine, OcrResult
from src.ingestion_parsing.parsers.ocr.paddleocr_engine import PaddleOcrEngine
from src.ingestion_parsing.parsers.ocr.tesseract_engine import TesseractEngine
from src.ingestion_parsing.services.ocr_exceptions import (
    OcrEngineNotAvailableError,
    OcrProcessingError,
)


class TestOcrResult:
    """Test OcrResult dataclass."""

    def test_ocr_result_creation(self) -> None:
        """Test creating OcrResult instance."""
        result = OcrResult(
            text="Sample text",
            confidence=0.95,
            bounding_boxes=[{"box": [0, 0, 100, 100]}],
            language="en",
            page_number=1,
            metadata={"engine": "paddleocr"},
        )

        assert result.text == "Sample text"
        assert result.confidence == 0.95
        assert result.page_number == 1
        assert result.language == "en"
        assert result.metadata["engine"] == "paddleocr"


class TestPaddleOcrEngine:
    """Test PaddleOCR engine implementation."""

    @patch("src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR")
    def test_initialization_success(self, mock_paddle: MagicMock) -> None:
        """Test successful PaddleOCR initialization."""
        mock_paddle.return_value = MagicMock()

        engine = PaddleOcrEngine(languages=["en"], use_gpu=False)

        assert engine.is_available()
        assert engine.languages == ["en"]
        assert not engine.use_gpu
        mock_paddle.assert_called_once()

    def test_initialization_failure(self) -> None:
        """Test PaddleOCR initialization failure when not installed."""
        with patch(
            "src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR",
            side_effect=ImportError("PaddleOCR not installed"),
        ):
            with pytest.raises(OcrEngineNotAvailableError) as exc_info:
                PaddleOcrEngine(languages=["en"])

            assert "paddleocr" in str(exc_info.value)

    @patch("src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR")
    def test_extract_text_success(self, mock_paddle: MagicMock) -> None:
        """Test successful text extraction from image."""
        # Mock OCR results
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.ocr.return_value = [
            [
                [
                    [[0, 0], [100, 0], [100, 50], [0, 50]],  # Bounding box
                    ("Hello World", 0.98),  # Text and confidence
                ],
                [
                    [[0, 60], [100, 60], [100, 110], [0, 110]],
                    ("Test Text", 0.95),
                ],
            ]
        ]
        mock_paddle.return_value = mock_ocr_instance

        engine = PaddleOcrEngine(languages=["en"], use_gpu=False)
        result = engine.extract_text("test_image.png", page_number=1)

        assert result.text == "Hello World\nTest Text"
        assert result.confidence == pytest.approx(0.965, rel=0.01)  # (0.98 + 0.95) / 2
        assert result.page_number == 1
        assert len(result.bounding_boxes) == 2

    @patch("src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR")
    def test_extract_text_no_text_detected(self, mock_paddle: MagicMock) -> None:
        """Test extraction when no text is detected."""
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.ocr.return_value = [[]]  # No text detected
        mock_paddle.return_value = mock_ocr_instance

        engine = PaddleOcrEngine(languages=["en"], use_gpu=False)
        result = engine.extract_text("blank_image.png")

        assert result.text == ""
        assert result.confidence == 0.0
        assert result.metadata["status"] == "no_text_detected"

    def test_supported_languages(self) -> None:
        """Test getting supported languages."""
        with patch("src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR"):
            engine = PaddleOcrEngine()
            languages = engine.get_supported_languages()

            assert "en" in languages
            assert "zh" in languages
            assert "ja" in languages
            assert len(languages) > 5


class TestTesseractEngine:
    """Test Tesseract OCR engine implementation."""

    @patch("src.ingestion_parsing.parsers.ocr.tesseract_engine.pytesseract")
    def test_initialization_success(self, mock_tesseract: MagicMock) -> None:
        """Test successful Tesseract initialization."""
        mock_tesseract.get_tesseract_version.return_value = "5.0.0"

        engine = TesseractEngine(languages=["en"])

        assert engine.is_available()
        assert engine.languages == ["en"]

    def test_initialization_failure(self) -> None:
        """Test Tesseract initialization failure when not installed."""
        with patch(
            "src.ingestion_parsing.parsers.ocr.tesseract_engine.pytesseract",
            side_effect=ImportError("pytesseract not installed"),
        ):
            with pytest.raises(OcrEngineNotAvailableError) as exc_info:
                TesseractEngine(languages=["en"])

            assert "tesseract" in str(exc_info.value)

    @patch("src.ingestion_parsing.parsers.ocr.tesseract_engine.pytesseract")
    @patch("src.ingestion_parsing.parsers.ocr.tesseract_engine.Image")
    def test_extract_text_success(
        self, mock_image: MagicMock, mock_tesseract: MagicMock
    ) -> None:
        """Test successful text extraction with Tesseract."""
        mock_tesseract.get_tesseract_version.return_value = "5.0.0"
        mock_tesseract.image_to_string.return_value = "Extracted text from image"
        mock_tesseract.image_to_data.return_value = {"conf": [85, 90, 88]}
        mock_tesseract.Output = MagicMock()
        mock_tesseract.Output.DICT = "dict"

        mock_img = MagicMock()
        mock_image.open.return_value = mock_img

        engine = TesseractEngine(languages=["en"])
        result = engine.extract_text("test_image.png")

        assert result.text == "Extracted text from image"
        assert result.confidence > 0.8
        assert result.metadata["engine"] == "tesseract"

    def test_supported_languages(self) -> None:
        """Test getting supported languages."""
        with patch("src.ingestion_parsing.parsers.ocr.tesseract_engine.pytesseract"):
            engine = TesseractEngine()
            languages = engine.get_supported_languages()

            assert "en" in languages
            assert len(languages) > 3


class TestBaseOcrEngine:
    """Test BaseOcrEngine abstract class."""

    def test_cannot_instantiate_directly(self) -> None:
        """Test that BaseOcrEngine cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseOcrEngine()  # type: ignore

    def test_repr(self) -> None:
        """Test string representation of OCR engine."""
        with patch("src.ingestion_parsing.parsers.ocr.paddleocr_engine.PaddleOCR"):
            engine = PaddleOcrEngine(languages=["en", "zh"])
            repr_str = repr(engine)

            assert "PaddleOcrEngine" in repr_str
            assert "languages" in repr_str
