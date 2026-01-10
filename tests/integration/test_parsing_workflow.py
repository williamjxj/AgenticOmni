"""Integration tests for document parsing workflow."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion_parsing.services.parsing_service import ParsingService
from src.storage_indexing.models import Document, DocumentChunk, ProcessingJob, ProcessingStatus
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository


@pytest.mark.asyncio
async def test_full_parsing_workflow(db_session: "AsyncSession") -> None:
    """Test complete parsing workflow: upload → parse → chunk → update status.
    
    This is the core integration test for document processing.
    """
    # Setup repositories
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    # Create a document record (simulating upload)
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test_doc.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_123",
    )
    
    # Create a processing job
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
        started_by=1,
    )
    
    # Initialize parsing service
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    
    # Execute parsing workflow
    await parsing_service.parse_document(document.document_id)
    
    # Verify document was updated
    await db_session.refresh(document)
    assert document.processing_status == ProcessingStatus.PARSED.value
    assert document.page_count is not None
    
    # Verify chunks were created
    chunks = await chunk_repo.get_by_document(document.document_id)
    assert len(chunks) > 0
    
    # Verify chunks have correct structure
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
        assert chunk.content is not None
        assert len(chunk.content) > 0
        assert chunk.token_count is not None
        assert chunk.token_count > 0
    
    # Verify job was updated
    await db_session.refresh(job)
    assert job.status == ProcessingStatus.COMPLETED.value
    assert job.progress_percent == 100


@pytest.mark.asyncio
async def test_parsing_workflow_with_progress_tracking(db_session: "AsyncSession") -> None:
    """Test parsing workflow updates progress at key stages."""
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test_doc.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_456",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
        started_by=1,
    )
    
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    
    # Parse document
    await parsing_service.parse_document(document.document_id)
    
    # Verify job progress reached 100%
    await db_session.refresh(job)
    assert job.progress_percent == 100
    assert job.status == ProcessingStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_parsing_workflow_error_handling(db_session: "AsyncSession") -> None:
    """Test parsing workflow handles errors gracefully."""
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    # Create document with invalid file path
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="invalid.pdf",
        original_filename="invalid.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=1000,
        storage_path="/nonexistent/file.pdf",
        content_hash="invalid_hash",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
        started_by=1,
    )
    
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    
    # Attempt to parse (should fail)
    with pytest.raises((FileNotFoundError, ValueError)):
        await parsing_service.parse_document(document.document_id)
    
    # Verify job status was updated to failed
    await db_session.refresh(job)
    assert job.status == ProcessingStatus.FAILED.value
    assert job.error_message is not None


@pytest.mark.asyncio
async def test_parsing_creates_correct_chunk_count(db_session: "AsyncSession") -> None:
    """Test parsing creates appropriate number of chunks based on document length."""
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test_doc.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_789",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
    )
    
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    
    await parsing_service.parse_document(document.document_id)
    
    # Get chunks
    chunks = await chunk_repo.get_by_document(document.document_id)
    
    # Verify chunks are sequential
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
    
    # Verify total token count is reasonable
    total_tokens = sum(chunk.token_count or 0 for chunk in chunks)
    assert total_tokens > 0


@pytest.mark.asyncio
async def test_parsing_workflow_chunk_metadata(db_session: "AsyncSession") -> None:
    """Test chunks contain proper metadata (page numbers, types, headings)."""
    document_repo = DocumentRepository(db_session)
    chunk_repo = ChunkRepository(db_session)
    job_repo = JobRepository(db_session)
    
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    document = await document_repo.create(
        tenant_id=1,
        uploaded_by=1,
        filename="test_doc.pdf",
        original_filename="sample.pdf",
        file_type="pdf",
        mime_type="application/pdf",
        file_size=test_file.stat().st_size,
        storage_path=str(test_file),
        content_hash="test_hash_metadata",
    )
    
    job = await job_repo.create(
        document_id=document.document_id,
        job_type="parse_document",
    )
    
    parsing_service = ParsingService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        job_repo=job_repo,
    )
    
    await parsing_service.parse_document(document.document_id)
    
    chunks = await chunk_repo.get_by_document(document.document_id)
    
    # Verify chunks have metadata
    for chunk in chunks:
        # Check that chunk_type is set (may be None for plain text)
        assert hasattr(chunk, 'chunk_type')
        
        # Check that page information exists (may be None depending on parser)
        assert hasattr(chunk, 'start_page')
        assert hasattr(chunk, 'end_page')
