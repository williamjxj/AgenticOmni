# OCR and Embedding Configuration

**Feature**: 004-ocr-embedding-pipeline  
**Date**: 2026-01-11

## Required Environment Variables

Add these variables to your `.env` file:

```bash
# ============================================================================
# OCR Configuration
# ============================================================================

# OCR Engine Selection: auto, paddleocr, tesseract
OCR_ENGINE=auto

# Supported languages (comma-separated): en, zh
OCR_LANGUAGES=en,zh

# Minimum confidence threshold for OCR text acceptance (0.0-1.0)
OCR_CONFIDENCE_THRESHOLD=0.7

# Enable GPU acceleration for OCR (true/false)
OCR_GPU_ENABLED=true

# Maximum concurrent OCR jobs
OCR_MAX_CONCURRENT_JOBS=4

# ============================================================================
# Embedding Configuration
# ============================================================================

# Embedding model name: multilingual-e5-base, multilingual-e5-large
EMBEDDING_MODEL=multilingual-e5-base

# Batch size for embedding generation
EMBEDDING_BATCH_SIZE=32

# Enable GPU acceleration for embeddings (true/false)
EMBEDDING_GPU_ENABLED=true

# Model cache directory (optional, defaults to ~/.cache/huggingface)
# EMBEDDING_MODEL_CACHE=/path/to/model/cache

# ============================================================================
# Document Processing Configuration
# ============================================================================

# Maximum chunk size in tokens
MAX_CHUNK_SIZE=500

# Chunk overlap in tokens
CHUNK_OVERLAP=50

# Maximum document size in MB
MAX_DOCUMENT_SIZE_MB=100

# Maximum pages per document
MAX_DOCUMENT_PAGES=500

# ============================================================================
# Vector Search Configuration
# ============================================================================

# Default search result limit
SEARCH_DEFAULT_LIMIT=10

# Maximum search result limit
SEARCH_MAX_LIMIT=100

# Minimum similarity score for search results (0.0-1.0)
SEARCH_MIN_SIMILARITY=0.0

# HNSW index parameters (for pgvector)
HNSW_M=16
HNSW_EF_CONSTRUCTION=64

# ============================================================================
# Background Task Processing
# ============================================================================

# Maximum retry attempts for failed jobs
MAX_JOB_RETRIES=3

# Job priority (1-10, 1=highest)
DEFAULT_JOB_PRIORITY=5

# Maximum concurrent processing jobs
MAX_CONCURRENT_JOBS=4
```

## Configuration Notes

### OCR Engine Selection

- **auto**: Automatically selects best engine based on document type and quality
- **paddleocr**: Use PaddleOCR for all documents (better for complex layouts, Chinese)
- **tesseract**: Use Tesseract for all documents (faster for simple, high-quality scans)

### GPU Acceleration

If you don't have a GPU or prefer CPU-only processing:

```bash
OCR_GPU_ENABLED=false
EMBEDDING_GPU_ENABLED=false
```

Note: CPU processing will be significantly slower (5-10x for OCR, 3-5x for embeddings).

### Language Support

Currently supported languages:
- **en**: English
- **zh**: Chinese (Simplified and Traditional)

To add more languages in the future, update `OCR_LANGUAGES` with comma-separated ISO 639-1 codes.

### Performance Tuning

For better performance on high-end hardware:

```bash
EMBEDDING_BATCH_SIZE=64  # Increase if you have more GPU memory
OCR_MAX_CONCURRENT_JOBS=8  # Increase if you have more CPU cores
MAX_CONCURRENT_JOBS=8
```

For resource-constrained environments:

```bash
EMBEDDING_BATCH_SIZE=16  # Reduce to lower memory usage
OCR_MAX_CONCURRENT_JOBS=2
MAX_CONCURRENT_JOBS=2
```

### Vector Search Tuning

For better search accuracy (slower indexing):

```bash
HNSW_M=32
HNSW_EF_CONSTRUCTION=128
```

For faster indexing (slightly lower accuracy):

```bash
HNSW_M=8
HNSW_EF_CONSTRUCTION=32
```

## Validation

After adding these variables to your `.env` file, verify the configuration:

```bash
# Check that all required variables are set
python scripts/validate_env.py --feature ocr-embedding
```

## Security Notes

- Never commit `.env` files to version control
- Use `.env.example` for documentation only (no real values)
- Rotate any exposed credentials immediately
- Use environment-specific `.env` files for different deployments

---

**Reference**: See `src/shared/config.py` for how these variables are loaded and validated.
