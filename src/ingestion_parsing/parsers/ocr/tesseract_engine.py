"""Tesseract OCR engine implementation (fallback).

Feature: 004-ocr-embedding-pipeline

Tesseract is used as a fallback when PaddleOCR is not available.
"""

import logging
from pathlib import Path

from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine, OcrResult
from src.ingestion_parsing.services.ocr_exceptions import (
    OcrEngineNotAvailableError,
    OcrProcessingError,
)

logger = logging.getLogger(__name__)


class TesseractEngine(BaseOcrEngine):
    """Tesseract OCR implementation for text extraction.

    Fallback engine when PaddleOCR is not available.
    """

    def __init__(self, languages: list[str] | None = None) -> None:
        """Initialize Tesseract engine.

        Args:
            languages: List of language codes (ISO 639-1)

        Raises:
            OcrEngineNotAvailableError: If Tesseract is not installed
        """
        super().__init__(languages)

        try:
            import pytesseract

            self.pytesseract = pytesseract
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except ImportError as e:
            logger.error(f"pytesseract not installed: {e}")
            raise OcrEngineNotAvailableError("tesseract") from e
        except Exception as e:
            logger.error(f"Tesseract not available: {e}")
            raise OcrEngineNotAvailableError(f"tesseract: {e}") from e

    def extract_text(self, image_path: str, page_number: int = 1) -> OcrResult:
        """Extract text from a single image.

        Args:
            image_path: Path to image file
            page_number: Page number (1-indexed)

        Returns:
            OcrResult with extracted text and metadata

        Raises:
            OcrProcessingError: If extraction fails
        """
        if not self.is_available():
            raise OcrEngineNotAvailableError("tesseract")

        try:
            from PIL import Image

            logger.debug(f"Extracting text with Tesseract from {image_path}")

            # Open image
            image = Image.open(image_path)

            # Convert language codes
            lang = "+".join(self.languages)

            # Extract text
            text = self.pytesseract.image_to_string(image, lang=lang)

            # Get confidence data (if available)
            try:
                data = self.pytesseract.image_to_data(
                    image, lang=lang, output_type=self.pytesseract.Output.DICT
                )
                confidences = [
                    conf for conf in data["conf"] if conf != -1
                ]
                avg_confidence = (
                    sum(confidences) / len(confidences) if confidences else 0.0
                ) / 100.0  # Tesseract returns 0-100
            except Exception as e:
                logger.warning(f"Could not get confidence data: {e}")
                avg_confidence = 0.5  # Default

            logger.info(
                f"Extracted text from {image_path} with confidence {avg_confidence:.3f}"
            )

            return OcrResult(
                text=text.strip(),
                confidence=avg_confidence,
                page_number=page_number,
                metadata={"engine": "tesseract", "language": lang},
            )

        except Exception as e:
            logger.error(f"Tesseract extraction failed for {image_path}: {e}")
            raise OcrProcessingError(0, f"Tesseract failed: {e}") from e

    def extract_from_pdf(self, pdf_path: str) -> list[OcrResult]:
        """Extract text from all pages of a PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of OcrResult, one per page

        Raises:
            OcrProcessingError: If extraction fails
        """
        if not self.is_available():
            raise OcrEngineNotAvailableError("tesseract")

        try:
            from pdf2image import convert_from_path

            logger.info(f"Converting PDF to images: {pdf_path}")

            # Convert PDF to images
            images = convert_from_path(pdf_path)

            logger.info(f"Processing {len(images)} pages with Tesseract")

            results = []
            for page_num, image in enumerate(images, start=1):
                # Save image temporarily
                temp_image_path = f"/tmp/pdf_page_{page_num}.png"
                image.save(temp_image_path, "PNG")

                # Extract text
                ocr_result = self.extract_text(temp_image_path, page_number=page_num)
                results.append(ocr_result)

                # Clean up
                Path(temp_image_path).unlink(missing_ok=True)

            logger.info(f"Extracted text from {len(results)} pages")

            return results

        except ImportError as e:
            logger.error("pdf2image not installed")
            raise OcrProcessingError(0, "pdf2image required") from e
        except Exception as e:
            logger.error(f"Tesseract PDF extraction failed: {e}")
            raise OcrProcessingError(0, f"PDF OCR failed: {e}") from e

    def is_available(self) -> bool:
        """Check if Tesseract engine is available.

        Returns:
            True if engine is ready
        """
        try:
            self.pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes
        """
        return [
            "en",  # English
            "chi_sim",  # Chinese Simplified
            "chi_tra",  # Chinese Traditional
            "jpn",  # Japanese
            "kor",  # Korean
            "fra",  # French
            "deu",  # German
            "spa",  # Spanish
        ]
