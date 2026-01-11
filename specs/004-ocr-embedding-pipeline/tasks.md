# Tasks: OCR and Embedding Pipeline

**Feature**: 004-ocr-embedding-pipeline  
**Input**: Design documents from `/specs/004-ocr-embedding-pipeline/`  
**Prerequisites**: ✅ plan.md, spec.md, research.md, data-model.md, contracts/ all available

**Tests**: Test tasks included based on project requirements (80% coverage minimum)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application following the structure in plan.md:
- Backend: `src/` (at repository root)
- Frontend: `frontend/src/`
- Tests: `tests/`
- Migrations: `src/storage_indexing/migrations/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [x] T001 Add new dependencies to pyproject.toml: sentence-transformers>=2.3.0, paddleocr>=2.7.0, langdetect>=1.0.9, paddlepaddle-gpu>=2.6.0
- [x] T002 [P] Install and verify pgvector extension is available in PostgreSQL database
- [x] T003 [P] Create directory structure for OCR parsers at src/ingestion_parsing/parsers/ocr/
- [x] T004 [P] Create directory structure for new models at src/rag_orchestration/services/
- [x] T005 [P] Update .env.example with OCR and embedding configuration variables (OCR_ENGINE, OCR_LANGUAGES, EMBEDDING_MODEL, etc.)
- [x] T006 Download embedding model (multilingual-e5-base) to cache: create scripts/download_models.py
- [x] T007 [P] Create test fixtures directory and add sample documents: tests/fixtures/sample_scanned.pdf, sample_mixed_content.pdf, sample_chinese.pdf
- [x] T008 [P] Update src/shared/config.py to add OCR and embedding settings from environment

**Checkpoint**: ✅ Development environment ready with all dependencies and structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations

- [x] T009 Create migration for OCR fields in documents table: src/storage_indexing/migrations/versions/004_add_ocr_fields.py
- [x] T010 Create migration for extracted_texts table: src/storage_indexing/migrations/versions/005_create_extracted_texts.py
- [x] T011 Create migration for embedding fields in document_chunks: src/storage_indexing/migrations/versions/006_add_embedding_fields.py
- [x] T012 Create migration for enhanced processing_jobs table: src/storage_indexing/migrations/versions/007_enhance_processing_jobs.py
- [x] T013 Create migration for search_queries and search_results tables: src/storage_indexing/migrations/versions/008_create_search_tables.py
- [ ] T014 Run all migrations and verify database schema: alembic upgrade head

### ORM Models (SQLAlchemy)

- [x] T015 [P] Enhance Document model with OCR/embedding fields in src/storage_indexing/models/document.py
- [x] T016 [P] Create ExtractedText model in src/storage_indexing/models/extracted_text.py
- [x] T017 [P] Enhance DocumentChunk model with embedding vector field in src/storage_indexing/models/document_chunk.py
- [x] T018 [P] Enhance ProcessingJob model with job types in src/storage_indexing/models/processing_job.py
- [x] T019 [P] Create SearchQuery model in src/storage_indexing/models/search_query.py
- [x] T020 [P] Create SearchResult model in src/storage_indexing/models/search_result.py
- [x] T021 Update src/storage_indexing/models/__init__.py to export all new models

### Repositories

- [ ] T022 [P] Create ExtractedTextRepository in src/storage_indexing/repositories/extracted_text_repository.py
- [ ] T023 [P] Enhance DocumentRepository with OCR/embedding queries in src/storage_indexing/repositories/document_repository.py
- [ ] T024 [P] Enhance ChunkRepository with vector queries in src/storage_indexing/repositories/chunk_repository.py
- [ ] T025 [P] Create SearchRepository in src/storage_indexing/repositories/search_repository.py

### Pydantic Schemas

- [ ] T026 [P] Create OCR request/response schemas in src/ingestion_parsing/models/ocr_request.py and ocr_response.py
- [ ] T027 [P] Create embedding request/response schemas in src/ingestion_parsing/models/embedding_request.py and embedding_response.py
- [ ] T028 [P] Create search request/response schemas in src/ingestion_parsing/models/search_request.py and search_response.py

### Shared Exception Classes

- [ ] T029 [P] Add OCR-specific exceptions to src/shared/exceptions.py (OcrProcessingError, UnsupportedFormatError, etc.)
- [ ] T030 [P] Add embedding exceptions to src/shared/exceptions.py (EmbeddingGenerationError, ModelLoadError, etc.)
- [ ] T031 [P] Add search exceptions to src/shared/exceptions.py (SearchServiceError, NoEmbeddingsError, etc.)

**Checkpoint**: Foundation ready - all database tables, models, and shared infrastructure complete. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Upload and Extract Text from Scanned Documents (Priority: P1) 🎯 MVP

**Goal**: Enable uploading scanned documents and extracting text via OCR, making content searchable

**Independent Test**: Upload a scanned PDF → verify text is extracted and stored → confirm document is searchable

### Unit Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T032 [P] [US1] Unit test for PaddleOCREngine in tests/unit/test_paddleocr_engine.py
- [ ] T033 [P] [US1] Unit test for TesseractEngine in tests/unit/test_tesseract_engine.py
- [ ] T034 [P] [US1] Unit test for ImagePreprocessor in tests/unit/test_image_preprocessor.py
- [ ] T035 [P] [US1] Unit test for OcrService in tests/unit/test_ocr_service.py (mock engines)
- [ ] T036 [P] [US1] Unit test for language detection in tests/unit/test_language_detection.py

### Implementation: OCR Engine Foundation

- [ ] T037 [P] [US1] Create base OCR engine interface in src/ingestion_parsing/parsers/ocr/base.py
- [ ] T038 [P] [US1] Implement PaddleOCR engine adapter in src/ingestion_parsing/parsers/ocr/paddleocr_engine.py
- [ ] T039 [P] [US1] Implement Tesseract engine adapter in src/ingestion_parsing/parsers/ocr/tesseract_engine.py
- [ ] T040 [P] [US1] Implement image preprocessor (contrast, deskew) in src/ingestion_parsing/parsers/ocr/image_preprocessor.py
- [ ] T041 [US1] Create OCR engine factory in src/ingestion_parsing/parsers/ocr/__init__.py (depends on T037-T040)

### Implementation: OCR Service

- [ ] T042 [US1] Implement OcrService orchestration in src/ingestion_parsing/services/ocr_service.py
- [ ] T043 [US1] Add language detection integration using langdetect in src/ingestion_parsing/services/ocr_service.py
- [ ] T044 [US1] Implement confidence score calculation and low-confidence flagging in src/ingestion_parsing/services/ocr_service.py
- [ ] T045 [US1] Add error handling and retry logic for OCR failures in src/ingestion_parsing/services/ocr_service.py

### Implementation: Parser Integration

- [ ] T046 [US1] Enhance Docling parser to detect scanned vs native content in src/ingestion_parsing/parsers/docling_parser.py
- [ ] T047 [US1] Route image-based pages to OCR service in src/ingestion_parsing/parsers/docling_parser.py
- [ ] T048 [US1] Merge native text with OCR text while preserving structure in src/ingestion_parsing/parsers/docling_parser.py

### Implementation: Background Tasks

- [ ] T049 [US1] Create Dramatiq actor for OCR processing in src/ingestion_parsing/tasks/ocr_actor.py
- [ ] T050 [US1] Implement task retry with exponential backoff in src/ingestion_parsing/tasks/ocr_actor.py
- [ ] T051 [US1] Add progress tracking and status updates to ProcessingJob in src/ingestion_parsing/tasks/ocr_actor.py

### Implementation: API Endpoints

- [ ] T052 [US1] Create OCR routes module in src/api/routes/ocr.py
- [ ] T053 [US1] Implement POST /api/v1/documents/{id}/ocr endpoint in src/api/routes/ocr.py
- [ ] T054 [US1] Implement GET /api/v1/documents/{id}/ocr/status endpoint in src/api/routes/ocr.py
- [ ] T055 [US1] Implement GET /api/v1/documents/{id}/extracted-text endpoint in src/api/routes/ocr.py
- [ ] T056 [US1] Implement POST /api/v1/documents/batch/ocr endpoint in src/api/routes/ocr.py
- [ ] T057 [US1] Register OCR routes in src/api/main.py

### Integration Tests for User Story 1

- [ ] T058 [US1] Contract test for OCR API endpoints in tests/contract/test_ocr_api_contract.py
- [ ] T059 [US1] Integration test for end-to-end OCR pipeline in tests/integration/test_ocr_pipeline.py
- [ ] T060 [US1] Integration test with sample scanned PDF in tests/integration/test_ocr_pipeline.py
- [ ] T061 [US1] Integration test with mixed content (native + scanned) in tests/integration/test_ocr_pipeline.py
- [ ] T062 [US1] Integration test for Chinese document OCR in tests/integration/test_ocr_pipeline.py

### User Story 1 Polish

- [ ] T063 [US1] Add logging for all OCR operations with structured context
- [ ] T064 [US1] Add metrics tracking (OCR success rate, average confidence, processing time)
- [ ] T065 [US1] Verify OCR accuracy meets ≥90% threshold with test documents

**Checkpoint**: User Story 1 complete - Users can upload scanned documents and extract text with OCR. Test independently before proceeding.

---

## Phase 4: User Story 2 - Semantic Document Search (Priority: P2)

**Goal**: Enable semantic search across documents using natural language queries

**Independent Test**: Upload documents with embeddings → search with natural language query → verify relevant results returned

### Unit Tests for User Story 2

- [ ] T066 [P] [US2] Unit test for ChunkingService with token counting in tests/unit/test_chunking_service.py
- [ ] T067 [P] [US2] Unit test for EmbeddingService (mock model) in tests/unit/test_embedding_service.py
- [ ] T068 [P] [US2] Unit test for VectorSearchService (test database) in tests/unit/test_vector_search.py
- [ ] T069 [P] [US2] Unit test for similarity scoring in tests/unit/test_vector_search.py

### Implementation: Chunking Service

- [ ] T070 [P] [US2] Enhance ChunkingService with tiktoken integration in src/ingestion_parsing/services/chunking_service.py
- [ ] T071 [P] [US2] Implement 500-token chunking with 50-token overlap in src/ingestion_parsing/services/chunking_service.py
- [ ] T072 [P] [US2] Preserve page numbers and section context in chunks in src/ingestion_parsing/services/chunking_service.py
- [ ] T073 [P] [US2] Implement semantic boundary detection (paragraph/sentence splits) in src/ingestion_parsing/services/chunking_service.py

### Implementation: Embedding Service

- [ ] T074 [US2] Create EmbeddingService in src/ingestion_parsing/services/embedding_service.py
- [ ] T075 [US2] Load multilingual-e5-base model with caching in src/ingestion_parsing/services/embedding_service.py
- [ ] T076 [US2] Implement batch embedding generation (batch size 32) in src/ingestion_parsing/services/embedding_service.py
- [ ] T077 [US2] Add GPU acceleration support in src/ingestion_parsing/services/embedding_service.py
- [ ] T078 [US2] Implement error handling for embedding failures in src/ingestion_parsing/services/embedding_service.py

### Implementation: Vector Search Service

- [ ] T079 [US2] Create VectorSearchService in src/rag_orchestration/services/vector_search_service.py
- [ ] T080 [US2] Implement similarity search with pgvector cosine distance in src/rag_orchestration/services/vector_search_service.py
- [ ] T081 [US2] Add metadata filtering (tenant_id, folder, date range) in src/rag_orchestration/services/vector_search_service.py
- [ ] T082 [US2] Implement result ranking and scoring in src/rag_orchestration/services/vector_search_service.py
- [ ] T083 [US2] Generate result snippets with context highlighting in src/rag_orchestration/services/vector_search_service.py
- [ ] T084 [US2] Implement pagination (default 10, max 100 results) in src/rag_orchestration/services/vector_search_service.py

### Implementation: Background Tasks

- [ ] T085 [US2] Create Dramatiq actor for embedding generation in src/ingestion_parsing/tasks/embedding_actor.py
- [ ] T086 [US2] Implement batch processing optimization in src/ingestion_parsing/tasks/embedding_actor.py
- [ ] T087 [US2] Add retry logic for embedding failures in src/ingestion_parsing/tasks/embedding_actor.py

### Implementation: API Endpoints

- [ ] T088 [US2] Create embeddings routes module in src/api/routes/embeddings.py
- [ ] T089 [US2] Implement POST /api/v1/documents/{id}/embeddings endpoint in src/api/routes/embeddings.py
- [ ] T090 [US2] Implement GET /api/v1/documents/{id}/embeddings endpoint in src/api/routes/embeddings.py
- [ ] T091 [US2] Implement GET /api/v1/documents/{id}/chunks endpoint in src/api/routes/embeddings.py
- [ ] T092 [US2] Implement GET /api/v1/embeddings/models endpoint in src/api/routes/embeddings.py
- [ ] T093 [US2] Register embeddings routes in src/api/main.py

- [ ] T094 [US2] Create search routes module in src/api/routes/search.py
- [ ] T095 [US2] Implement POST /api/v1/search endpoint in src/api/routes/search.py
- [ ] T096 [US2] Implement GET /api/v1/search/history endpoint in src/api/routes/search.py
- [ ] T097 [US2] Register search routes in src/api/main.py

### Integration Tests for User Story 2

- [ ] T098 [US2] Contract test for Embedding API endpoints in tests/contract/test_embedding_api_contract.py
- [ ] T099 [US2] Contract test for Search API endpoints in tests/contract/test_search_api_contract.py
- [ ] T100 [US2] Integration test for end-to-end embedding pipeline in tests/integration/test_embedding_pipeline.py
- [ ] T101 [US2] Integration test for semantic search with sample queries in tests/integration/test_search_api.py
- [ ] T102 [US2] Integration test for multilingual search (English and Chinese) in tests/integration/test_search_api.py
- [ ] T103 [US2] Performance test for search latency (<2 seconds for 10k docs) in tests/integration/test_search_performance.py

### User Story 2 Polish

- [ ] T104 [US2] Tune HNSW index parameters (m=16, ef_construction=64) for optimal performance
- [ ] T105 [US2] Add logging for search operations with query text and results
- [ ] T106 [US2] Add metrics tracking (search latency, relevance scores, result counts)
- [ ] T107 [US2] Verify search relevance meets 80% top-5 threshold with test queries

**Checkpoint**: User Story 2 complete - Users can perform semantic search across documents. Both US1 and US2 should work independently.

---

## Phase 5: User Story 3 - Batch Document Processing (Priority: P3)

**Goal**: Enable efficient processing of multiple documents simultaneously

**Independent Test**: Upload 20+ documents as batch → verify all processed in parallel → confirm 60% faster than sequential

### Unit Tests for User Story 3

- [ ] T108 [P] [US3] Unit test for batch service orchestration in tests/unit/test_batch_service.py
- [ ] T109 [P] [US3] Unit test for progress aggregation in tests/unit/test_batch_service.py

### Implementation: Batch Service Enhancement

- [ ] T110 [US3] Enhance BatchService for multi-document uploads in src/ingestion_parsing/services/batch_service.py
- [ ] T111 [US3] Implement folder structure preservation in src/ingestion_parsing/services/batch_service.py
- [ ] T112 [US3] Add parallel processing coordination in src/ingestion_parsing/services/batch_service.py
- [ ] T113 [US3] Implement aggregate progress tracking in src/ingestion_parsing/services/batch_service.py

### Implementation: Background Tasks

- [ ] T114 [US3] Enhance batch_actor for OCR/embedding orchestration in src/ingestion_parsing/tasks/batch_actor.py
- [ ] T115 [US3] Implement individual document task spawning in src/ingestion_parsing/tasks/batch_actor.py
- [ ] T116 [US3] Add batch completion notification in src/ingestion_parsing/tasks/batch_actor.py

### Implementation: API Endpoints

- [ ] T117 [US3] Enhance POST /api/v1/documents endpoint for multi-file upload in src/api/routes/documents.py
- [ ] T118 [US3] Implement POST /api/v1/documents/batch/embeddings endpoint in src/api/routes/embeddings.py
- [ ] T119 [US3] Implement GET /api/v1/documents/batch/{batch_id}/status endpoint in src/api/routes/documents.py

### Implementation: Frontend (Minimal)

- [ ] T120 [P] [US3] Create batch upload progress component in frontend/components/upload/batch-progress.tsx
- [ ] T121 [P] [US3] Add batch status dashboard in frontend/app/documents/batch-status.tsx

### Integration Tests for User Story 3

- [ ] T122 [US3] Integration test for batch upload (20 documents) in tests/integration/test_batch_processing.py
- [ ] T123 [US3] Integration test for partial batch failure handling in tests/integration/test_batch_processing.py
- [ ] T124 [US3] Integration test for folder structure preservation in tests/integration/test_batch_processing.py
- [ ] T125 [US3] Performance test verifying 60% speedup vs sequential in tests/integration/test_batch_performance.py

### User Story 3 Polish

- [ ] T126 [US3] Add logging for batch operations with batch_id context
- [ ] T127 [US3] Add metrics tracking (batch size, parallel efficiency, failure rates)
- [ ] T128 [US3] Verify batch processing meets 60% speedup threshold

**Checkpoint**: User Story 3 complete - Users can efficiently process document batches. All three stories (US1, US2, US3) should work independently.

---

## Phase 6: User Story 4 - Similar Document Discovery (Priority: P3)

**Goal**: Enable finding documents similar to a given document without crafting queries

**Independent Test**: Select a document → request similar documents → verify semantically related results returned

### Unit Tests for User Story 4

- [ ] T129 [P] [US4] Unit test for document similarity scoring in tests/unit/test_vector_search.py
- [ ] T130 [P] [US4] Unit test for similarity reason generation in tests/unit/test_vector_search.py

### Implementation: Similarity Service

- [ ] T131 [US4] Add document similarity methods to VectorSearchService in src/rag_orchestration/services/vector_search_service.py
- [ ] T132 [US4] Implement chunk-level similarity in src/rag_orchestration/services/vector_search_service.py
- [ ] T133 [US4] Generate similarity reasons/explanations in src/rag_orchestration/services/vector_search_service.py

### Implementation: API Endpoints

- [ ] T134 [US4] Implement GET /api/v1/documents/{id}/similar endpoint in src/api/routes/search.py
- [ ] T135 [US4] Implement GET /api/v1/documents/{id}/chunks/{chunk_id}/similar endpoint in src/api/routes/search.py

### Implementation: Frontend (Minimal)

- [ ] T136 [P] [US4] Create similarity panel component in frontend/components/search/similarity-panel.tsx
- [ ] T137 [P] [US4] Add "Find Similar" button to document view in frontend/app/documents/[id]/page.tsx

### Integration Tests for User Story 4

- [ ] T138 [US4] Contract test for similarity API endpoints in tests/contract/test_search_api_contract.py
- [ ] T139 [US4] Integration test for document similarity in tests/integration/test_similarity_search.py
- [ ] T140 [US4] Integration test for chunk similarity in tests/integration/test_similarity_search.py

### User Story 4 Polish

- [ ] T141 [US4] Add logging for similarity requests
- [ ] T142 [US4] Add metrics tracking (similarity query latency, average similarity scores)

**Checkpoint**: User Story 4 complete - Users can discover similar documents. All four stories should work independently.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Performance Optimization

- [ ] T143 [P] Optimize HNSW index parameters based on real data (may need m=32, ef_construction=128)
- [ ] T144 [P] Implement search result caching in Redis for popular queries
- [ ] T145 [P] Add database query optimization and connection pooling tuning

### Monitoring & Observability

- [ ] T146 [P] Create Prometheus metrics endpoints for OCR, embedding, and search operations
- [ ] T147 [P] Add detailed structured logging with correlation IDs across all services
- [ ] T148 [P] Create monitoring dashboard configuration (Grafana) in docs/monitoring/

### Error Handling & Reliability

- [ ] T149 [P] Implement circuit breaker pattern for OCR/embedding failures
- [ ] T150 [P] Add dead letter queue monitoring and alerting
- [ ] T151 [P] Enhance error messages for user-facing clarity

### Security & Compliance

- [ ] T152 [P] Verify tenant isolation in all search queries
- [ ] T153 [P] Add rate limiting for search endpoints
- [ ] T154 [P] Audit logging for document access and searches

### Documentation

- [ ] T155 [P] Update API documentation (OpenAPI specs) in docs/api/
- [ ] T156 [P] Create runbook for common OCR/search issues in docs/runbooks/
- [ ] T157 [P] Update README.md with OCR and search feature descriptions
- [ ] T158 [P] Validate quickstart.md with fresh environment setup

### Testing

- [ ] T159 [P] Add performance benchmarks for all critical paths
- [ ] T160 [P] Run full test suite and verify 80% code coverage
- [ ] T161 [P] Add load testing for 50+ concurrent users
- [ ] T162 [P] Test with realistic document volumes (100+ documents, 10k+ chunks)

### Deployment Preparation

- [ ] T163 Update Docker configuration for new dependencies (PaddleOCR, embedding models)
- [ ] T164 [P] Create migration rollback documentation
- [ ] T165 [P] Set up feature flags for gradual rollout (ENABLE_OCR_PROCESSING, ENABLE_SEMANTIC_SEARCH, etc.)
- [ ] T166 Create deployment checklist in docs/PRODUCTION_DEPLOY.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if multiple developers)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **No dependencies on other stories**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for document text extraction
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 and US2 but independently testable
- **User Story 4 (P3)**: Can start after US2 completion - Requires embeddings from US2

### Within Each User Story

- **Tests** MUST be written and FAIL before implementation
- **Models** before services
- **Services** before endpoints
- **Core implementation** before integration
- **Story complete** before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T002, T003, T004, T005, T007, T008 can all run in parallel

**Foundational Phase (Phase 2)**:
- All migration tasks (T009-T013) can run sequentially or in careful order
- All ORM models (T015-T020) can run in parallel after migrations
- All repositories (T022-T025) can run in parallel after ORM models
- All Pydantic schemas (T026-T028) can run in parallel
- All exception classes (T029-T031) can run in parallel

**User Story 1 (Phase 3)**:
- All unit tests (T032-T036) can run in parallel
- OCR engine implementations (T038-T040) can run in parallel
- API endpoint implementations (T053-T056) can run in parallel

**User Story 2 (Phase 4)**:
- All unit tests (T066-T069) can run in parallel
- Chunking enhancements (T070-T073) can run in parallel (same file but independent methods)
- API endpoints for embeddings (T089-T092) can run in parallel
- API endpoints for search (T095-T096) can run in parallel
- Integration tests (T098-T103) can run in parallel

**User Story 3 (Phase 5)**:
- Unit tests (T108-T109) can run in parallel
- Frontend components (T120-T121) can run in parallel
- Integration tests (T122-T125) can run in parallel

**User Story 4 (Phase 6)**:
- Unit tests (T129-T130) can run in parallel
- Frontend components (T136-T137) can run in parallel
- Integration tests (T139-T140) can run in parallel

**Polish Phase (Phase 7)**:
- Most tasks (T143-T162) can run in parallel as they affect different areas

---

## Parallel Example: User Story 1 (OCR Extraction)

Once Foundational phase is complete, launch User Story 1 tasks:

```bash
# Launch unit tests in parallel:
Task T032: "Unit test for PaddleOCREngine"
Task T033: "Unit test for TesseractEngine"
Task T034: "Unit test for ImagePreprocessor"
Task T035: "Unit test for OcrService"
Task T036: "Unit test for language detection"

