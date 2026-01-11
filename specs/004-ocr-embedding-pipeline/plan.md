# Implementation Plan: OCR and Embedding Pipeline

**Branch**: `004-ocr-embedding-pipeline` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)

## Summary

This feature implements comprehensive OCR text extraction and embedding generation capabilities for the AI eDocuments platform, enabling semantic search across uploaded documents. The solution integrates:

- **Document Parsing**: Docling library for native PDF/DOCX text extraction with structure preservation
- **OCR Processing**: PaddleOCR (primary) and Tesseract (fallback) for scanned/image-based content with English and Chinese language support
- **Embedding Generation**: Multilingual-E5-base model for semantic vector representations with 500-token chunking and 50-token overlap
- **Vector Search**: pgvector-powered similarity search with cosine distance, supporting 10k+ document collections with sub-2-second query response
- **Async Processing**: Dramatiq task queue for background OCR and embedding jobs with retry logic and progress tracking

The implementation follows a phased approach aligned with user story priorities (P1: Text Extraction → P2: Semantic Search → P3: Batch Processing), delivering an MVP with each phase while maintaining production-ready quality standards.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**:
- `fastapi>=0.109.0` - API framework
- `sqlalchemy[asyncio]>=2.0.25` - Async ORM
- `pgvector>=0.2.4` - PostgreSQL vector extension  
- `docling>=1.0.0` - Document parsing
- `paddleocr>=2.7.0` - OCR engine (primary)
- `pytesseract>=0.3.10` - OCR engine (fallback)
- `sentence-transformers>=2.3.0` - Embedding models (NEW)
- `dramatiq[redis]>=1.15.0` - Task queue
- `tiktoken>=0.5.2` - Token counting
- `langdetect>=1.0.9` - Language detection (NEW)

**Storage**: 
- PostgreSQL 14+ with pgvector extension for relational data and vector embeddings
- Local filesystem or S3-compatible storage for original document files
- Redis 6.0+ for Dramatiq task queue and caching

**Testing**: 
- pytest with pytest-asyncio for async tests
- pytest-cov for coverage tracking (80% minimum)
- pytest-mock for service mocking
- Integration tests with real database and models for critical paths

**Target Platform**: 
- Linux/macOS development and deployment
- Docker containers for production
- GPU support optional but recommended for OCR and embedding performance

**Project Type**: Web application (backend API + frontend) - follows existing structure

**Performance Goals**:
- OCR: 2-5 seconds per page (300 DPI scans)
- Embedding: 0.1-0.2 seconds per chunk (GPU, batch size 32)
- Search: < 2 seconds response time for 10k document collections
- End-to-end document processing: < 30 seconds for 20-page typical document
- Concurrent users: 50+ without degradation
- Batch processing: 60% faster than sequential uploads

**Constraints**:
- OCR accuracy: ≥90% for standard quality scans, ≥95% for good quality (300+ DPI)
- Search relevance: Top-5 results must be relevant 80% of the time
- Chunk size: Maximum 500 tokens (hard limit from embedding model context)
- Result limits: Default 10, maximum 100 per search query
- Processing failure rate: < 5% for valid uploads
- System uptime: 99% for upload and search functionality

**Scale/Scope**:
- Initial target: 10k documents, 400k chunks
- Storage: ~14GB total (10GB files + 4GB database)
- Concurrent processing: 4-8 documents simultaneously
- Languages: English and Chinese (requirement)
- Supported formats: PDF and DOCX initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Status: ✅ PASSED (Constitution template not yet filled, assumed standard practices)

Since the project constitution file is still a template, we follow industry-standard best practices for Python FastAPI projects:

**Assumed Principles**:

1. ✅ **Modular Architecture**: Features organized into clear service boundaries
   - Services in `src/ingestion_parsing/services/`
   - Models in `src/storage_indexing/models/`
   - API routes in `src/api/routes/`
   - Clear separation of concerns

2. ✅ **Test-First Development**: Comprehensive test coverage required
   - Unit tests for all services with mocked dependencies
   - Integration tests for critical workflows (upload → OCR → embedding → search)
   - Contract tests for API endpoints
   - Minimum 80% code coverage (project requirement)

