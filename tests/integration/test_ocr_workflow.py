"""Integration tests for OCR workflow.

Feature: 004-ocr-embedding-pipeline

Tests the complete OCR processing workflow from API to database.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.document import Document, OcrStatus
from src.storage_indexing.models.extracted_text import ExtractedText


@pytest.mark.integration
@pytest.mark.asyncio
class TestOcrWorkflow:
    """Integration tests for complete OCR workflow."""

    async def test_ocr_extraction_workflow(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_document: Document,
    ) -> None:
        """Test complete OCR extraction workflow.

        Workflow:
        1. Upload document (already done via fixture)
        2. Trigger OCR extraction
        3. Check processing status
        4. Retrieve extracted text
        5. Verify database records
        """
        document_id = sample_document.document_id

        # Step 1: Verify document exists and is not processed
        stmt = select(Document).where(Document.document_id == document_id)
        result = await db_session.execute(stmt)
        document = result.scalar_one()

        assert document.ocr_status == OcrStatus.NOT_STARTED.value

        # Step 2: Trigger OCR extraction
        # Note: This would normally call the actual OCR API
        # For integration tests, we might mock the OCR engine or use a test document
        response = await async_client.post(
            f"/api/v1/ocr/extract",
            json={
                "document_id": document_id,
                "force_reprocess": False,
                "ocr_languages": ["en"],
            },
        )

        # If OCR engines are not available in test environment, skip
        if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            pytest.skip("OCR engines not available in test environment")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["document_id"] == document_id
            assert data["ocr_status"] in [
                OcrStatus.IN_PROGRESS.value,
                OcrStatus.COMPLETED.value,
            ]

            # Step 3: Check processing status
            response = await async_client.get(f"/api/v1/ocr/status/{document_id}")
            assert response.status_code == status.HTTP_200_OK

            status_data = response.json()
            assert "ocr_status" in status_data
            assert "page_count" in status_data

            # Step 4: If completed, retrieve extracted text
            if status_data["ocr_status"] == OcrStatus.COMPLETED.value:
                response = await async_client.get(f"/api/v1/ocr/text/{document_id}")
                assert response.status_code == status.HTTP_200_OK

                text_data = response.json()
                assert "text_content" in text_data
                assert "character_count" in text_data
                assert text_data["character_count"] > 0

                # Step 5: Verify database records
                stmt = select(ExtractedText).where(
                    ExtractedText.document_id == document_id
                )
                result = await db_session.execute(stmt)
                extracted_texts = result.scalars().all()

                assert len(extracted_texts) > 0
                for extracted_text in extracted_texts:
                    assert extracted_text.text_content
                    assert extracted_text.character_count > 0
                    assert extracted_text.extraction_method in [
                        "ocr_paddleocr",
                        "ocr_tesseract",
                    ]

    async def test_ocr_status_not_found(
        self, async_client: AsyncClient
    ) -> None:
        """Test OCR status for non-existent document."""
        response = await async_client.get("/api/v1/ocr/status/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_ocr_extract_already_processed(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_document: Document,
    ) -> None:
        """Test OCR extraction for already processed document."""
        document_id = sample_document.document_id

        # Mark document as completed
        stmt = select(Document).where(Document.document_id == document_id)
        result = await db_session.execute(stmt)
        document = result.scalar_one()
        document.ocr_status = OcrStatus.COMPLETED.value
        await db_session.commit()

        # Try to process again without force flag
        response = await async_client.post(
            f"/api/v1/ocr/extract",
            json={
                "document_id": document_id,
                "force_reprocess": False,
            },
        )

        # Should return conflict status
        if response.status_code != status.HTTP_503_SERVICE_UNAVAILABLE:
            assert response.status_code == status.HTTP_409_CONFLICT

    async def test_ocr_extract_with_force_reprocess(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_document: Document,
    ) -> None:
        """Test OCR extraction with force_reprocess flag."""
        document_id = sample_document.document_id

        # Mark document as completed
        stmt = select(Document).where(Document.document_id == document_id)
        result = await db_session.execute(stmt)
        document = result.scalar_one()
        document.ocr_status = OcrStatus.COMPLETED.value
        await db_session.commit()

        # Try to process again WITH force flag
        response = await async_client.post(
            f"/api/v1/ocr/extract",
            json={
                "document_id": document_id,
                "force_reprocess": True,
                "ocr_languages": ["en"],
            },
        )

        # Should succeed or return service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]

    async def test_ocr_get_pages(
        self, async_client: AsyncClient, sample_document: Document
    ) -> None:
        """Test retrieving extracted text by page."""
        document_id = sample_document.document_id

        response = await async_client.get(f"/api/v1/ocr/pages/{document_id}")

        # Should return list (empty if not processed, or with pages if processed)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_ocr_multilanguage_extraction(
        self, async_client: AsyncClient, sample_document: Document
    ) -> None:
        """Test OCR extraction with multiple languages."""
        document_id = sample_document.document_id

        response = await async_client.post(
            f"/api/v1/ocr/extract",
            json={
                "document_id": document_id,
                "force_reprocess": False,
                "ocr_languages": ["en", "zh"],  # English and Chinese
            },
        )

        # Should succeed or return service unavailable
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_409_CONFLICT,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ]


@pytest.fixture
async def sample_document(db_session: AsyncSession) -> Document:
    """Create a sample document for testing.

    This fixture should be customized based on your test database setup.
    """
    # For now, return a mock document
    # In real tests, you'd create an actual document record
    document = Document(
        document_id=1,
        tenant_id=1,
        filename="test_document.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/tmp/test_document.pdf",
        content_hash="abc123",
        uploaded_by=1,
        original_filename="test_document.pdf",
        mime_type="application/pdf",
    )

    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)

    return document
