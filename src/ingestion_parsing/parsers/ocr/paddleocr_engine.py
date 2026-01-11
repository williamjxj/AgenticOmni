"""PaddleOCR engine implementation.

Feature: 004-ocr-embedding-pipeline

PaddleOCR is the primary OCR engine for English and Chinese text extraction.
Provides high accuracy with multi-language support.
"""

import logging
from pathlib import Path
from typing import Any

from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine, OcrResult
from src.ingestion_parsing.services.ocr_exceptions import (
    OcrEngineNotAvailableError,
    OcrProcessingError,
)

logger = logging.getLogger(__name__)


class PaddleOcrEngine(BaseOcrEngine):
    """PaddleOCR implementation for text extraction.

    Supports English, Chinese, and many other languages with high accuracy.
    Uses GPU acceleration if available.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        use_gpu: bool = True,
        use_angle_cls: bool = True,
    ) -> None:
        """Initialize PaddleOCR engine.

        Args:
            languages: List of language codes (ISO 639-1)
            use_gpu: Whether to use GPU acceleration
            use_angle_cls: Whether to use angle classification for rotated text

        Raises:
            OcrEngineNotAvailableError: If PaddleOCR is not installed
        """
        super().__init__(languages)
        self.use_gpu = use_gpu
        self.use_angle_cls = use_angle_cls
        self._ocr = None

        # Initialize OCR engine
        try:
            from paddleocr import PaddleOCR

            # Map common language codes to PaddleOCR language codes
            lang_map = {
                "en": "en",
                "zh": "ch",  # Chinese
                "zh-CN": "ch",
                "zh-TW": "ch",
                "ja": "japan",
                "ko": "korean",
                "fr": "french",
                "de": "german",
                "es": "spanish",
            }

            # Use first language or default to English
            primary_lang = self.languages[0] if self.languages else "en"
            paddle_lang = lang_map.get(primary_lang, "en")

            logger.info(
                f"Initializing PaddleOCR with language={paddle_lang}, "
                f"use_gpu={use_gpu}, use_angle_cls={use_angle_cls}"
            )

            self._ocr = PaddleOCR(
                lang=paddle_lang,
                use_gpu=use_gpu,
                use_angle_cls=use_angle_cls,
                show_log=False,  # Suppress verbose logs
            )

            logger.info("PaddleOCR initialized successfully")

        except ImportError as e:
            logger.error(f"PaddleOCR not installed: {e}")
            raise OcrEngineNotAvailableError("paddleocr") from e
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise OcrEngineNotAvailableError(f"paddleocr: {e}") from e

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
            raise OcrEngineNotAvailableError("paddleocr")

        try:
            logger.debug(f"Extracting text from {image_path} (page {page_number})")

            # Run OCR
            result = self._ocr.ocr(image_path, cls=self.use_angle_cls)

            if not result or not result[0]:
                logger.warning(f"No text detected in {image_path}")
                return OcrResult(
                    text="",
                    confidence=0.0,
                    page_number=page_number,
                    bounding_boxes=[],
                    metadata={"engine": "paddleocr", "status": "no_text_detected"},
                )

            # Parse results
            texts = []
            confidences = []
            bounding_boxes = []

            for line in result[0]:
                if len(line) >= 2:
                    box = line[0]  # Bounding box coordinates
                    text_info = line[1]  # (text, confidence)

                    text = text_info[0]
                    confidence = text_info[1]

                    texts.append(text)
                    confidences.append(confidence)
                    bounding_boxes.append(
                        {
                            "box": box,
                            "text": text,
                            "confidence": confidence,
                        }
                    )

            # Combine texts with newlines
            full_text = "\n".join(texts)

            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(
                f"Extracted {len(texts)} text lines from {image_path} "
                f"with avg confidence {avg_confidence:.3f}"
            )

            return OcrResult(
                text=full_text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                page_number=page_number,
                metadata={
                    "engine": "paddleocr",
                    "num_lines": len(texts),
                    "use_gpu": self.use_gpu,
                },
            )

        except Exception as e:
            logger.error(f"PaddleOCR extraction failed for {image_path}: {e}")
            raise OcrProcessingError(0, f"PaddleOCR failed: {e}") from e

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
            raise OcrEngineNotAvailableError("paddleocr")

        try:
            from pdf2image import convert_from_path

            logger.info(f"Converting PDF to images: {pdf_path}")

            # Convert PDF to images
            images = convert_from_path(pdf_path)

            logger.info(f"Processing {len(images)} pages from {pdf_path}")

            results = []
            for page_num, image in enumerate(images, start=1):
                # Save image temporarily
                temp_image_path = f"/tmp/pdf_page_{page_num}.png"
                image.save(temp_image_path, "PNG")

                # Extract text from image
                ocr_result = self.extract_text(temp_image_path, page_number=page_num)
                results.append(ocr_result)

                # Clean up temp file
                Path(temp_image_path).unlink(missing_ok=True)

            logger.info(
                f"Extracted text from {len(results)} pages of {pdf_path}"
            )

            return results

        except ImportError as e:
            logger.error("pdf2image not installed")
            raise OcrProcessingError(0, "pdf2image required for PDF processing") from e
        except Exception as e:
            logger.error(f"PDF OCR extraction failed for {pdf_path}: {e}")
            raise OcrProcessingError(0, f"PDF OCR failed: {e}") from e

    def is_available(self) -> bool:
        """Check if PaddleOCR engine is available.

        Returns:
            True if engine is initialized and ready
        """
        return self._ocr is not None

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes.

        Returns:
            List of ISO 639-1 language codes
        """
        return [
            "en",  # English
            "zh",  # Chinese
            "zh-CN",  # Chinese Simplified
            "zh-TW",  # Chinese Traditional
            "ja",  # Japanese
            "ko",  # Korean
            "fr",  # French
            "de",  # German
            "es",  # Spanish
            "it",  # Italian
            "ru",  # Russian
            "ar",  # Arabic
        ]
