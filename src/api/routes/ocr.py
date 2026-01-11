"""OCR API endpoints.

Feature: 004-ocr-embedding-pipeline
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from src.api.dependencies import get_db, get_settings
from src.ingestion_parsing.models.ocr_schemas import (
    ExtractedTextResponse,
    OcrExtractionRequest,
    OcrExtractionResponse,
)
from src.ingestion_parsing.services.ocr_exceptions import (
    DocumentAlreadyProcessedError,
    DocumentNotFoundError,
    OcrEngineNotAvailableError,
    OcrProcessingError,
)
from src.ingestion_parsing.services.ocr_service import OcrService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post(
    "/extract",
    response_model=OcrExtractionResponse,
    status_code=status.HTTP_200_OK,
)
async def extract_text(
    request: OcrExtractionRequest,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Extract text from a document using OCR.

    Processes the document with the configured OCR engine (PaddleOCR or Tesseract)
    and stores the extracted text in the database.

    Args:
        request: OCR extraction request with document_id and options
        session: Database session
        settings: Application settings

    Returns:
        OcrExtractionResponse with processing results

    Raises:
        HTTPException: For various error conditions
    """
    logger.info(f"OCR extraction request for document {request.document_id}")

    ocr_service = OcrService(session, settings)

    try:
        result = await ocr_service.process_document(
            document_id=request.document_id,
            force_reprocess=request.force_reprocess,
            languages=request.ocr_languages,
        )

        return OcrExtractionResponse(**result)

    except DocumentNotFoundError as e:
        logger.warning(f"Document not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {request.document_id} not found",
        ) from e

    except DocumentAlreadyProcessedError as e:
        logger.info(f"Document already processed: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document {request.document_id} already processed. Use force_reprocess=true to reprocess.",
        ) from e

    except OcrEngineNotAvailableError as e:
        logger.error(f"OCR engine not available: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OCR service unavailable: {e}",
        ) from e

    except OcrProcessingError as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {e.reason}",
        ) from e


@router.get(
    "/status/{document_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
)
async def get_ocr_status(
    document_id: int,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get OCR processing status for a document.

    Args:
        document_id: Document ID
        session: Database session
        settings: Application settings

    Returns:
        Dictionary with OCR status information

    Raises:
        HTTPException: If document not found
    """
    logger.info(f"OCR status request for document {document_id}")

    ocr_service = OcrService(session, settings)

    try:
        status_info = await ocr_service.get_ocr_status(document_id)
        return status_info

    except DocumentNotFoundError as e:
        logger.warning(f"Document not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        ) from e


@router.get(
    "/text/{document_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
)
async def get_extracted_text(
    document_id: int,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get extracted text for a document.

    Args:
        document_id: Document ID
        session: Database session
        settings: Application settings

    Returns:
        Dictionary with full text content

    Raises:
        HTTPException: If document not found or no text available
    """
    logger.info(f"Get extracted text for document {document_id}")

    ocr_service = OcrService(session, settings)

    try:
        full_text = await ocr_service.get_document_text(document_id)

        return {
            "document_id": document_id,
            "text_content": full_text,
            "character_count": len(full_text),
        }

    except DocumentNotFoundError as e:
        logger.warning(f"Document not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        ) from e

    except ValueError as e:
        logger.warning(f"No extracted text: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No extracted text available for document {document_id}",
        ) from e


@router.get(
    "/pages/{document_id}",
    response_model=list[ExtractedTextResponse],
    status_code=status.HTTP_200_OK,
)
async def get_extracted_pages(
    document_id: int,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get extracted text for all pages of a document.

    Args:
        document_id: Document ID
        session: Database session
        settings: Application settings

    Returns:
        List of ExtractedTextResponse for each page

    Raises:
        HTTPException: If document not found
    """
    logger.info(f"Get extracted pages for document {document_id}")

    ocr_service = OcrService(session, settings)

    try:
        extracted_texts = await ocr_service.get_extracted_texts(document_id)

        return [
            ExtractedTextResponse(
                extracted_text_id=et.extracted_text_id,
                document_id=et.document_id,
                page_number=et.page_number,
                extraction_method=et.extraction_method,
                text_content=et.text_content,
                confidence_score=et.confidence_score,
                character_count=et.character_count,
                created_at=et.created_at,
            )
            for et in extracted_texts
        ]

    except Exception as e:
        logger.error(f"Error getting extracted pages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get extracted pages: {e}",
        ) from e
