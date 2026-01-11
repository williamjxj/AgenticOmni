# Research: OCR and Embedding Pipeline

**Feature**: 004-ocr-embedding-pipeline  
**Date**: 2026-01-11  
**Status**: Completed

## Overview

This document consolidates research findings for implementing OCR, embedding generation, and vector similarity search capabilities for the AI eDocuments platform.

## Technical Decisions

### 1. OCR Engine Selection

**Decision**: Use PaddleOCR as primary engine with Tesseract as fallback

**Rationale**:
- **PaddleOCR**: 
  - Superior accuracy on complex layouts and low-quality scans
  - Built-in support for English and Chinese languages (requirement)
  - Provides confidence scores for extracted text
  - GPU acceleration support for faster processing
  - More robust with mixed content (text + images)
- **Tesseract**: 
  - Fallback option for simpler documents
  - Widely adopted, stable, and well-documented
  - Lower resource requirements
  - Good for high-quality scans

**Alternatives Considered**:
- **EasyOCR**: Good multi-language support but slower than PaddleOCR
- **Cloud OCR APIs (Google Vision, AWS Textract)**: Excellent accuracy but introduces cost per document, latency, and data privacy concerns
- **Azure Form Recognizer**: Strong structured document handling but requires cloud dependency

**Implementation Notes**:
- Use PaddleOCR for complex documents (scanned PDFs, images, low quality)
- Consider Tesseract for simple, high-quality documents to reduce GPU load
- Implement confidence threshold (e.g., 0.7) to flag low-quality extractions

---

### 2. Document Parsing Library

**Decision**: Use Docling for PDF/DOCX parsing

**Rationale**:
- Already included in project dependencies (`docling>=1.0.0`)
- Designed specifically for document understanding with structure preservation
- Handles both native text extraction and integration with OCR for image-based content
- Maintains document hierarchy (headings, paragraphs, tables)
- Better than raw pypdf/python-docx for complex layouts

**Alternatives Considered**:
- **pypdf + python-docx**: Basic libraries, require more custom logic for structure preservation
- **Apache Tika**: Java dependency, heavier setup
- **Unstructured.io**: Similar capabilities but adds another dependency when Docling is sufficient

**Implementation Notes**:
- Use Docling's document parser for initial text extraction
- Hook into Docling's image extraction pipeline to pass images to PaddleOCR
- Preserve document structure metadata (page numbers, sections, tables)

---

### 3. Embedding Model Selection

**Decision**: Use multilingual-e5-large or multilingual-e5-base from sentence-transformers

**Rationale**:
- **Multi-language Support**: Native support for English and Chinese (requirement)
- **Performance**: State-of-the-art semantic similarity performance on MTEB benchmarks
- **Context Length**: Supports up to 512 tokens (aligns with 500-token chunk requirement)
- **License**: MIT license, suitable for commercial use
- **Model Size**: 
  - `multilingual-e5-base`: 278M parameters, 768 dimensions - good balance
  - `multilingual-e5-large`: 560M parameters, 1024 dimensions - higher accuracy
- **Local Deployment**: Can run locally or on GPU for data privacy

**Alternatives Considered**:
- **OpenAI embeddings (text-embedding-3-small/large)**: Excellent quality but requires API calls, ongoing costs, and sends data externally
- **BGE-M3**: Good multilingual support but slightly lower English performance
- **Cohere embeddings**: Strong but cloud-dependent
- **paraphrase-multilingual-mpnet-base-v2**: Older model, lower performance than E5

**Implementation Notes**:
- Start with `multilingual-e5-base` for better resource efficiency
- Can upgrade to `multilingual-e5-large` if accuracy is insufficient
- Use GPU for embedding generation if available (batch processing)
- Implement batch embedding generation for efficiency (32-64 documents at a time)

---

### 4. Vector Database Storage

**Decision**: Use pgvector extension in existing PostgreSQL database

**Rationale**:
- Already installed and configured in project (`pgvector>=0.2.4` in dependencies)
- Co-locates vector embeddings with relational data (documents, chunks, metadata)
- Simplifies deployment - no additional database infrastructure
- Supports efficient similarity search with IVFFLAT or HNSW indexes
- Strong consistency guarantees
- Transactional support for atomic updates

**Alternatives Considered**:
- **Qdrant**: Purpose-built vector database, excellent performance but adds infrastructure complexity
- **Weaviate**: Good semantic search features but another service to manage
- **Pinecone**: Cloud-native, managed but introduces vendor lock-in and ongoing costs
- **Milvus**: High performance but overkill for initial scale (10k documents)
- **ChromaDB**: Simple but not production-ready at scale

**Implementation Notes**:
- Use `vector(768)` or `vector(1024)` column type depending on model choice
- Create HNSW index for fast approximate nearest neighbor search
- Use cosine similarity for distance metric (`<=>` operator)
- Store embeddings alongside DocumentChunk records for easy joins

---

### 5. Chunking Strategy

**Decision**: Use semantic chunking with 500-token limit and 50-token overlap