3. ✅ **Type Safety**: Full type annotations required
   - Python 3.12 type hints throughout
   - mypy strict mode compliance
   - Pydantic models for API request/response validation

4. ✅ **Database Migrations**: Alembic for schema versioning
   - All schema changes via migrations
   - Rollback strategy documented
   - Migration testing in CI/CD

5. ✅ **Async-First**: Non-blocking I/O throughout
   - FastAPI async endpoints
   - SQLAlchemy async ORM
   - Background tasks via Dramatiq

6. ✅ **Observability**: Structured logging and metrics
   - structlog for JSON-formatted logs
   - Metrics tracked for processing success/failure rates
   - Search performance monitoring

7. ✅ **Security**: Input validation and tenant isolation
   - Pydantic validation for all inputs
   - Tenant-scoped database queries (multi-tenancy)
   - Malware scanning before processing

**No Constitution Violations Detected**

## Project Structure

### Documentation (this feature)

```text
specs/004-ocr-embedding-pipeline/
├── plan.md                  # ✅ This file
├── research.md              # ✅ Phase 0 - Technology decisions
├── data-model.md            # ✅ Phase 1 - Database schema
├── quickstart.md            # ✅ Phase 1 - Developer guide
├── contracts/               # ✅ Phase 1 - API specifications
│   ├── ocr-extraction-api.yaml
│   ├── embedding-api.yaml
│   └── vector-search-api.yaml
└── tasks.md                 # Phase 2 - Generated by /speckit.tasks command
```

### Source Code (repository root)

This is a web application with backend and frontend. The feature primarily impacts backend services with minimal frontend changes for status display.

