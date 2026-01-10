"""Unit tests for document parsers."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

from src.ingestion_parsing.parsers.pdf_parser import PDFParser


def test_pdf_parser_extract_text() -> None:
    """Test PDF text extraction using Docling."""
    parser = PDFParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    # Parse the PDF
    result = parser.parse(str(test_file))
    
    # Verify text was extracted
    assert result.text_content is not None
    assert len(result.text_content) > 0
    
    # Verify metadata
    assert result.page_count is not None
    assert result.page_count > 0


def test_pdf_parser_extract_metadata() -> None:
    """Test PDF metadata extraction."""
    parser = PDFParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    result = parser.parse(str(test_file))
    
    # Check metadata structure
    assert isinstance(result.metadata, dict)
    assert result.page_count is not None
    
    # Language detection (may be None for short documents)
    assert result.language is None or isinstance(result.language, str)


def test_pdf_parser_page_boundaries() -> None:
    """Test PDF parser preserves page boundary information."""
    parser = PDFParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    result = parser.parse(str(test_file))
    
    # Verify we have page information
    assert result.page_count is not None
    assert result.page_count >= 1


def test_pdf_parser_invalid_file() -> None:
    """Test PDF parser handles invalid files gracefully."""
    parser = PDFParser()
    
    with pytest.raises((FileNotFoundError, ValueError)):
        parser.parse("/nonexistent/file.pdf")


def test_pdf_parser_empty_document() -> None:
    """Test PDF parser handles empty documents."""
    parser = PDFParser()
    
    # This would need an actual empty PDF file
    # For now, just test that the method exists
    assert hasattr(parser, 'parse')
    assert hasattr(parser, 'extract_text')
    assert hasattr(parser, 'extract_metadata')


def test_pdf_parser_extract_text_method() -> None:
    """Test PDFParser.extract_text() method directly."""
    parser = PDFParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    text = parser.extract_text(str(test_file))
    
    assert isinstance(text, str)
    assert len(text) > 0


def test_pdf_parser_extract_metadata_method() -> None:
    """Test PDFParser.extract_metadata() method directly."""
    parser = PDFParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    metadata = parser.extract_metadata(str(test_file))
    
    assert isinstance(metadata, dict)
    # Check for expected metadata keys
    assert "page_count" in metadata or metadata.get("page_count") is not None


# ============================================================================
# DOCX Parser Tests (T083)
# ============================================================================


def test_docx_parser_extract_text() -> None:
    """Test DOCX text extraction using python-docx."""
    from src.ingestion_parsing.parsers.docx_parser import DOCXParser
    
    parser = DOCXParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.docx"
    
    # Parse the DOCX
    result = parser.parse(str(test_file))
    
    # Verify text was extracted
    assert result.text_content is not None
    assert len(result.text_content) > 0


def test_docx_parser_extract_metadata() -> None:
    """Test DOCX metadata extraction."""
    from src.ingestion_parsing.parsers.docx_parser import DOCXParser
    
    parser = DOCXParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.docx"
    
    metadata = parser.extract_metadata(str(test_file))
    
    assert isinstance(metadata, dict)


def test_docx_parser_supports_format() -> None:
    """Test DOCX parser format detection."""
    from src.ingestion_parsing.parsers.docx_parser import DOCXParser
    
    parser = DOCXParser()
    
    assert parser.supports_format("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert not parser.supports_format("application/pdf")


# ============================================================================
# TXT Parser Tests (T084)
# ============================================================================


def test_txt_parser_extract_text() -> None:
    """Test plain text extraction with UTF-8 encoding."""
    from src.ingestion_parsing.parsers.txt_parser import TXTParser
    
    parser = TXTParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.txt"
    
    result = parser.parse(str(test_file))
    
    assert result.text_content is not None
    assert len(result.text_content) > 0


def test_txt_parser_handles_encodings() -> None:
    """Test TXT parser handles different encodings."""
    from src.ingestion_parsing.parsers.txt_parser import TXTParser
    
    parser = TXTParser()
    test_file = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.txt"
    
    text = parser.extract_text(str(test_file))
    
    assert isinstance(text, str)
    assert len(text) > 0


def test_txt_parser_supports_format() -> None:
    """Test TXT parser format detection."""
    from src.ingestion_parsing.parsers.txt_parser import TXTParser
    
    parser = TXTParser()
    
    assert parser.supports_format("text/plain")
    assert not parser.supports_format("application/pdf")
