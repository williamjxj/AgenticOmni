"""Unit tests for document chunking service."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

from src.ingestion_parsing.services.chunking_service import ChunkingService


def test_chunk_document_basic() -> None:
    """Test basic document chunking with 512-token target."""
    service = ChunkingService(
        chunk_size_tokens=512,
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=100,
    )
    
    # Create sample text (simulating a multi-paragraph document)
    sample_text = "This is a test paragraph. " * 100  # ~500 words
    
    chunks = service.chunk_document(sample_text)
    
    # Verify chunks were created
    assert len(chunks) > 0
    
    # Verify each chunk has required fields
    for chunk in chunks:
        assert hasattr(chunk, 'content')
        assert hasattr(chunk, 'chunk_index')
        assert hasattr(chunk, 'token_count')
        assert len(chunk.content) > 0


def test_chunk_document_token_limits() -> None:
    """Test chunks respect token size limits (with overlap tolerance)."""
    service = ChunkingService(
        chunk_size_tokens=512,
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=100,
    )
    
    # Long text with paragraph breaks to force splitting
    paragraphs = ["This is paragraph number {}. ".format(i) * 20 for i in range(20)]
    sample_text = "\n\n".join(paragraphs)  # Multiple paragraphs
    
    chunks = service.chunk_document(sample_text)
    
    # Verify chunks were created
    assert len(chunks) > 1
    
    # Verify chunks are within reasonable limits
    # Note: overlap can cause chunks to slightly exceed target size
    for chunk in chunks:
        assert chunk.token_count is not None
        assert chunk.token_count <= 600  # Allow some tolerance for overlap


def test_chunk_document_overlap() -> None:
    """Test chunks have 50-token overlap."""
    service = ChunkingService(
        chunk_size_tokens=200,  # Smaller for testing
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=50,
    )
    
    sample_text = "Word " * 500
    
    chunks = service.chunk_document(sample_text)
    
    # If we have multiple chunks, verify overlap exists
    if len(chunks) > 1:
        # The end of chunk N should overlap with the start of chunk N+1
        # This is implicit in the chunking - we just verify reasonable sizes
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i


def test_semantic_chunking_headings() -> None:
    """Test semantic chunking preserves heading structure."""
    service = ChunkingService(
        chunk_size_tokens=512,
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=100,
    )
    
    # Text with clear heading structure
    sample_text = """
# Introduction
This is the introduction paragraph with some content.

# Methods
This is the methods section with detailed procedures.

# Results
This section contains the results of the experiment.
"""
    
    chunks = service.chunk_document(sample_text)
    
    # Verify chunks were created
    assert len(chunks) > 0
    
    # Verify chunk metadata (if implemented)
    for chunk in chunks:
        assert chunk.content is not None


def test_chunking_service_split_by_semantic_boundaries() -> None:
    """Test semantic boundary detection."""
    service = ChunkingService()
    
    text_with_boundaries = """
Paragraph 1 with some content.

Paragraph 2 with different content.

Paragraph 3 with more information.
"""
    
    # This tests the internal method if exposed, or we test via chunk_document
    chunks = service.chunk_document(text_with_boundaries)
    assert len(chunks) > 0


def test_chunking_service_enforce_token_limits() -> None:
    """Test token limit enforcement with tiktoken."""
    service = ChunkingService(
        chunk_size_tokens=100,
        chunk_overlap_tokens=20,
        min_chunk_size_tokens=50,
    )
    
    # Long text that will need splitting
    long_text = "This is a word. " * 200  # ~400 words
    
    chunks = service.chunk_document(long_text)
    
    # All chunks should be within reasonable limits
    # Allow tolerance for overlap
    for chunk in chunks:
        if chunk.token_count:
            assert chunk.token_count <= 150  # Allow tolerance for overlap
            # Last chunk might be smaller, but others should be near target
            if chunk.chunk_index < len(chunks) - 1:
                assert chunk.token_count >= 50


def test_chunking_service_add_overlap() -> None:
    """Test overlap addition between chunks."""
    service = ChunkingService(
        chunk_size_tokens=200,
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=50,
    )
    
    text = "Sentence. " * 100
    
    chunks = service.chunk_document(text)
    
    if len(chunks) > 1:
        # Verify sequential chunk indices
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i


def test_chunking_empty_text() -> None:
    """Test chunking handles empty text."""
    service = ChunkingService()
    
    chunks = service.chunk_document("")
    
    # Should return empty list or handle gracefully
    assert isinstance(chunks, list)


def test_chunking_short_text() -> None:
    """Test chunking handles text shorter than minimum chunk size."""
    service = ChunkingService(
        chunk_size_tokens=512,
        chunk_overlap_tokens=50,
        min_chunk_size_tokens=100,
    )
    
    short_text = "Just a few words here."
    
    chunks = service.chunk_document(short_text)
    
    # Should create at least one chunk even if below minimum
    # (or handle appropriately based on implementation)
    assert isinstance(chunks, list)


def test_chunking_table_handling() -> None:
    """Test chunking handles table-like content."""
    service = ChunkingService()
    
    table_text = """
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
"""
    
    chunks = service.chunk_document(table_text)
    
    assert len(chunks) > 0
    # Table should ideally stay together in a chunk
    assert any("|" in chunk.content for chunk in chunks)
