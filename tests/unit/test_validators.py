"""Unit tests for markdown validation functions.

Tests UTF-8 encoding validation and file extension validation for markdown files.
User Story 1: Upload and Parse Markdown Documents (Priority: P1)
"""

from pathlib import Path

import pytest

from src.shared.validators import (
    validate_markdown_encoding,
    validate_markdown_file_extension,
)


def test_validate_markdown_file_extension_md(tmp_path: Path) -> None:
    """Test .md extension is valid.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "document.md"
    md_file.write_text("# Hello")
    
    # Act
    is_valid = validate_markdown_file_extension(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_file_extension_markdown(tmp_path: Path) -> None:
    """Test .markdown extension is valid.
    
    User Story 1, Task T026
    """
    # Arrange
    markdown_file = tmp_path / "document.markdown"
    markdown_file.write_text("# Hello")
    
    # Act
    is_valid = validate_markdown_file_extension(markdown_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_file_extension_uppercase(tmp_path: Path) -> None:
    """Test uppercase .MD extension is valid.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "document.MD"
    md_file.write_text("# Hello")
    
    # Act
    is_valid = validate_markdown_file_extension(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_file_extension_invalid(tmp_path: Path) -> None:
    """Test non-markdown extensions are invalid.
    
    User Story 1, Task T026
    """
    # Arrange
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("Plain text")
    
    # Act
    is_valid = validate_markdown_file_extension(txt_file)
    
    # Assert
    assert is_valid is False


def test_validate_markdown_file_extension_no_extension(tmp_path: Path) -> None:
    """Test file with no extension is invalid.
    
    User Story 1, Task T026
    """
    # Arrange
    no_ext_file = tmp_path / "README"
    no_ext_file.write_text("# README")
    
    # Act
    is_valid = validate_markdown_file_extension(no_ext_file)
    
    # Assert
    assert is_valid is False


def test_validate_markdown_encoding_utf8(tmp_path: Path) -> None:
    """Test UTF-8 encoded markdown is valid.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "utf8.md"
    md_file.write_text("# UTF-8 文档 🎉", encoding="utf-8")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_ascii(tmp_path: Path) -> None:
    """Test ASCII encoded markdown is valid (subset of UTF-8).
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "ascii.md"
    md_file.write_text("# ASCII Document", encoding="ascii")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_invalid_encoding(tmp_path: Path) -> None:
    """Test non-UTF-8 encoded file is invalid.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "latin1.md"
    # Write with latin-1 encoding (will fail UTF-8 validation)
    with open(md_file, "wb") as f:
        f.write(b"# Document \xE9\xE8")  # Invalid UTF-8 bytes
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is False


def test_validate_markdown_encoding_empty_file(tmp_path: Path) -> None:
    """Test empty file is valid UTF-8.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "empty.md"
    md_file.write_text("", encoding="utf-8")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_unicode_emoji(tmp_path: Path) -> None:
    """Test markdown with Unicode emoji is valid UTF-8.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "emoji.md"
    md_file.write_text("# Hello 👋 World 🌍 Test 🎉", encoding="utf-8")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_chinese_characters(tmp_path: Path) -> None:
    """Test markdown with Chinese characters is valid UTF-8.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "chinese.md"
    md_file.write_text("# 中文文档\n\n这是一个测试文档。", encoding="utf-8")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_mixed_unicode(tmp_path: Path) -> None:
    """Test markdown with mixed Unicode characters is valid UTF-8.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "mixed.md"
    md_file.write_text(
        "# Mixed Languages\n\nEnglish, 中文, 日本語, 한국어, العربية, עברית",
        encoding="utf-8",
    )
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True


def test_validate_markdown_encoding_bom(tmp_path: Path) -> None:
    """Test UTF-8 with BOM is valid.
    
    User Story 1, Task T026
    """
    # Arrange
    md_file = tmp_path / "bom.md"
    # Write UTF-8 with BOM
    with open(md_file, "wb") as f:
        f.write(b"\xef\xbb\xbf# Document with BOM")
    
    # Act
    is_valid = validate_markdown_encoding(md_file)
    
    # Assert
    assert is_valid is True