# Launch OCR engine implementations in parallel:
Task T038: "Implement PaddleOCR engine adapter"
Task T039: "Implement Tesseract engine adapter"
Task T040: "Implement image preprocessor"

# After engines complete, launch API endpoints in parallel:
Task T053: "POST /api/v1/documents/{id}/ocr"
Task T054: "GET /api/v1/documents/{id}/ocr/status"
Task T055: "GET /api/v1/documents/{id}/extracted-text"
Task T056: "POST /api/v1/documents/batch/ocr"
```

---

## Parallel Example: User Story 2 (Semantic Search)

After US1 completes (or in parallel if separate team):

```bash
# Launch unit tests in parallel:
Task T066: "Unit test for ChunkingService"
Task T067: "Unit test for EmbeddingService"
Task T068: "Unit test for VectorSearchService"
Task T069: "Unit test for similarity scoring"

# Launch embedding API endpoints in parallel:
Task T089: "POST /api/v1/documents/{id}/embeddings"
Task T090: "GET /api/v1/documents/{id}/embeddings"
Task T091: "GET /api/v1/documents/{id}/chunks"
Task T092: "GET /api/v1/embeddings/models"

# Launch search API endpoints in parallel:
Task T095: "POST /api/v1/search"
Task T096: "GET /api/v1/search/history"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Deliver minimum viable product with OCR text extraction

