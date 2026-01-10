"""Unit tests for file validation functions."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

from src.shared.validators import (
    detect_file_type,
    generate_content_hash,
    validate_file_size,
    validate_file_type,
    validate_filename,
)


def test_detect_file_type_pdf() -> None:
    """Test file type detection for PDF using magic bytes."""
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    mime_type = detect_file_type(str(test_file))
    
    assert mime_type == "application/pdf"


def test_detect_file_type_txt() -> None:
    """Test file type detection for text file."""
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.txt"
    
    mime_type = detect_file_type(str(test_file))
    
    assert mime_type in ["text/plain", "text/x-python"]  # May vary by system


def test_detect_file_type_nonexistent() -> None:
    """Test file type detection raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        detect_file_type("/nonexistent/file.pdf")


def test_validate_file_size_within_limit() -> None:
    """Test file size validation passes for file within limit."""
    file_size = 5_000_000  # 5MB
    max_size = 50_000_000  # 50MB
    
    result = validate_file_size(file_size, max_size)
    
    assert result is True


def test_validate_file_size_exceeds_limit() -> None:
    """Test file size validation fails for file exceeding limit."""
    file_size = 60_000_000  # 60MB
    max_size = 50_000_000  # 50MB
    
    result = validate_file_size(file_size, max_size)
    
    assert result is False


def test_validate_file_size_exactly_at_limit() -> None:
    """Test file size validation passes for file exactly at limit."""
    file_size = 50_000_000  # 50MB
    max_size = 50_000_000  # 50MB
    
    result = validate_file_size(file_size, max_size)
    
    assert result is True


def test_validate_file_size_zero_bytes() -> None:
    """Test file size validation fails for zero-byte file."""
    file_size = 0
    max_size = 50_000_000
    
    result = validate_file_size(file_size, max_size)
    
    assert result is False


def test_validate_file_type_allowed() -> None:
    """Test file type validation passes for allowed type."""
    mime_type = "application/pdf"
    allowed_types = ["application/pdf", "text/plain", "application/msword"]
    
    result = validate_file_type(mime_type, allowed_types)
    
    assert result is True


def test_validate_file_type_not_allowed() -> None:
    """Test file type validation fails for disallowed type."""
    mime_type = "application/x-msdownload"  # .exe
    allowed_types = ["application/pdf", "text/plain", "application/msword"]
    
    result = validate_file_type(mime_type, allowed_types)
    
    assert result is False


def test_generate_content_hash() -> None:
    """Test SHA-256 content hash generation."""
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.txt"
    
    content_hash = generate_content_hash(str(test_file))
    
    assert len(content_hash) == 64  # SHA-256 produces 64 hex characters
    assert content_hash.isalnum()  # Only alphanumeric characters
    
    # Test determinism - same file should produce same hash
    content_hash_2 = generate_content_hash(str(test_file))
    assert content_hash == content_hash_2


def test_generate_content_hash_different_files() -> None:
    """Test different files produce different hashes."""
    test_file_1 = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.txt"
    test_file_2 = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    hash_1 = generate_content_hash(str(test_file_1))
    hash_2 = generate_content_hash(str(test_file_2))
    
    assert hash_1 != hash_2


def test_generate_content_hash_nonexistent() -> None:
    """Test content hash generation raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        generate_content_hash("/nonexistent/file.pdf")


def test_validate_filename_safe() -> None:
    """Test filename validation passes for safe filename."""
    assert validate_filename("document.pdf") is True
    assert validate_filename("report-2024.docx") is True
    assert validate_filename("file_name.txt") is True


def test_validate_filename_path_traversal() -> None:
    """Test filename validation fails for path traversal attempts."""
    assert validate_filename("../../../etc/passwd") is False
    assert validate_filename("..\\..\\windows\\system32") is False
    assert validate_filename("/etc/passwd") is False
    assert validate_filename("subdir/file.pdf") is False
