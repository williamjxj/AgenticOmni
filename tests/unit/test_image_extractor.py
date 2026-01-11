"""Unit tests for image reference extraction.

Tests image URL extraction, alt text parsing, and base64 detection.
User Story 4: Handle Special Markdown Content (Priority: P3)
"""

import pytest

from src.ingestion_parsing.parsers.markdown.image_extractor import (
    ImageReferenceData,
    extract_image_references,
)


def test_extract_image_alt_text() -> None:
    """Test extraction of image alt text.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Images

![Company Logo](https://example.com/logo.png)

![Product Diagram with detailed annotations](./diagrams/product.png)

![](https://example.com/no-alt.png)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 3
    
    # Check alt texts
    alt_texts = [img.alt_text for img in images]
    assert "Company Logo" in alt_texts
    assert "Product Diagram with detailed annotations" in alt_texts
    assert "" in alt_texts or None in alt_texts  # Empty alt text


def test_extract_image_base64_detection() -> None:
    """Test detection of base64-encoded images.
    
    User Story 4, Task T094
    """
    # Arrange
    content = """# Images

![Base64 Image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)

![External](https://example.com/image.png)

![Local](./local/image.png)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 3
    
    # Check image types
    base64_images = [img for img in images if img.is_base64]
    external_images = [img for img in images if img.is_external_url]
    local_images = [img for img in images if img.is_local_path]
    
    assert len(base64_images) == 1
    assert len(external_images) == 1
    assert len(local_images) == 1
    
    # Verify base64 image URL starts with data:image/
    assert base64_images[0].image_url.startswith("data:image/")


def test_extract_image_url_types() -> None:
    """Test classification of different image URL types.
    
    User Story 4, Task T094
    """
    # Arrange
    content = """# Image Types

![External HTTPS](https://cdn.example.com/image1.png)
![External HTTP](http://example.com/image2.jpg)
![Relative Path](../images/diagram.svg)
![Absolute Local](/var/www/images/photo.png)
![Base64](data:image/jpeg;base64,/9j/4AAQSkZJRg...)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 5
    
    # Check classifications
    https_images = [img for img in images if img.image_url.startswith("https://")]
    http_images = [img for img in images if img.image_url.startswith("http://")]
    base64_images = [img for img in images if img.is_base64]
    local_images = [img for img in images if img.is_local_path]
    
    assert len(https_images) == 1
    assert len(http_images) == 1
    assert len(base64_images) == 1
    assert len(local_images) == 2  # Relative and absolute local paths


def test_extract_image_position_tracking() -> None:
    """Test that image positions in document are tracked.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Document

First paragraph.

![Image 1](img1.png)

Second paragraph.

![Image 2](img2.png)

![Image 3](img3.png)

Third paragraph.
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 3
    
    # Check positions are tracked
    positions = [img.position_in_document for img in images]
    assert positions == [0, 1, 2]


def test_extract_image_empty_document() -> None:
    """Test image extraction from document with no images.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Document

Just text, no images.

## Section

More text.
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 0


def test_extract_image_with_special_characters_in_alt() -> None:
    """Test alt text extraction with special characters.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Images

![Logo with "quotes" and 'apostrophes'](logo.png)

![Emoji 🎉 and symbols @#$%](emoji.png)

![Unicode 中文字符](unicode.png)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 3
    
    alt_texts = [img.alt_text for img in images]
    assert any("quotes" in alt for alt in alt_texts if alt)
    assert any("🎉" in alt for alt in alt_texts if alt)
    assert any("中文" in alt for alt in alt_texts if alt)


def test_extract_image_ocr_pending_for_local() -> None:
    """Test that local images are marked for OCR processing.
    
    User Story 4, Task T103
    """
    # Arrange
    content = """# Images

![Local Image](./images/diagram.png)

![External Image](https://example.com/image.png)

![Base64 Image](data:image/png;base64,ABC123)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    local_images = [img for img in images if img.is_local_path]
    external_images = [img for img in images if img.is_external_url]
    base64_images = [img for img in images if img.is_base64]
    
    # Local images should be marked for OCR
    assert all(img.ocr_pending for img in local_images)
    
    # External and base64 images should not be marked for OCR by default
    assert not any(img.ocr_pending for img in external_images)
    assert not any(img.ocr_pending for img in base64_images)


def test_extract_image_nested_in_lists() -> None:
    """Test image extraction when images are nested in lists.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Images in Lists

- Item 1 with ![inline image](img1.png)
- Item 2
  - Nested item with ![nested image](img2.png)
- Item 3

1. Ordered item with ![ordered image](img3.png)
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 3
    
    filenames = [img.image_url for img in images]
    assert "img1.png" in filenames
    assert "img2.png" in filenames
    assert "img3.png" in filenames


def test_extract_image_in_tables() -> None:
    """Test image extraction from markdown tables.
    
    User Story 4, Task T093
    """
    # Arrange
    content = """# Table with Images

| Name | Icon |
|------|------|
| Item 1 | ![icon1](icon1.png) |
| Item 2 | ![icon2](icon2.png) |
"""
    
    # Act
    import marko
    doc = marko.parse(content)
    images = extract_image_references(doc, document_id=1)
    
    # Assert
    assert len(images) == 2
    
    filenames = [img.image_url for img in images]
    assert "icon1.png" in filenames
    assert "icon2.png" in filenames