**Rationale**:
- **500 tokens**: Fits within embedding model context (512 tokens) with margin for special tokens
- **50-token overlap**: Balances context preservation with storage efficiency (10% overlap)
- **Semantic boundaries**: Split on paragraph boundaries when possible to maintain coherence
- Aligns with user requirement from specification

**Alternatives Considered**:
- **Fixed-size chunking**: Simple but breaks semantic units
- **Sliding window**: Preserves context but creates many redundant chunks
- **LangChain RecursiveCharacterTextSplitter**: Good default but less control
- **Sentence-based chunking**: Too small, loses context

**Implementation Notes**:
- Use `tiktoken` (already in dependencies) for accurate token counting
- Implement hierarchy: Try paragraph splits first, then sentence splits, then character splits
- Preserve document structure metadata in each chunk (page number, section heading)
- Store chunk sequence number and character offsets for reconstruction

---

### 6. Asynchronous Processing Architecture

**Decision**: Use Dramatiq with Redis for background task processing

**Rationale**:
- Already included in dependencies (`dramatiq[redis]>=1.15.0`)
- **Async processing needed for**:
  - OCR is CPU/GPU intensive (seconds to minutes per document)
  - Embedding generation requires batching for efficiency
  - Don't block HTTP requests waiting for processing
- **Dramatiq benefits**:
  - Reliable task queue with retries
  - Dead letter queue for failed tasks
  - Task prioritization support
  - Progress tracking via middleware
- **Redis**: Fast, lightweight, already used for caching

**Alternatives Considered**:
- **Celery**: More mature but heavier, more complex configuration
- **RQ**: Simpler but less feature-rich
- **APScheduler**: For scheduling only, not distributed task queue
- **Sync processing**: Unacceptable latency for users

**Implementation Notes**:
- Create separate actors for: OCR extraction, embedding generation, batch processing
- Implement task chaining: Upload → OCR → Chunking → Embedding → Index
- Use priority queues: P1 (single doc uploads) > P2 (batch uploads) > P3 (reprocessing)
- Store task IDs in ProcessingJob table for status tracking

---

### 7. Search Implementation

**Decision**: Two-tier search strategy - vector similarity + metadata filtering

**Rationale**:
- **Primary**: pgvector similarity search with cosine distance
- **Enhancements**: 
  - Pre-filter by metadata (tenant_id, folder, date) before vector search
  - Post-rank by hybrid relevance (vector similarity + metadata boosts)
  - Return top 10 by default, max 100 (user requirement)
- **Performance**: HNSW index provides sub-linear search time even with large collections

**Alternatives Considered**:
- **Hybrid search (BM25 + vector)**: Complex, requires Elasticsearch or additional dependencies
- **Pure vector search**: Good but ignores structured metadata
- **Keyword-only search**: Insufficient for semantic queries

**Implementation Notes**:
- Implement search API endpoint with filters: `POST /api/v1/search`
- Support "find similar" from document ID: `GET /api/v1/documents/{id}/similar`
- Return results with similarity scores, snippets, and metadata
- Implement pagination with cursor-based approach for large result sets

---

### 8. Language Detection

**Decision**: Use `langdetect` library for automatic language detection

**Rationale**:
- Lightweight, fast, supports 55+ languages including English and Chinese
- Helps route documents to appropriate OCR models if needed
- Can be used for analytics and search filtering

**Alternatives Considered**:
- **fasttext language detection**: More accurate but larger model
- **Manual language tagging**: Puts burden on users
- **Assume single language**: Inflexible

**Implementation Notes**:
- Detect language after text extraction
- Store detected language in Document metadata
- Use for monitoring and analytics (e.g., track language distribution)
- Future: Enable language-specific search filters

---

### 9. Error Handling and Retry Logic

**Decision**: Implement graduated retry strategy with circuit breaker pattern

**Rationale**:
- OCR and embedding can have transient failures (GPU out of memory, model loading issues)
- Network issues with Redis/database
- Need to balance retry attempts with failure detection

