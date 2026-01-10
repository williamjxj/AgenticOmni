"""Integration tests for processing job status API."""

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models import ProcessingStatus


@pytest.mark.asyncio
async def test_get_job_status_endpoint_contract(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test GET /api/v1/processing/jobs/{job_id} endpoint contract."""
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    from src.storage_indexing.repositories.job_repository import JobRepository
    
    # Setup: Create a document and job
    document_repo = DocumentRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
        started_by=1,
    )
    
    # Test: Get job status
    response = await client.get(f"/api/v1/processing/jobs/{job.job_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "job_id" in data
    assert "document_id" in data
    assert "status" in data
    assert "job_type" in data
    assert "progress_percent" in data
    assert "created_at" in data
    
    assert data["job_id"] == job.job_id
    assert data["document_id"] == document.document_id
    assert data["status"] == ProcessingStatus.PENDING.value


@pytest.mark.asyncio
async def test_get_job_status_not_found(client: AsyncClient) -> None:
    """Test job status endpoint returns 404 for non-existent job."""
    response = await client.get("/api/v1/processing/jobs/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["type"] == "not_found"


@pytest.mark.asyncio
async def test_job_status_polling_workflow(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test job status polling workflow: upload → poll → verify completion.
    
    This simulates a client uploading a document and polling for completion.
    """
    from src.ingestion_parsing.services.parsing_service import ParsingService
    from src.storage_indexing.repositories.chunk_repository import ChunkRepository
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    from src.storage_indexing.repositories.job_repository import JobRepository
    
    # Setup repositories
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    # Create document and job
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_polling",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
        started_by=1,
    )
    
    # Initial status should be pending
    response = await client.get(f"/api/v1/processing/jobs/{job.job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ProcessingStatus.PENDING.value
    assert data["progress_percent"] == 0
    
    # Start processing (simulate async task)
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    await parsing_service.parse_document(document.document_id)
    
    # Poll until complete
    max_attempts = 10
    for attempt in range(max_attempts):
        response = await client.get(f"/api/v1/processing/jobs/{job.job_id}")
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] == ProcessingStatus.COMPLETED.value:
            assert data["progress_percent"] == 100
            break
        
        await asyncio.sleep(0.5)
    
    # Verify final status
    assert data["status"] == ProcessingStatus.COMPLETED.value
    assert data["progress_percent"] == 100


@pytest.mark.asyncio
async def test_job_status_with_progress_updates(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test that job status includes progress updates at each stage."""
    from src.storage_indexing.repositories.job_repository import JobRepository
    
    job_repo = JobRepository(db_session)
    
    # Create a job
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    
    document_repo = DocumentRepository(db_session)
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_progress",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
    )
    
    # Update progress to 50%
    await job_repo.update_status(
        job_id=job.job_id,
        status=ProcessingStatus.PROCESSING.value,
        progress_percent=50,
    )
    
    # Check status
    response = await client.get(f"/api/v1/processing/jobs/{job.job_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == ProcessingStatus.PROCESSING.value
    assert data["progress_percent"] == 50


@pytest.mark.asyncio
async def test_retry_failed_job(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test retrying a failed job."""
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    from src.storage_indexing.repositories.job_repository import JobRepository
    
    document_repo = DocumentRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_retry",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
    )
    
    # Mark job as failed
    await job_repo.update_status(
        job_id=job.job_id,
        status=ProcessingStatus.FAILED.value,
        error_message="Test failure",
    )
    
    # Retry the job
    response = await client.post(f"/api/v1/processing/jobs/{job.job_id}/retry")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_cancel_job(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test cancelling a processing job."""
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    from src.storage_indexing.repositories.job_repository import JobRepository
    
    document_repo = DocumentRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_cancel",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
    )
    
    # Cancel the job
    response = await client.post(f"/api/v1/processing/jobs/{job.job_id}/cancel")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_get_document_with_processing_status(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test GET /api/v1/documents/{document_id} includes processing status."""
    from src.storage_indexing.repositories.document_repository import DocumentRepository
    
    document_repo = DocumentRepository(db_session)
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_doc_status",
    )
    
    # Get document details
    response = await client.get(f"/api/v1/documents/{document.document_id}?tenant_id=1")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["document_id"] == document.document_id
    assert data["processing_status"] == ProcessingStatus.UPLOADED.value
    assert "filename" in data
    assert "file_size" in data
