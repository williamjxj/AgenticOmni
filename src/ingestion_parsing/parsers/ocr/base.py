"""Base OCR engine interface.

Feature: 004-ocr-embedding-pipeline
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class OcrResult:
    """Result from OCR processing.

    Attributes:
        text: Extracted text content
        confidence: Confidence score (0.0-1.0)
        bounding_boxes: Optional bounding box coordinates
        language: Detected language code
        page_number: Page number (1-indexed)
        metadata: Additional metadata from OCR engine
    """

    text: str
    confidence: float
    bounding_boxes: list[dict[str, Any]] | None = None
    language: str | None = None
    page_number: int = 1
    metadata: dict[str, Any] | None = None


class BaseOcrEngine(ABC):
    """Abstract base class for OCR engines.

    Defines the interface that all OCR engines must implement.
    """

    def __init__(self, languages: list[str] | None = None) -> None:
        """Initialize OCR engine with language support.

        Args:
            languages: List of language codes (ISO 639-1) to support
        """
        self.languages = languages or ["en"]

    @abstractmethod
    def extract_text(self, image_path: str, page_number: int = 1) -> OcrResult:
        """Extract text from a single image or page.

        Args:
            image_path: Path to image file
            page_number: Page number (1-indexed)

        Returns:
            OcrResult with extracted text and metadata

        Raises:
            OcrProcessingError: If extraction fails
        """
        pass

    @abstractmethod
    def extract_from_pdf(self, pdf_path: str) -> list[OcrResult]:
        """Extract text from all pages of a PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of OcrResult, one per page

        Raises:
            OcrProcessingError: If extraction fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if OCR engine is available and configured.

        Returns:
            True if engine is available, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes
        """
        pass

    def __repr__(self) -> str:
        """String representation of OCR engine."""
        return f"<{self.__class__.__name__}(languages={self.languages})>"