**Strategy**:
- **Retry schedule**: 3 attempts with exponential backoff (0s, 30s, 5m)
- **Circuit breaker**: After 5 consecutive failures, pause processing for 10 minutes
- **Failure categorization**:
  - Transient (retry): Network errors, timeouts, resource constraints
  - Permanent (don't retry): Corrupt files, unsupported formats, parsing errors
- **Dead letter queue**: Move permanently failed tasks for manual review

**Implementation Notes**:
- Use Dramatiq's built-in retry mechanism with custom middleware
- Log all failures with structured logging (document_id, error_type, attempt_number)
- Expose metrics for monitoring (failure rate, retry rate, queue depth)
- User notification for permanent failures

---

### 10. Testing Strategy

**Decision**: Multi-layer testing approach

**Test Coverage**:
1. **Unit Tests** (pytest):
   - Text extraction functions (mocked file I/O)
   - Chunking logic with various document sizes
   - Embedding generation (mocked model)
   - Vector search queries (test database)

2. **Integration Tests**:
   - End-to-end document upload → OCR → embedding → search
   - Batch processing workflows
   - Error handling and retry mechanisms
   - Database transactions and constraints

3. **Contract Tests**:
   - API endpoint contracts (request/response schemas)
   - Task queue message formats
   - Database schema validation

4. **Performance Tests**:
   - OCR throughput (documents/minute)
   - Embedding generation latency
   - Search response time with varying collection sizes
   - Concurrent upload handling

**Test Data**:
- Sample documents: Clean PDFs, scanned PDFs, DOCX with images, multi-page documents
- Edge cases: Corrupted files, very large files, empty files, non-text content
- Languages: English, Chinese, mixed-language documents

**Implementation Notes**:
- Use pytest fixtures for test documents and database setup
- Mock external dependencies (PaddleOCR, embedding models) in unit tests
- Use real models in integration tests with small sample documents
- Achieve 80% code coverage minimum (project requirement)

---

## Performance Benchmarks

### Expected Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| OCR per page | 2-5 seconds | Standard quality scan (300 DPI) |
| Embedding per chunk | 0.1-0.2 seconds | GPU, batch size 32 |
| Search query | < 2 seconds | 10k document collection |
| Document processing | < 30 seconds | 20-page typical document (end-to-end) |
| Batch upload | 60% faster | vs sequential (20+ documents) |
| Concurrent users | 50+ | Without degradation |

### Resource Requirements

- **CPU**: 4+ cores for parallel OCR processing
- **Memory**: 8GB minimum, 16GB recommended (model loading + document buffers)
- **GPU**: Optional but highly recommended for faster OCR and embedding generation
  - NVIDIA GPU with 4GB+ VRAM (PaddleOCR + embedding models)
  - CUDA 11.0+ support
- **Storage**: 
  - Document storage: ~1MB average per document
  - Vector storage: ~3KB per chunk (768-dim embeddings)
  - Database: ~10GB for 10k documents with embeddings
- **Redis**: 512MB minimum for task queue

---

## Security Considerations

### Malware Scanning

- Use existing `clamd` integration (already in dependencies)
- Scan all uploads before processing
- Quarantine suspicious files
- Log all scan results

### Data Privacy

- All processing happens locally (no external API calls)
- Tenant-scoped access (multi-tenancy)
- Encryption at rest for stored documents (if configured)
- Audit logging for document access

### Input Validation

- File size limits: Max 100MB per file
- Format validation: Only PDF/DOCX accepted initially
- Content validation: Reject empty or corrupted files
- Rate limiting: Prevent abuse of upload/search endpoints

---

## Dependencies Confirmed

All required dependencies are already present in `pyproject.toml`:

✅ **Document Processing**:
- `docling>=1.0.0` - Document parsing
- `pytesseract>=0.3.10` - OCR (Tesseract wrapper)
- `opencv-python>=4.9.0` - Image preprocessing for OCR
- `pypdf>=4.0.0` - PDF handling
- `python-docx>=1.1.0` - DOCX handling
- `pillow>=10.2.0` - Image manipulation

✅ **Embeddings & Vector Search**:
- `pgvector>=0.2.4` - PostgreSQL vector extension
- `tiktoken>=0.5.2` - Token counting

✅ **Task Queue**:
- `dramatiq[redis]>=1.15.0` - Background task processing
- `redis>=5.0.1` - Task queue backend

✅ **Additional Required** (to be added):
- `sentence-transformers>=2.3.0` - Embedding model framework
- `paddleocr>=2.7.0` - PaddleOCR library
- `langdetect>=1.0.9` - Language detection

---

## Implementation Phases

### Phase 1: Core Text Extraction (P1 - MVP)
- Document upload with validation
- Docling integration for native PDF/DOCX parsing
- OCR integration (PaddleOCR + Tesseract)
- Text storage with confidence scores
- Basic status tracking

### Phase 2: Embedding & Search (P2)
- Document chunking with overlap
- Embedding generation (multilingual-e5-base)
- pgvector storage setup
- Semantic search API
- Similar document discovery

### Phase 3: Batch Processing (P3)
- Multi-file upload
- Folder structure preservation
- Parallel processing
- Progress tracking
- Batch status reporting

### Phase 4: Optimization & Monitoring
- Performance tuning
- Monitoring dashboard
- Error analytics
- Resource usage tracking
- A/B testing for model selection

---

## Open Questions Resolved

1. ✅ **Chunking parameters**: 500 tokens with 50 token overlap (from spec clarification)
2. ✅ **Search result limits**: Default 10, max 100 (from spec clarification)
3. ✅ **Language support**: English and Chinese (from spec clarification)
4. ✅ **OCR engine choice**: PaddleOCR primary, Tesseract fallback (research decision)
5. ✅ **Embedding model**: multilingual-e5-base (research decision)
6. ✅ **Vector database**: pgvector in PostgreSQL (already configured)

---

## References

- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Docling Documentation](https://github.com/DS4SD/docling)
- [Multilingual-E5 Paper](https://arxiv.org/abs/2402.05672)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Dramatiq Documentation](https://dramatiq.io/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/async/)
