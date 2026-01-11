# Test Fixtures for OCR and Embedding Pipeline

**Feature**: 004-ocr-embedding-pipeline  
**Purpose**: Sample documents for testing OCR, embedding, and search functionality

## Required Test Documents

This directory should contain the following test documents:

### 1. sample_scanned.pdf
- **Type**: Scanned PDF (image-based)
- **Content**: English text, standard quality scan (200-300 DPI)
- **Purpose**: Test basic OCR functionality
- **Expected**: Text extraction with ≥90% accuracy

### 2. sample_mixed_content.pdf
- **Type**: PDF with both native and scanned content
- **Content**: Mix of digital text and scanned images with text
- **Purpose**: Test hybrid document processing (Docling + OCR)
- **Expected**: Extract text from both sources correctly

### 3. sample_chinese.pdf
- **Type**: Scanned PDF with Chinese text
- **Content**: Chinese characters, standard quality
- **Purpose**: Test multilingual OCR (Chinese language support)
- **Expected**: Chinese text extraction with good accuracy

## Creating Test Documents

Since these are binary files, they need to be created manually. Here are options:

### Option 1: Create Your Own
1. Create a simple PDF with text
2. Print to PDF as "image only" for scanned version
3. Include Chinese characters using Google Translate or similar
4. Save with the names above

### Option 2: Use Online Tools
- Use https://tools.pdf24.org/en/image-to-pdf to create scanned PDFs
- Use https://www.ilovepdf.com/scan-to-pdf for mixed content
- Generate Chinese text PDFs with online converters

### Option 3: Placeholder Files
For initial development, you can use any PDF files and rename them. The tests will use whatever content is in the files.

## File Specifications

- **Max size**: 10 MB per file
- **Format**: PDF (for scanned tests), DOCX (for Office tests)
- **Quality**: 200-300 DPI for scanned documents
- **Languages**: English (sample_scanned.pdf), Chinese (sample_chinese.pdf)

## Usage in Tests

These files are loaded by test cases in:
- `tests/integration/test_ocr_pipeline.py`
- `tests/integration/test_embedding_pipeline.py`
- `tests/unit/test_ocr_service.py`

Example test usage:

```python
def test_ocr_scanned_pdf():
    with open("tests/fixtures/sample_scanned.pdf", "rb") as f:
        result = ocr_service.process_document(f)
    assert result.confidence > 0.9
    assert len(result.text) > 100
```

## Note

If these files are not present, the tests that require them will be skipped with a pytest skip marker:

```python
@pytest.mark.skipif(
    not Path("tests/fixtures/sample_scanned.pdf").exists(),
    reason="Test fixture not available"
)
```

## Adding Your Own Fixtures

To add additional test documents:
1. Place PDF/DOCX files in this directory
2. Update test cases to reference the new files
3. Document the purpose and expected results here
4. Keep file sizes reasonable (<10 MB)

---

**Status**: Placeholder created - actual binary files need to be added manually
**Created**: 2026-01-11