1. ✅ Complete Phase 1: Setup (T001-T008)
2. ✅ Complete Phase 2: Foundational (T009-T031) - **CRITICAL BLOCKING PHASE**
3. ✅ Complete Phase 3: User Story 1 (T032-T065)
4. **STOP and VALIDATE**: Test User Story 1 independently with real documents
5. Deploy/demo OCR extraction capability

**MVP Deliverable**: Users can upload scanned documents and extract text with OCR. Text is stored and basic document search works.

**Estimated Effort**: 2-3 weeks for 1-2 developers

---

### Incremental Delivery Strategy

**Delivery 1: OCR Text Extraction (MVP)**
- Complete Setup + Foundational + User Story 1
- **Test independently**: Upload scanned PDFs → extract text → verify accuracy
- **Deploy**: Enable OCR for production users
- **Value**: Previously unsearchable scanned documents become searchable

**Delivery 2: Semantic Search**
- Add User Story 2 (T066-T107)
- **Test independently**: Semantic search queries → verify relevant results
- **Deploy**: Enable semantic search feature
- **Value**: Users find documents using natural language without exact keywords

**Delivery 3: Batch Processing**
- Add User Story 3 (T108-T128)
- **Test independently**: Upload 20+ document batch → verify parallel processing
- **Deploy**: Enable batch upload UI
- **Value**: 60% faster document processing for large collections