```text
backend/
├── src/
│   ├── api/
│   │   ├── main.py                           # FastAPI app (existing)
│   │   ├── dependencies.py                    # Existing
│   │   ├── routes/
│   │   │   ├── documents.py                   # ✓ Existing - enhanced for OCR/embeddings
│   │   │   ├── ocr.py                         # ✨ NEW - OCR endpoints
│   │   │   ├── embeddings.py                  # ✨ NEW - Embedding endpoints
│   │   │   ├── search.py                      # ✨ NEW - Vector search endpoints
│   │   │   └── health.py                      # ✓ Existing
│   │   └── middleware/                        # ✓ Existing
│   │
│   ├── ingestion_parsing/
│   │   ├── parsers/
│   │   │   ├── docling_parser.py              # ✓ Existing - enhanced for OCR integration
│   │   │   ├── ocr/                           # ✨ NEW directory
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                    # ✨ NEW - OCR engine interface
│   │   │   │   ├── paddleocr_engine.py        # ✨ NEW - PaddleOCR implementation
│   │   │   │   ├── tesseract_engine.py        # ✨ NEW - Tesseract implementation
│   │   │   │   └── image_preprocessor.py      # ✨ NEW - Image enhancement for OCR
│   │   │   └── pdf_parser.py                  # ✓ Existing
│   │   │
│   │   ├── services/
│   │   │   ├── ocr_service.py                 # ✨ NEW - OCR orchestration
│   │   │   ├── chunking_service.py            # ✓ Existing - enhanced with token-based chunking
│   │   │   ├── embedding_service.py           # ✨ NEW - Embedding generation
│   │   │   ├── batch_service.py               # ✓ Existing - enhanced for OCR/embedding batches
│   │   │   └── upload_service.py              # ✓ Existing
│   │   │
│   │   ├── tasks/                             # ✨ Enhanced - Dramatiq actors
│   │   │   ├── __init__.py
│   │   │   ├── ocr_actor.py                   # ✨ NEW - Background OCR processing
│   │   │   ├── embedding_actor.py             # ✨ NEW - Background embedding generation
│   │   │   └── batch_actor.py                 # ✓ Existing - enhanced
│   │   │
│   │   └── models/                            # Pydantic models
│   │       ├── ocr_request.py                 # ✨ NEW - OCR API schemas
│   │       ├── ocr_response.py                # ✨ NEW
│   │       ├── embedding_request.py           # ✨ NEW - Embedding API schemas
│   │       └── search_request.py              # ✨ NEW - Search API schemas
│   │
│   ├── rag_orchestration/
│   │   ├── services/
│   │   │   └── vector_search_service.py       # ✨ NEW - pgvector similarity search
│   │   └── models/
│   │       └── search_result.py               # ✨ NEW - Search result models
│   │
│   ├── storage_indexing/
│   │   ├── models/                            # SQLAlchemy ORM models
│   │   │   ├── document.py                    # ✓ Existing - add OCR/embedding fields
│   │   │   ├── extracted_text.py              # ✨ NEW - OCR text storage
│   │   │   ├── document_chunk.py              # ✓ Existing - add embedding vector field
│   │   │   ├── processing_job.py              # ✓ Existing - enhance with job types
│   │   │   ├── search_query.py                # ✨ NEW - Search analytics
│   │   │   └── search_result.py               # ✨ NEW - Result tracking
│   │   │
│   │   ├── repositories/
│   │   │   ├── document_repository.py         # ✓ Existing - add OCR/embedding queries
│   │   │   ├── extracted_text_repository.py   # ✨ NEW
│   │   │   ├── chunk_repository.py            # ✓ Existing - add vector queries
│   │   │   └── search_repository.py           # ✨ NEW - Search operations
│   │   │
│   │   └── migrations/
│   │       └── versions/
│   │           ├── XXXX_add_ocr_fields.py     # ✨ NEW - Migration 1
│   │           ├── XXXX_create_extracted_texts.py  # ✨ NEW - Migration 2
│   │           ├── XXXX_add_embedding_fields.py    # ✨ NEW - Migration 3
│   │           ├── XXXX_enhance_processing_jobs.py # ✨ NEW - Migration 4
│   │           └── XXXX_create_search_tables.py    # ✨ NEW - Migration 5
│   │
│   └── shared/
│       ├── config.py                          # ✓ Existing - add OCR/embedding config
│       ├── exceptions.py                      # ✓ Existing - add OCR/search exceptions
│       └── logging_config.py                  # ✓ Existing
│
└── tests/
    ├── unit/
    │   ├── test_ocr_service.py                # ✨ NEW
    │   ├── test_chunking_service.py           # ✓ Existing - enhance
    │   ├── test_embedding_service.py          # ✨ NEW
    │   ├── test_vector_search.py              # ✨ NEW
    │   └── test_language_detection.py         # ✨ NEW
    │
    ├── integration/
    │   ├── test_ocr_pipeline.py               # ✨ NEW - End-to-end OCR flow
    │   ├── test_embedding_pipeline.py         # ✨ NEW - End-to-end embedding flow
    │   ├── test_search_api.py                 # ✨ NEW - Search API integration
    │   └── test_batch_processing.py           # ✓ Existing - enhance
    │
    ├── contract/
    │   ├── test_ocr_api_contract.py           # ✨ NEW - Validate OCR API spec
    │   ├── test_embedding_api_contract.py     # ✨ NEW - Validate Embedding API spec
    │   └── test_search_api_contract.py        # ✨ NEW - Validate Search API spec
    │
    └── fixtures/
        ├── sample_scanned.pdf                 # ✨ NEW - Test document
        ├── sample_mixed_content.pdf           # ✨ NEW - Native + scanned content
        └── sample_chinese.pdf                 # ✨ NEW - Chinese language test

frontend/
├── app/
│   └── documents/
│       └── [id]/
│           ├── ocr-status.tsx                 # ✨ NEW - OCR status display
│           └── search-results.tsx             # ✨ NEW - Search results UI
│
└── components/
    └── search/
        ├── semantic-search-bar.tsx            # ✨ NEW - Search input component
        └── similarity-panel.tsx               # ✨ NEW - Similar docs widget

scripts/
├── download_models.py                         # ✨ NEW - Pre-download embedding models
├── rebuild_embeddings.py                      # ✨ NEW - Regenerate embeddings script
└── test_load.py                               # ✨ NEW - Load testing script
```

**Structure Decision**: 

This feature extends the existing web application structure (`backend/` + `frontend/`) with new services, models, and API endpoints. The decision to enhance existing modules rather than create a separate project maintains consistency with the established architecture while keeping the codebase modular.

