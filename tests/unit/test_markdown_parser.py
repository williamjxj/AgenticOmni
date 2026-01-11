"""Unit tests for MarkdownParser.

Tests text extraction, structural element detection, and metadata extraction.
User Story 1: Upload and Parse Markdown Documents (Priority: P1)
"""

from pathlib import Path
from typing import Any

import pytest

from src.ingestion_parsing.models.parsing_result import ParsingResult
from src.ingestion_parsing.parsers.markdown_parser import MarkdownParser


@pytest.mark.asyncio
async def test_markdown_parser_text_extraction_basic(tmp_path: Path) -> None:
    """Test basic markdown text extraction with marko.
    
    User Story 1, Task T025
    """
    # Arrange
    markdown_file = tmp_path / "test.md"
    markdown_file.write_text(
        """# Hello World

This is a paragraph with some **bold** text and *italic* text.

## Section

Another paragraph here.
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert isinstance(result, ParsingResult)
    assert result.text_content is not None
    assert "Hello World" in result.text_content
    assert "paragraph" in result.text_content
    assert "Section" in result.text_content


@pytest.mark.asyncio
async def test_markdown_parser_heading_detection(tmp_path: Path) -> None:
    """Test heading count extraction from markdown.
    
    User Story 1, Task T027
    """
    # Arrange
    markdown_file = tmp_path / "headings.md"
    markdown_file.write_text(
        """# H1 Title

## H2 Subtitle

### H3 Section

Some content here.

## Another H2

Text.
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata is not None
    assert "heading_count" in result.metadata
    assert result.metadata["heading_count"] == 4  # 1 H1 + 3 H2/H3


@pytest.mark.asyncio
async def test_markdown_parser_code_block_detection(tmp_path: Path) -> None:
    """Test code block count extraction from markdown.
    
    User Story 1, Task T027
    """
    # Arrange
    markdown_file = tmp_path / "code.md"
    markdown_file.write_text(
        """# Code Examples

Here's some Python:

```python
def hello():
    print("Hello")
```

And some JavaScript:

```javascript
console.log("Hi");
```

Inline `code` is not counted.
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata is not None
    assert "code_block_count" in result.metadata
    assert result.metadata["code_block_count"] == 2


@pytest.mark.asyncio
async def test_markdown_parser_link_detection(tmp_path: Path) -> None:
    """Test link count extraction from markdown.
    
    User Story 1, Task T027
    """
    # Arrange
    markdown_file = tmp_path / "links.md"
    markdown_file.write_text(
        """# Links

Visit [Example](https://example.com) for more info.

Also check out [Another Link](https://another.com).

[Third link](https://third.com)
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata is not None
    assert "link_count" in result.metadata
    assert result.metadata["link_count"] == 3


@pytest.mark.asyncio
async def test_markdown_parser_table_detection(tmp_path: Path) -> None:
    """Test GFM table detection from markdown.
    
    User Story 1, Task T027
    """
    # Arrange
    markdown_file = tmp_path / "table.md"
    markdown_file.write_text(
        """# Tables

| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |

Some text.

| Col1 | Col2 |
|------|------|
| A | B |
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata is not None
    assert "table_count" in result.metadata
    assert result.metadata["table_count"] == 2


@pytest.mark.asyncio
async def test_markdown_parser_structural_elements(tmp_path: Path) -> None:
    """Test structural element identification (heading, code, list, table).
    
    User Story 1, Task T027
    """
    # Arrange
    markdown_file = tmp_path / "structure.md"
    markdown_file.write_text(
        """# Document

## Intro

- List item 1
- List item 2

```python
code_here = True
```

| Table | Header |
|-------|--------|
| Data | Value |
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.structural_elements is not None
    element_types = [elem["type"] for elem in result.structural_elements]
    
    assert "heading" in element_types
    assert "list" in element_types
    assert "code_block" in element_types
    assert "table" in element_types


@pytest.mark.asyncio
async def test_markdown_parser_empty_file(tmp_path: Path) -> None:
    """Test parsing empty markdown file returns empty result.
    
    User Story 1, Task T025
    """
    # Arrange
    markdown_file = tmp_path / "empty.md"
    markdown_file.write_text("")
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.text_content == ""
    assert result.metadata["heading_count"] == 0
    assert result.metadata["code_block_count"] == 0


@pytest.mark.asyncio
async def test_markdown_parser_with_sample_fixture(
    sample_markdown_file: Path,
) -> None:
    """Test parsing with sample.md fixture from test fixtures.
    
    User Story 1, Task T025
    """
    # Arrange
    parser = MarkdownParser()
    sample_file = Path("tests/fixtures/sample_documents/sample.md")
    
    if not sample_file.exists():
        pytest.skip("Sample fixture not found")
    
    # Act
    result = await parser.parse(sample_file)
    
    # Assert
    assert result.text_content is not None
    assert len(result.text_content) > 0
    assert result.metadata is not None


@pytest.mark.asyncio
async def test_markdown_parser_preserves_code_content(tmp_path: Path) -> None:
    """Test code block content is preserved in text extraction.
    
    User Story 1, Task T025
    """
    # Arrange
    markdown_file = tmp_path / "code_content.md"
    code_content = """def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 3)
"""
    markdown_file.write_text(
        f"""# Function Example

```python
{code_content}```

The function adds two numbers.
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert "calculate_sum" in result.text_content
    assert "def calculate_sum(a, b):" in result.text_content


@pytest.mark.asyncio
async def test_markdown_parser_list_extraction(tmp_path: Path) -> None:
    """Test list items are extracted in text content.
    
    User Story 1, Task T025
    """
    # Arrange
    markdown_file = tmp_path / "lists.md"
    markdown_file.write_text(
        """# Lists

Unordered:
- Item one
- Item two
- Item three

Ordered:
1. First
2. Second
3. Third
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert "Item one" in result.text_content
    assert "First" in result.text_content
    assert "Second" in result.text_content


@pytest.mark.asyncio
async def test_markdown_parser_malformed_markdown_graceful(tmp_path: Path) -> None:
    """Test parser handles malformed markdown gracefully without crashing.
    
    User Story 1, Task T025
    """
    # Arrange
    markdown_file = tmp_path / "malformed.md"
    markdown_file.write_text(
        """# Incomplete Heading ##

[Link with no URL]()

```
Unclosed code block
"""
    )
    
    parser = MarkdownParser()
    
    # Act - should not raise exception
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result is not None
    assert isinstance(result.text_content, str)


# Fixtures


@pytest.mark.asyncio
async def test_markdown_parser_code_block_language_detection(tmp_path: Path) -> None:
    """Test detection of code block language specifiers.
    
    User Story 2, Task T044
    """
    # Arrange
    markdown_file = tmp_path / "code_langs.md"
    markdown_file.write_text(
        """# Code Examples

```python
def hello():
    pass
```

```javascript
console.log("hi");
```

```typescript
const x: number = 5;
```

```
plain_code = True
```
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata["code_block_count"] == 4
    # Check structural elements include language info
    code_blocks = [e for e in result.structural_elements if e["type"] == "code_block"]
    languages = [block["language"] for block in code_blocks]
    assert "python" in languages
    assert "javascript" in languages
    assert "typescript" in languages
    assert "plain" in languages or "" in languages


@pytest.mark.asyncio
async def test_markdown_parser_link_url_extraction(tmp_path: Path) -> None:
    """Test extraction of link URLs from markdown.
    
    User Story 2, Task T045
    """
    # Arrange
    markdown_file = tmp_path / "links.md"
    markdown_file.write_text(
        """# Links

Visit [Example](https://example.com) for more info.

Check [GitHub](https://github.com/user/repo) repository.

Internal [link](/docs/api) to API docs.

[Multiple](https://one.com) [links](https://two.com) in a row.
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata["link_count"] >= 5
    link_urls = result.metadata.get("link_urls", [])
    assert "https://example.com" in link_urls
    assert "https://github.com/user/repo" in link_urls
    assert "/docs/api" in link_urls
    assert "https://one.com" in link_urls
    assert "https://two.com" in link_urls


@pytest.mark.asyncio
async def test_markdown_parser_gfm_table_parsing(tmp_path: Path) -> None:
    """Test GFM table detection and text extraction.
    
    User Story 2, Task T046
    """
    # Arrange
    markdown_file = tmp_path / "table.md"
    markdown_file.write_text(
        """# Tables

| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |

Some text.

| Product | Price |
|---------|-------|
| Widget | $10 |
| Gadget | $20 |
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    assert result.metadata["table_count"] == 2
    # Check that table content is in text
    assert "Alice" in result.text_content
    assert "NYC" in result.text_content
    assert "Widget" in result.text_content
    assert "$10" in result.text_content


@pytest.mark.asyncio
async def test_markdown_parser_table_structure_preserved(tmp_path: Path) -> None:
    """Test that table cell contents are preserved in text extraction.
    
    User Story 2, Task T046
    """
    # Arrange
    markdown_file = tmp_path / "table_structure.md"
    markdown_file.write_text(
        """# Data Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data A1 | Data B1 | Data C1 |
| Data A2 | Data B2 | Data C2 |
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    text = result.text_content
    # All table data should be present
    assert "Column 1" in text
    assert "Column 2" in text
    assert "Column 3" in text
    assert "Data A1" in text
    assert "Data B1" in text
    assert "Data C1" in text
    assert "Data A2" in text
    assert "Data B2" in text
    assert "Data C2" in text


@pytest.mark.asyncio
async def test_markdown_parser_mixed_content(tmp_path: Path) -> None:
    """Test parsing markdown with mixed content types.
    
    User Story 2, comprehensive test
    """
    # Arrange
    markdown_file = tmp_path / "mixed.md"
    markdown_file.write_text(
        """---
title: Mixed Content
author: Test User
---

# Main Heading

This is a paragraph with a [link](https://example.com).

## Code Section

```python
def hello():
    return "world"
```

## Data Table

| Name | Value |
|------|-------|
| Test | 123 |

## List

- Item 1
- Item 2

![Image](https://example.com/img.png)
"""
    )
    
    parser = MarkdownParser()
    
    # Act
    result = await parser.parse(markdown_file)
    
    # Assert
    # Frontmatter
    assert result.metadata.get("has_yaml_frontmatter") is True
    frontmatter = result.metadata.get("frontmatter", {})
    assert frontmatter.get("title") == "Mixed Content"
    assert frontmatter.get("author") == "Test User"
    
    # Counts
    assert result.metadata["heading_count"] >= 3
    assert result.metadata["code_block_count"] >= 1
    assert result.metadata["link_count"] >= 1
    assert result.metadata["table_count"] >= 1
    assert result.metadata["image_count"] >= 1
    
    # Content preserved
    assert "Main Heading" in result.text_content
    assert "hello" in result.text_content
    assert "Test" in result.text_content


# Fixtures


@pytest.fixture
def sample_markdown_file() -> Path:
    """Return path to sample markdown fixture."""
    return Path("tests/fixtures/sample_documents/sample.md")
