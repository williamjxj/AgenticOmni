"""OCR engine implementations.

Feature: 004-ocr-embedding-pipeline
"""

from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine, OcrResult
from src.ingestion_parsing.parsers.ocr.paddleocr_engine import PaddleOcrEngine
from src.ingestion_parsing.parsers.ocr.tesseract_engine import TesseractEngine

__all__ = [
    "BaseOcrEngine",
    "OcrResult",
    "PaddleOcrEngine",
    "TesseractEngine",
]