Key organizational choices:
1. **OCR parsers** in `ingestion_parsing/parsers/ocr/` - grouped with other parsers
2. **Embedding service** in `ingestion_parsing/services/` - logically part of document processing
3. **Vector search** in `rag_orchestration/services/` - anticipates future RAG features (Phase 2 roadmap)
4. **Search API** as separate route module - distinct from document upload/management

## Complexity Tracking

No constitution violations identified. Table intentionally left empty.

## Implementation Phases

### Phase 0: Research & Planning ✅ COMPLETED

**Deliverables**:
- ✅ `research.md` - Technology choices and rationale
- ✅ `data-model.md` - Database schema design
- ✅ `quickstart.md` - Developer setup guide
- ✅ `contracts/*.yaml` - API specifications (3 files)

**Key Decisions Made**:
1. PaddleOCR as primary OCR engine (superior accuracy for English/Chinese)
2. multilingual-e5-base for embedding model (balance of quality and performance)
3. pgvector for vector storage (co-location with relational data)
4. 500-token chunks with 50-token overlap (spec requirement)
5. Dramatiq for async processing (already in project dependencies)

### Phase 1: Core Text Extraction (P1 - MVP)

**Goal**: Enable uploading documents and extracting text via OCR, making content searchable

**Duration**: 2-3 weeks

**Tasks** (high-level, detailed breakdown in `tasks.md`):

1. **Database Migrations**:
   - Create `extracted_texts` table
   - Add OCR fields to `documents` table
   - Enhance `processing_jobs` for OCR task tracking

2. **OCR Engine Integration**:
   - Implement PaddleOCR engine adapter
   - Implement Tesseract fallback adapter
   - Image preprocessing service (enhance contrast, deskew)
   - Language detection integration

3. **OCR Service**:
   - Orchestrate OCR processing workflow
   - Confidence score calculation
   - Error handling and retry logic
   - Store extracted text with metadata

4. **Docling Parser Enhancement**:
   - Route image-based pages to OCR service
   - Merge native text with OCR text
   - Preserve page structure

5. **Dramatiq Actors**:
   - `ocr_actor.py` for background OCR jobs
   - Task retry with exponential backoff
   - Progress tracking and status updates

6. **API Endpoints**:
   - `POST /documents/{id}/ocr` - Trigger OCR
   - `GET /documents/{id}/ocr/status` - Check progress
   - `GET /documents/{id}/extracted-text` - Retrieve results
   - `POST /documents/batch/ocr` - Batch OCR

7. **Testing**:
   - Unit tests for OCR engines (mocked)
   - Integration tests with sample scanned PDFs
   - Contract tests for OCR API
   - Performance tests (OCR throughput)

**Success Criteria** (from spec):
- ✅ SC-001: 90% OCR accuracy for standard quality scans
- ✅ SC-006: 95% character accuracy for high quality scans
- ✅ SC-010: Extract text from both native and scanned sources

### Phase 2: Embeddings & Search (P2)

**Goal**: Enable semantic search across documents

**Duration**: 2-3 weeks

**Tasks**:

1. **Database Migrations**:
   - Add `embedding_vector` field to `document_chunks`
   - Create HNSW index on embedding vectors
   - Create `search_queries` and `search_results` tables

2. **Chunking Service Enhancement**:
   - Token-based chunking (tiktoken)
   - 500-token limit with 50-token overlap
   - Preserve page/section context
   - Handle document structure (paragraphs, headings)

3. **Embedding Service**:
   - Load multilingual-e5-base model
   - Batch embedding generation
   - GPU acceleration support
   - Store vectors in pgvector format

4. **Vector Search Service**:
   - Similarity search with pgvector (cosine distance)
   - Metadata filtering (tenant, folder, date)
   - Result ranking and scoring
   - Snippet generation with context

5. **Dramatiq Actors**:
   - `embedding_actor.py` for background embedding generation
   - Batch processing optimization
   - Error handling and retry

6. **API Endpoints**:
   - `POST /documents/{id}/embeddings` - Generate embeddings
   - `GET /documents/{id}/embeddings` - Check status
   - `POST /search` - Semantic search
   - `GET /documents/{id}/similar` - Find similar docs
   - `GET /documents/{id}/chunks/{chunk_id}/similar` - Similar chunks

7. **Testing**:
   - Unit tests for chunking and embedding services
   - Integration tests for end-to-end search workflow
   - Contract tests for Search API
   - Performance tests (search latency, relevance)