**Delivery 4: Similar Documents**
- Add User Story 4 (T129-T142)
- **Test independently**: Select document → find similar → verify relevance
- **Deploy**: Enable "Find Similar" feature
- **Value**: Content discovery without crafting queries

**Delivery 5: Production Hardening**
- Complete Phase 7: Polish (T143-T166)
- **Deploy**: Production-ready with monitoring, performance tuning, documentation

---

### Parallel Team Strategy

With 3-4 developers after Foundational phase complete:

**Week 1-2: Parallel User Stories**
- Developer A: User Story 1 (OCR) - T032-T065
- Developer B: User Story 2 (Search) - T066-T107
- Developer C: User Story 3 (Batch) - T108-T128
- Developer D: User Story 4 (Similar) - T129-T142

**Week 3: Integration & Testing**
- All developers: Cross-story integration testing
- Verify each story works independently
- Verify stories work together when combined

**Week 4: Polish & Deploy**
- All developers: Phase 7 tasks in parallel
- Performance testing, monitoring, documentation
- Production deployment

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 23 tasks (BLOCKING)
- **Phase 3 (User Story 1 - OCR)**: 34 tasks
- **Phase 4 (User Story 2 - Search)**: 42 tasks
- **Phase 5 (User Story 3 - Batch)**: 21 tasks
- **Phase 6 (User Story 4 - Similar)**: 14 tasks
- **Phase 7 (Polish)**: 24 tasks

**Total Tasks**: 166 tasks

**Parallel Opportunities Identified**: 
- 45+ tasks marked [P] can run in parallel within their phases
- 4 user stories can be developed in parallel after Foundational phase
- Estimated 30-40% time savings with parallel execution

**Test Coverage**: 
- 30+ unit test tasks
- 15+ integration test tasks
- 10+ contract test tasks
- Total: 55+ test tasks ensuring 80%+ coverage

**MVP Scope (Recommended Start)**: 
- Phase 1 (8 tasks) + Phase 2 (23 tasks) + Phase 3 User Story 1 (34 tasks) = **65 tasks**
- Delivers: OCR text extraction from scanned documents
- Independent value: Makes previously unsearchable documents searchable

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- **Each user story** should be independently completable and testable
- **Verify tests fail** before implementing (TDD approach)
- **Commit** after each task or logical group of related tasks
- **Stop at checkpoints** to validate story independently before proceeding
- **File paths** are exact - follow plan.md structure
- **Avoid**: vague tasks, same-file conflicts, cross-story dependencies that break independence

---

**Generated**: 2026-01-11  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Next Step**: Begin Phase 1 (Setup) tasks T001-T008
