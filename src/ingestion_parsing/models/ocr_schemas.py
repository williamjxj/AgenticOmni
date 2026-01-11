"""Pydantic schemas for OCR operations.

Feature: 004-ocr-embedding-pipeline
Task: T026
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class OcrExtractionRequest(BaseModel):
    """Request schema for OCR extraction API.

    Attributes:
        document_id: Foreign key to documents table
        force_reprocess: Force OCR even if already processed
        ocr_languages: Optional list of language codes (ISO 639-1)
    """

    document_id: int = Field(..., gt=0, description="Document ID to process")
    force_reprocess: bool = Field(
        default=False, description="Force reprocess even if already completed"
    )
    ocr_languages: list[str] | None = Field(
        default=None,
        description="Language codes for OCR (e.g., ['en', 'zh'])",
        max_length=10,
    )

    @field_validator("ocr_languages")
    @classmethod
    def validate_languages(cls, v: list[str] | None) -> list[str] | None:
        """Validate language codes are 2-character ISO 639-1 codes.

        Args:
            v: List of language codes

        Returns:
            Validated language codes

        Raises:
            ValueError: If language code is invalid
        """
        if v is not None:
            for lang in v:
                if len(lang) != 2:
                    raise ValueError(f"Language code must be 2 characters: {lang}")
        return v


class OcrExtractionResponse(BaseModel):
    """Response schema for OCR extraction API.

    Attributes:
        document_id: Document ID that was processed
        ocr_status: Status (not_started, in_progress, completed, failed)
        confidence_score: Average confidence score (0.0-1.0)
        pages_processed: Number of pages processed
        extraction_method: Method used (paddleocr, tesseract)
        language_detected: Detected language (ISO 639-1)
        processing_time_ms: Processing time in milliseconds
        created_at: When processing started
    """

    document_id: int
    ocr_status: str
    confidence_score: float | None = None
    pages_processed: int | None = None
    extraction_method: str | None = None
    language_detected: str | None = None
    processing_time_ms: int | None = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ExtractedTextResponse(BaseModel):
    """Response schema for extracted text.

    Attributes:
        extracted_text_id: Unique identifier
        document_id: Foreign key to documents
        page_number: Page number (1-indexed)
        extraction_method: Method used
        text_content: Extracted text
        confidence_score: OCR confidence score
        character_count: Number of characters
        created_at: Extraction timestamp
    """

    extracted_text_id: int
    document_id: int
    page_number: int
    extraction_method: str
    text_content: str
    confidence_score: float | None = None
    character_count: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class OcrBatchRequest(BaseModel):
    """Request schema for batch OCR processing.

    Attributes:
        document_ids: List of document IDs to process
        force_reprocess: Force OCR even if already processed
        ocr_languages: Optional list of language codes
    """

    document_ids: list[int] = Field(..., min_length=1, max_length=100)
    force_reprocess: bool = Field(default=False)
    ocr_languages: list[str] | None = Field(default=None)


class OcrBatchResponse(BaseModel):
    """Response schema for batch OCR processing.

    Attributes:
        job_id: Processing job ID for tracking
        total_documents: Total documents queued
        estimated_time_minutes: Estimated processing time
    """

    job_id: int
    total_documents: int
    estimated_time_minutes: int | None = None