**Success Criteria** (from spec):
- ✅ SC-002: Document processing < 30 seconds (20-page doc)
- ✅ SC-003: 80% relevance in top-5 results
- ✅ SC-005: 70% success rate for semantic queries
- ✅ SC-007: Search < 2 seconds for 10k documents

### Phase 3: Batch Processing (P3)

**Goal**: Efficiently process multiple documents simultaneously

**Duration**: 1-2 weeks

**Tasks**:

1. **Batch Service Enhancement**:
   - Multi-document upload handling
   - Folder structure preservation
   - Parallel processing coordination
   - Aggregate progress tracking

2. **Dramatiq Actors**:
   - `batch_actor.py` for orchestrating batch jobs
   - Individual document task spawning
   - Progress aggregation
   - Batch completion notification

3. **API Endpoints**:
   - Enhance existing `/documents` endpoint for multi-file upload
   - `POST /documents/batch/ocr` - Batch OCR
   - `POST /documents/batch/embeddings` - Batch embeddings
   - `GET /documents/batch/{batch_id}/status` - Batch progress

4. **Frontend Components** (minimal):
   - Batch upload progress UI
   - Status dashboard for batch jobs

5. **Testing**:
   - Integration tests with 20-100 document batches
   - Performance tests (parallel vs sequential)
   - Error handling tests (partial batch failures)

**Success Criteria** (from spec):
- ✅ SC-004: Successfully process 100 documents in batch
- ✅ SC-011: 60% faster than sequential processing
- ✅ SC-012: 50+ concurrent users without degradation

### Phase 4: Monitoring & Optimization

**Goal**: Production readiness and performance tuning

**Duration**: 1 week

**Tasks**:

1. **Monitoring Dashboard**:
   - Processing success/failure rates
   - Average processing times
   - Search performance metrics
   - Queue depth and worker utilization

2. **Performance Optimization**:
   - HNSW index tuning (m, ef_construction parameters)
   - Batch size optimization for embeddings
   - Database query optimization
   - Caching strategy for popular searches

3. **Error Analytics**:
   - Failure categorization (transient vs permanent)
   - Automatic retry tuning
   - Dead letter queue monitoring
   - User-facing error messages

4. **Documentation**:
   - API documentation (OpenAPI)
   - Runbook for common issues
   - Performance tuning guide
   - Deployment guide

**Success Criteria** (from spec):
- ✅ SC-008: 99% uptime
- ✅ SC-009: <5% processing failure rate

## Dependencies & Integration Points

### Internal Dependencies

1. **Existing Upload Service**: Used for document ingestion before OCR/embedding
2. **Malware Scanner**: Must scan documents before processing (security requirement)
3. **Storage Service**: Retrieve original files for OCR processing
4. **Authentication**: Tenant/user context for multi-tenancy and permissions

### External Dependencies

1. **PostgreSQL with pgvector**: Vector storage and similarity search
2. **Redis**: Task queue backend for Dramatiq
3. **PaddleOCR Models**: Downloaded on first use (~500MB)
4. **Embedding Models**: Downloaded from HuggingFace on first use (~1GB)

### Integration Considerations

- **Backward Compatibility**: Existing documents without OCR/embeddings remain accessible
- **Incremental Processing**: Documents can be OCR'd/embedded after initial upload
- **Fallback Behavior**: If embeddings unavailable, fall back to keyword search (future enhancement)
- **Multi-Tenancy**: All data strictly scoped by `tenant_id` (existing pattern)

## Risk Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PaddleOCR accuracy insufficient for production | High | Low | Benchmark on real documents; Tesseract fallback; Manual review queue |
| Vector search performance degradation at scale | High | Medium | HNSW index tuning; Caching popular queries; Horizontal scaling |
| Embedding model size causes OOM | Medium | Medium | Use base model (768-dim); Batch size tuning; GPU with larger VRAM |
| OCR processing time too slow for UX | Medium | Medium | GPU acceleration; Parallel processing; Status polling UI |
| Language detection inaccurate | Low | Medium | Default to English; User language hints; Confidence thresholds |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Dramatiq worker crashes under load | High | Low | Resource limits; Health checks; Auto-restart; Circuit breaker |
| Database storage exceeds capacity | Medium | Medium | Monitor usage; Archive old embeddings; Compression |
| Model downloads fail in production | Medium | Low | Pre-download in Docker image; Local model cache; Retry logic |
| Search results not relevant (user dissatisfaction) | High | Medium | Relevance testing; Feedback mechanism; Model tuning |

## Success Metrics & Monitoring

### Key Performance Indicators (KPIs)

1. **Processing Metrics**:
   - OCR success rate: Target 95%
   - Embedding generation success rate: Target 95%
   - Average processing time: < 30 seconds per document

2. **Search Metrics**:
   - Search latency p50/p95/p99: Target < 500ms / 1s / 2s
   - Search relevance (user clicks on result): Target > 70%
   - Searches per day: Track growth

3. **System Health**:
   - API uptime: Target 99%
   - Worker uptime: Target 99%
   - Database connection pool utilization: < 80%
   - Queue depth: < 100 pending jobs

### Monitoring Implementation

- **Logs**: Structured JSON logs with correlation IDs
- **Metrics**: Prometheus metrics exposed on `/metrics`
- **Alerts**: PagerDuty/Slack for critical failures
- **Dashboards**: Grafana for real-time monitoring

## Rollout Strategy

### Development → Staging → Production

1. **Development** (local + CI/CD):
   - All tests pass
   - Code review approved
   - 80% code coverage achieved

2. **Staging**:
   - Deploy with 100 test documents
   - Run load tests (50 concurrent users)
   - Manual QA testing
   - Performance benchmark validation

3. **Production Rollout**:
   - Phase 1 (P1): Enable for 10% of users (canary)
   - Monitor for 48 hours
   - Phase 2 (P2): Enable for 50% of users
   - Monitor for 48 hours  
   - Phase 3 (Full): Enable for 100% of users

### Feature Flags

- `ENABLE_OCR_PROCESSING`: Toggle OCR feature
- `ENABLE_SEMANTIC_SEARCH`: Toggle vector search
- `ENABLE_BATCH_UPLOAD`: Toggle batch processing
- `OCR_ENGINE`: Switch between paddleocr/tesseract
- `EMBEDDING_MODEL`: Switch embedding models

## Post-Launch

### Iteration Plan

1. **Week 1-2**: Monitor production metrics, fix critical bugs
2. **Week 3-4**: Performance tuning based on real usage patterns
3. **Month 2**: User feedback analysis, relevance improvements
4. **Month 3**: Additional language support (if needed)

### Future Enhancements (Out of Scope)

- Hybrid search (BM25 + vector)
- Query expansion with LLM
- Document classification/tagging
- Multi-modal embeddings (text + images)
- GraphRAG (document relationships) - **Planned for future phase**
- Real-time collaborative editing

## Appendix

### Key Files Reference

- **Specification**: [spec.md](./spec.md) - User requirements and success criteria
- **Research**: [research.md](./research.md) - Technology decisions and rationale  
- **Data Model**: [data-model.md](./data-model.md) - Database schema and entities
- **Quickstart**: [quickstart.md](./quickstart.md) - Developer setup guide
- **API Contracts**:
  - [OCR API](./contracts/ocr-extraction-api.yaml)
  - [Embedding API](./contracts/embedding-api.yaml)
  - [Search API](./contracts/vector-search-api.yaml)

### Related Documentation

- [FRONTEND_INTEGRATION.md](../../docs/FRONTEND_INTEGRATION.md) - Frontend integration guide
- [PRODUCTION_DEPLOY.md](../../docs/PRODUCTION_DEPLOY.md) - Deployment procedures
- [MALWARE_SCANNING.md](../../docs/MALWARE_SCANNING.md) - Security scanning details

### Next Command

After reviewing this plan, generate detailed implementation tasks:

```bash
/speckit.tasks
```

This will create `tasks.md` with specific, actionable tasks for each phase including:
- Acceptance criteria per task
- Dependencies and ordering
- Estimated effort
- Assigned components

---

**Plan Status**: ✅ **COMPLETE** - Ready for task generation and implementation  
**Last Updated**: 2026-01-11  
**Reviewers**: AI Platform Team
