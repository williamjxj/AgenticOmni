# Tasks: Document Upload and Parsing

**Input**: Design documents from `/specs/002-doc-upload-parsing/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included as this is a critical feature requiring comprehensive testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/` at repository root
- **Frontend**: `frontend/` at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for document upload feature

- [x] T001 Create ingestion_parsing module structure with parsers/, services/, storage/, tasks/, models/ directories
- [x] T002 Create tests/fixtures/sample_documents/ directory and add sample PDF, DOCX, TXT files
- [x] T003 [P] Create tests/unit/test_parsers.py, test_upload_service.py, test_chunking_service.py, test_validators.py files
- [x] T004 [P] Create tests/integration/test_upload_api.py, test_parsing_workflow.py, test_document_api.py files
- [x] T005 Install new dependencies: docling, python-docx, python-magic, aiofiles, dramatiq[redis], python-multipart, boto3, tiktoken, clamd
- [x] T006 [P] Add environment variables to .env.example: STORAGE_BACKEND, UPLOAD_DIR, MAX_UPLOAD_SIZE_MB, ALLOWED_FILE_TYPES, DRAMATIQ_BROKER_URL, CHUNK_SIZE_TOKENS
- [x] T007 [P] Create local storage directories: ./uploads and ./tmp/uploads with appropriate permissions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Run alembic migration to add fields to documents table: content_hash, language, page_count, uploaded_by, original_filename, mime_type
- [ ] T009 Run alembic migration to add fields to document_chunks table: chunk_type, start_page, end_page, token_count, parent_heading
- [ ] T010 Run alembic migration to add fields to processing_jobs table: progress_percent, estimated_time_remaining, started_by
- [ ] T011 Run alembic migration to add fields to tenants table: storage_quota_bytes, storage_used_bytes
- [ ] T012 Run alembic migration to create upload_sessions table with session_id, tenant_id, user_id, filename, total_size_bytes, uploaded_size_bytes, status, expires_at
- [ ] T013 [P] Update config/settings.py to add UploadSettings class with STORAGE_BACKEND, UPLOAD_DIR, MAX_UPLOAD_SIZE_MB, ALLOWED_FILE_TYPES, CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS
- [ ] T014 [P] Update config/settings.py to add TaskQueueSettings class with DRAMATIQ_BROKER_URL, DRAMATIQ_RESULT_BACKEND, MAX_CONCURRENT_PARSING_JOBS
- [ ] T015 [P] Create src/shared/validators.py with file type validator, file size validator, content hash generator, malware scan validator
- [ ] T016 [P] Update src/shared/exceptions.py to add upload-specific exceptions: FileTypeNotAllowedError, FileTooLargeError, QuotaExceededError, MalwareScanFailedError
- [ ] T017 Create src/ingestion_parsing/storage/file_storage.py with FileStorage abstract base class and upload(), download(), delete() methods
- [ ] T018 [P] Implement LocalFileStorage class in src/ingestion_parsing/storage/file_storage.py for development (local filesystem)
- [ ] T019 [P] Implement S3FileStorage class in src/ingestion_parsing/storage/file_storage.py for production (boto3 S3 client)
- [ ] T020 Create src/ingestion_parsing/storage/quota_manager.py with QuotaManager class for check_quota(), update_usage(), get_usage() methods
- [ ] T021 Create src/storage_indexing/repositories/document_repository.py with DocumentRepository class for CRUD operations
- [ ] T022 [P] Create src/storage_indexing/repositories/chunk_repository.py with ChunkRepository class for chunk CRUD operations
- [ ] T023 [P] Create src/storage_indexing/repositories/job_repository.py with JobRepository class for job status queries and updates
- [ ] T024 Setup Dramatiq broker configuration in src/ingestion_parsing/tasks/worker.py with Redis backend connection
- [ ] T025 [P] Update src/api/dependencies.py to add get_file_storage(), get_quota_manager(), get_document_repository() dependency injection functions
- [ ] T026 [P] Create src/api/middleware/request_id.py for request ID tracking across async operations
- [ ] T027 [P] Create src/api/middleware/error_handler.py for standardized error responses with proper HTTP status codes

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Single Document Upload (Priority: P1) 🎯 MVP

**Goal**: Allow users to upload a single document (PDF) through the API, store it securely, and return confirmation with a processing job ID.

**Independent Test**: Upload a single 5-page PDF via POST /api/v1/documents/upload and verify it appears in database with status "uploaded", file is stored in correct location, and processing job is created with status "pending".

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T028 [P] [US1] Write contract test for POST /api/v1/documents/upload endpoint in tests/integration/test_upload_api.py (test request validation, response structure, status codes)
- [ ] T029 [P] [US1] Write integration test for single PDF upload workflow in tests/integration/test_upload_api.py (end-to-end: upload → storage → database → job creation)
- [ ] T030 [P] [US1] Write unit test for file type validation in tests/unit/test_validators.py (test python-magic content detection for PDF)
- [ ] T031 [P] [US1] Write unit test for file size validation in tests/unit/test_validators.py (test 50MB limit enforcement)
- [ ] T032 [P] [US1] Write unit test for quota checking in tests/unit/test_quota_manager.py (test quota exceeded scenario)

### Implementation for User Story 1

- [ ] T033 [P] [US1] Create src/ingestion_parsing/models/upload_request.py with UploadRequest Pydantic model for API request validation
- [ ] T034 [P] [US1] Create src/ingestion_parsing/models/parsing_result.py with ParsingResult Pydantic model for parsing output structure
- [ ] T035 [US1] Implement file type detection function in src/shared/validators.py using python-magic to inspect magic bytes
- [ ] T036 [US1] Implement file size validation function in src/shared/validators.py with configurable max size from settings
- [ ] T037 [US1] Implement content hash generation (SHA-256) in src/shared/validators.py for duplicate detection
- [ ] T038 [US1] Implement UploadService.upload_file() method in src/ingestion_parsing/services/upload_service.py (validates, generates filename, calls storage)
- [ ] T039 [US1] Implement UploadService.validate_upload() method in src/ingestion_parsing/services/upload_service.py (type, size, quota checks)
- [ ] T040 [US1] Implement POST /api/v1/documents/upload endpoint in src/api/routes/documents.py with multipart/form-data handling
- [ ] T041 [US1] Add tenant isolation check in documents.py route (ensure user can only upload to their tenant)
- [ ] T042 [US1] Implement document record creation in DocumentRepository.create() with uploaded_by, content_hash, mime_type fields
- [ ] T043 [US1] Implement processing job creation in JobRepository.create() with job_type="parse_document", status="pending"
- [ ] T044 [US1] Update tenant storage_used_bytes in QuotaManager.update_usage() after successful upload
- [ ] T045 [US1] Add error handling for upload failures in documents.py route (quota exceeded, invalid file type, storage errors)
- [ ] T046 [US1] Add structured logging for upload operations in upload_service.py (log document_id, file_size, tenant_id, user_id)

**Checkpoint**: At this point, User Story 1 should be fully functional - can upload single PDF, see it in database, job created

---

## Phase 4: User Story 5 - Document Content Extraction (Priority: P1) 🎯 MVP

**Goal**: Automatically extract text content from uploaded PDF documents and split into chunks optimized for vector search, making document content searchable.

**Independent Test**: Upload a PDF with known content, wait for processing job to complete, verify extracted text matches original, and chunks are created with correct order and token counts.

### Tests for User Story 5

- [ ] T047 [P] [US5] Write unit test for PDF parser in tests/unit/test_parsers.py (test Docling text extraction accuracy with sample PDF)
- [ ] T048 [P] [US5] Write unit test for chunking service in tests/unit/test_chunking_service.py (test 512-token chunks with 50-token overlap)
- [ ] T049 [P] [US5] Write integration test for full parsing workflow in tests/integration/test_parsing_workflow.py (upload → parse → chunk → update status)
- [ ] T050 [P] [US5] Write unit test for semantic chunking in tests/unit/test_chunking_service.py (test heading preservation, table handling)

### Implementation for User Story 5

- [ ] T051 [P] [US5] Create src/ingestion_parsing/parsers/base.py with BaseParser abstract class defining parse() method interface
- [ ] T052 [P] [US5] Implement PDFParser class in src/ingestion_parsing/parsers/pdf_parser.py using Docling library for text extraction
- [ ] T053 [US5] Implement PDFParser.extract_text() method in pdf_parser.py to extract full document text with page boundaries
- [ ] T054 [US5] Implement PDFParser.extract_metadata() method in pdf_parser.py to get page_count, language, document properties
- [ ] T055 [US5] Create src/ingestion_parsing/parsers/parser_factory.py with ParserFactory.get_parser() to select parser based on MIME type
- [ ] T056 [US5] Implement ChunkingService.chunk_document() method in src/ingestion_parsing/services/chunking_service.py with hybrid semantic + fixed-size strategy
- [ ] T057 [US5] Implement ChunkingService.split_by_semantic_boundaries() in chunking_service.py to detect headings, paragraphs, lists
- [ ] T058 [US5] Implement ChunkingService.enforce_token_limits() in chunking_service.py to ensure chunks are 100-512 tokens with tiktoken
- [ ] T059 [US5] Implement ChunkingService.add_overlap() in chunking_service.py to add 50-token overlap between chunks for context preservation
- [ ] T060 [US5] Create src/ingestion_parsing/services/parsing_service.py with ParsingService.parse_document() orchestration method
- [ ] T061 [US5] Implement parse_document() workflow in parsing_service.py: get parser → extract text → chunk → store chunks → update document status
- [ ] T062 [US5] Define parse_document Dramatiq actor in src/ingestion_parsing/tasks/document_tasks.py with @dramatiq.actor decorator (max_retries=3, time_limit=300000)
- [ ] T063 [US5] Implement parse_document task in document_tasks.py to call ParsingService.parse_document() and handle errors
- [ ] T064 [US5] Implement job progress tracking in parse_document task (update progress_percent at key stages: 25%, 50%, 75%, 100%)
- [ ] T065 [US5] Implement chunk creation in ChunkRepository.create_batch() to insert multiple chunks efficiently with chunk_order, chunk_type, token_count
- [ ] T066 [US5] Update document processing_status in DocumentRepository.update_status() when parsing completes (parsed) or fails (failed)
- [ ] T067 [US5] Implement retry logic with exponential backoff in parse_document task for transient failures
- [ ] T068 [US5] Add error message storage in JobRepository.update() when parsing fails (store error_message, error_code)
- [ ] T069 [US5] Add structured logging for parsing operations (log document_id, chunk_count, parsing_duration, errors)

**Checkpoint**: At this point, uploaded PDF documents are automatically parsed, chunked, and ready for search (MVP complete!)

---

## Phase 5: User Story 4 - Upload Progress and Status Tracking (Priority: P2)

**Goal**: Provide real-time visibility into upload progress and document processing status so users know when documents are ready.

**Independent Test**: Upload a large document, poll GET /api/v1/processing/jobs/{job_id} endpoint, verify progress_percent increases from 0 to 100 and status changes from pending → processing → completed.

### Tests for User Story 4

- [ ] T070 [P] [US4] Write contract test for GET /api/v1/processing/jobs/{job_id} endpoint in tests/integration/test_processing_api.py
- [ ] T071 [P] [US4] Write integration test for job status polling workflow in tests/integration/test_processing_api.py (upload → poll status every 2s → verify completion)
- [ ] T072 [P] [US4] Write unit test for progress calculation in tests/unit/test_parsing_service.py (test progress updates at each stage)

### Implementation for User Story 4

- [ ] T073 [P] [US4] Implement GET /api/v1/processing/jobs/{job_id} endpoint in src/api/routes/processing.py to return job status
- [ ] T074 [P] [US4] Implement GET /api/v1/documents/{document_id} endpoint in src/api/routes/documents.py to return document details with processing status
- [ ] T075 [US4] Implement JobRepository.get_by_id() method in src/storage_indexing/repositories/job_repository.py with tenant isolation check
- [ ] T076 [US4] Add progress_percent field updates in parse_document task at stages: file loaded (25%), text extracted (50%), chunks created (75%), complete (100%)
- [ ] T077 [US4] Implement estimated_time_remaining calculation in parse_document task based on file size and average parsing speed
- [ ] T078 [US4] Add polling example to quickstart.md showing curl commands to check job status every 5 seconds
- [ ] T079 [US4] Implement POST /api/v1/processing/jobs/{job_id}/retry endpoint in src/api/routes/processing.py for failed jobs
- [ ] T080 [US4] Implement POST /api/v1/processing/jobs/{job_id}/cancel endpoint in src/api/routes/processing.py for cancelling jobs
- [ ] T081 [US4] Add WebSocket support (optional) in src/api/routes/processing.py for real-time progress updates
- [ ] T082 [US4] Add tenant isolation checks in processing.py routes (ensure user can only access their tenant's jobs)

**Checkpoint**: Users can now track upload and processing status in real-time

---

## Phase 6: User Story 2 - Document Format Support (Priority: P2)

**Goal**: Support uploading documents in DOCX and TXT formats in addition to PDF, automatically detecting format and parsing accordingly.

**Independent Test**: Upload one file of each format (PDF, DOCX, TXT) and verify all are correctly parsed with text extracted and chunks created.

### Tests for User Story 2

- [ ] T083 [P] [US2] Write unit test for DOCX parser in tests/unit/test_parsers.py (test python-docx text extraction with sample DOCX)
- [ ] T084 [P] [US2] Write unit test for TXT parser in tests/unit/test_parsers.py (test plain text parsing with UTF-8 encoding)
- [ ] T085 [P] [US2] Write integration test for multi-format uploads in tests/integration/test_upload_api.py (upload PDF, DOCX, TXT in sequence)
- [ ] T086 [P] [US2] Write unit test for file type detection in tests/unit/test_validators.py (test MIME type detection for all supported formats)

### Implementation for User Story 2

- [ ] T087 [P] [US2] Implement DOCXParser class in src/ingestion_parsing/parsers/docx_parser.py using python-docx library
- [ ] T088 [US2] Implement DOCXParser.extract_text() method in docx_parser.py to extract text from paragraphs and tables
- [ ] T089 [US2] Implement DOCXParser.extract_metadata() method in docx_parser.py to get document properties (author, title, created_at)
- [ ] T090 [P] [US2] Implement TXTParser class in src/ingestion_parsing/parsers/txt_parser.py for plain text files
- [ ] T091 [US2] Implement TXTParser.extract_text() method in txt_parser.py with UTF-8 encoding and line ending normalization
- [ ] T092 [US2] Update ParserFactory.get_parser() in parser_factory.py to return DOCXParser for application/vnd.openxmlformats-officedocument.wordprocessingml.document
- [ ] T093 [US2] Update ParserFactory.get_parser() in parser_factory.py to return TXTParser for text/plain MIME type
- [ ] T094 [US2] Update ALLOWED_FILE_TYPES in config/settings.py to include docx and txt extensions
- [ ] T095 [US2] Add MIME type validation in src/shared/validators.py for all supported formats (PDF, DOCX, TXT)
- [ ] T096 [US2] Add error handling in ParserFactory for unsupported file types with clear error message listing supported formats
- [ ] T097 [US2] Update upload endpoint error responses in src/api/routes/documents.py to list supported formats when file type is rejected
- [ ] T098 [US2] Add sample DOCX and TXT files to tests/fixtures/sample_documents/ for testing

**Checkpoint**: System now supports PDF, DOCX, and TXT uploads with automatic format detection

---

## Phase 7: User Story 3 - Batch Upload (Priority: P3)

**Goal**: Allow users to upload multiple documents at once to save time, with each file processed independently.

**Independent Test**: Upload 10 PDF files via POST /api/v1/documents/batch-upload, verify all 10 are queued with individual job IDs, and all process successfully.

### Tests for User Story 3

- [ ] T099 [P] [US3] Write contract test for POST /api/v1/documents/batch-upload endpoint in tests/integration/test_upload_api.py
- [ ] T100 [P] [US3] Write integration test for batch upload with mixed success/failure in tests/integration/test_upload_api.py (10 files, 1 invalid)
- [ ] T101 [P] [US3] Write unit test for batch validation in tests/unit/test_upload_service.py (test max batch size limit)

### Implementation for User Story 3

- [ ] T102 [P] [US3] Create BatchUploadRequest Pydantic model in src/ingestion_parsing/models/upload_request.py with files array validation
- [ ] T103 [P] [US3] Create BatchUploadResponse Pydantic model in src/ingestion_parsing/models/upload_request.py with total, successful, failed counts
- [ ] T104 [US3] Implement POST /api/v1/documents/batch-upload endpoint in src/api/routes/documents.py accepting multiple files
- [ ] T105 [US3] Implement UploadService.batch_upload() method in src/ingestion_parsing/services/upload_service.py to process files sequentially
- [ ] T106 [US3] Add batch size validation in batch_upload() (max 10 files per batch from settings)
- [ ] T107 [US3] Implement partial success handling in batch_upload(): continue processing remaining files if one fails
- [ ] T108 [US3] Return detailed status for each file in batch response: filename, status (success/error), document_id, job_id, error message
- [ ] T109 [US3] Add quota check before starting batch: verify total batch size fits within available quota
- [ ] T110 [US3] Add structured logging for batch operations (log batch_id, total_files, successful_count, failed_count)
- [ ] T111 [US3] Add batch upload example to quickstart.md with curl command for multiple files
- [ ] T112 [US3] Implement GET /api/v1/documents endpoint with pagination in src/api/routes/documents.py (page, limit query params)
- [ ] T113 [US3] Add filtering by status and file_type in GET /api/v1/documents endpoint

**Checkpoint**: Users can now upload multiple documents in a single operation

---

## Phase 8: User Story 6 (Stretch) - Resumable Uploads (Priority: P4)

**Goal**: Support resumable uploads for large files (>10MB) so network interruptions don't lose progress.

**Independent Test**: Start uploading a 45MB file, interrupt after 25MB, resume upload, verify final document is complete and correct.

### Tests for User Story 6

- [ ] T114 [P] [US6] Write contract test for POST /api/v1/documents/upload/resumable endpoint in tests/integration/test_upload_api.py
- [ ] T115 [P] [US6] Write contract test for PATCH /api/v1/documents/upload/resumable/{session_id} endpoint in tests/integration/test_upload_api.py
- [ ] T116 [P] [US6] Write integration test for resumable upload workflow in tests/integration/test_upload_api.py (init → upload 3 chunks → merge)
- [ ] T117 [P] [US6] Write unit test for chunk merging in tests/unit/test_upload_service.py

### Implementation for User Story 6

- [ ] T118 [P] [US6] Create ResumableUploadInit Pydantic model in src/ingestion_parsing/models/upload_request.py with filename, file_size, chunk_size
- [ ] T119 [P] [US6] Create ResumableUploadSession Pydantic model in src/ingestion_parsing/models/upload_request.py for session responses
- [ ] T120 [US6] Implement POST /api/v1/documents/upload/resumable endpoint in src/api/routes/documents.py to create upload session
- [ ] T121 [US6] Implement UploadSession creation in src/storage_indexing/repositories/upload_session_repository.py (session_id, expires_at = now + 24h)
- [ ] T122 [US6] Implement PATCH /api/v1/documents/upload/resumable/{session_id} endpoint in src/api/routes/documents.py to accept chunks
- [ ] T123 [US6] Parse Content-Range header in resumable upload endpoint to get byte range
- [ ] T124 [US6] Store chunks in temporary location: /tmp/uploads/{session_id}/chunk_{N} with chunk number
- [ ] T125 [US6] Update UploadSession.uploaded_size_bytes after each chunk upload
- [ ] T126 [US6] Implement chunk merging in UploadService.merge_chunks() when uploaded_size_bytes == total_size_bytes
- [ ] T127 [US6] Validate merged file hash matches original file hash to ensure integrity
- [ ] T128 [US6] Create Document record after successful merge and trigger parsing job
- [ ] T129 [US6] Clean up temporary chunk files after merge or cancellation
- [ ] T130 [US6] Implement GET /api/v1/documents/upload/resumable/{session_id} endpoint to check progress
- [ ] T131 [US6] Implement DELETE /api/v1/documents/upload/resumable/{session_id} endpoint to cancel and cleanup
- [ ] T132 [US6] Create Dramatiq periodic task to clean up expired upload sessions (status = expired after 24 hours)
- [ ] T133 [US6] Add resumable upload example to quickstart.md with curl commands for chunked upload

**Checkpoint**: Large file uploads are now resumable and network-resilient

---

## Phase 9: User Story 7 (Stretch) - Malware Scanning (Priority: P4)

**Goal**: Scan uploaded files for malware before storing to protect system and users.

**Independent Test**: Upload EICAR test file, verify it's detected and rejected with clear error message.

### Tests for User Story 7

- [ ] T134 [P] [US7] Write integration test for malware detection in tests/integration/test_upload_api.py using EICAR test file
- [ ] T135 [P] [US7] Write unit test for ClamAV scanner in tests/unit/test_malware_scanner.py (mock ClamAV responses)

### Implementation for User Story 7

- [ ] T136 [P] [US7] Add ClamAV service to docker-compose.yml with clamav/clamav:latest image on port 3310
- [ ] T137 [P] [US7] Add ENABLE_MALWARE_SCANNING and CLAMAV_HOST settings to config/settings.py (default: false for development)
- [ ] T138 [US7] Implement MalwareScanner class in src/ingestion_parsing/services/malware_scanner.py with scan_file() method
- [ ] T139 [US7] Integrate clamd library in malware_scanner.py to connect to ClamAV daemon
- [ ] T140 [US7] Call malware scanner in UploadService.validate_upload() before storing file (if ENABLE_MALWARE_SCANNING=true)
- [ ] T141 [US7] Return clear error message when malware is detected: "File rejected: malware detected" with HTTP 400
- [ ] T142 [US7] Add fallback behavior if ClamAV is unavailable: log warning and continue (configurable: fail-open vs fail-closed)
- [ ] T143 [US7] Download EICAR test file to tests/fixtures/sample_documents/malicious.txt for testing
- [ ] T144 [US7] Add malware scanning documentation to quickstart.md (how to enable/disable ClamAV)

**Checkpoint**: System now scans uploads for malware (optional feature)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T145 [P] Add comprehensive docstrings (Google style) to all parser classes in src/ingestion_parsing/parsers/
- [ ] T146 [P] Add comprehensive docstrings to all service classes in src/ingestion_parsing/services/
- [ ] T147 [P] Add type hints to all functions in src/ingestion_parsing/ modules using Python 3.12+ typing
- [ ] T148 [P] Run ruff check and ruff format on all new code in src/ingestion_parsing/ and src/api/routes/
- [ ] T149 [P] Run mypy on src/ingestion_parsing/ to verify type safety (strict mode)
- [ ] T150 [P] Add input validation examples to quickstart.md (max file size, allowed types, quota limits)
- [ ] T151 [P] Update main README.md with document upload feature description and API endpoints
- [ ] T152 [P] Add OpenAPI schema generation for new endpoints (auto-generated by FastAPI)
- [ ] T153 Add performance benchmarks to tests: measure parsing speed for 1MB, 10MB, 50MB files
- [ ] T154 Optimize database queries: add indexes on documents.content_hash, documents.uploaded_by, upload_sessions.expires_at
- [ ] T155 [P] Add metrics collection for monitoring: upload_count, parsing_duration_seconds, chunk_count, error_rate
- [ ] T156 Add rate limiting to upload endpoints to prevent abuse (e.g., max 100 uploads per hour per user)
- [ ] T157 [P] Create scripts/test_parsers.py manual testing script from quickstart.md example
- [ ] T158 [P] Create scripts/setup_storage.sh to initialize upload directories with proper permissions
- [ ] T159 Run full quickstart.md validation: execute all steps and verify outputs match expected results
- [ ] T160 Generate API documentation using Swagger UI: verify all endpoints documented at /api/v1/docs
- [ ] T161 Create production deployment checklist in docs/ (S3 setup, ClamAV deployment, monitoring, backups)
- [ ] T162 Add security hardening: implement CSRF protection, validate Content-Type headers, sanitize filenames
- [ ] T163 [P] Add integration with frontend: document API client functions needed in frontend/lib/api/documents.ts
- [ ] T164 Perform end-to-end testing: upload → parse → search (integration with future RAG features)
- [ ] T165 Update CHANGELOG.md with document upload feature release notes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - **Phase 3 (US1)** and **Phase 4 (US5)**: Can start after Foundational (P1 priority - MVP)
  - **Phase 5 (US4)** and **Phase 6 (US2)**: Can start after Foundational (P2 priority)
  - **Phase 7 (US3)**: Can start after Foundational (P3 priority)
  - **Phase 8 (US6)**: Can start after US1 is stable (stretch goal)
  - **Phase 9 (US7)**: Can start after US1 is stable (stretch goal)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Single Upload - No dependencies on other stories
- **User Story 5 (P1)**: Content Extraction - No dependencies on other stories
- **User Story 4 (P2)**: Progress Tracking - Depends on US1 and US5 for testing, but independently implementable
- **User Story 2 (P2)**: Format Support - Depends on US1 and US5 patterns, but adds new parsers independently
- **User Story 3 (P3)**: Batch Upload - Depends on US1 being stable, reuses upload logic
- **User Story 6 (P4)**: Resumable Uploads - Depends on US1 being stable, separate upload flow
- **User Story 7 (P4)**: Malware Scanning - Independent, can be added anytime

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T006, T007 can run in parallel

**Phase 2 (Foundational)**: T013-T014, T015-T016, T018-T019, T022-T023, T026-T027 can run in parallel

**Phase 3 (US1 - Tests)**: T028, T029, T030, T031, T032 can all run in parallel

**Phase 3 (US1 - Models)**: T033, T034 can run in parallel

**Phase 4 (US5 - Tests)**: T047, T048, T049, T050 can all run in parallel

**Phase 4 (US5 - Parsers)**: T051, T052 can run in parallel

**Phase 5 (US4 - Tests)**: T070, T071, T072 can all run in parallel

**Phase 5 (US4 - Endpoints)**: T073, T074 can run in parallel

**Phase 6 (US2 - Tests)**: T083, T084, T085, T086 can all run in parallel

**Phase 6 (US2 - Parsers)**: T087, T090 can run in parallel

**Phase 7 (US3 - Tests)**: T099, T100, T101 can all run in parallel

**Phase 7 (US3 - Models)**: T102, T103 can run in parallel

**Phase 8 (US6 - Tests)**: T114, T115, T116, T117 can all run in parallel

**Phase 8 (US6 - Models)**: T118, T119 can run in parallel

**Phase 9 (US7 - Tests)**: T134, T135 can run in parallel

**Phase 9 (US7 - Setup)**: T136, T137 can run in parallel

**Phase 10 (Polish)**: T145, T146, T147, T148, T149, T150, T151, T152, T157, T158, T163 can run in parallel

**Cross-Story Parallelism**: Once Foundational (Phase 2) completes, Phase 3 (US1) and Phase 4 (US5) can proceed in parallel as they are both P1 priority and have no dependencies on each other.

---

## Parallel Example: User Story 1 (Single Upload)

```bash
# Launch all tests for User Story 1 together:
Task T028: "Contract test for POST /api/v1/documents/upload endpoint"
Task T029: "Integration test for single PDF upload workflow"
Task T030: "Unit test for file type validation"
Task T031: "Unit test for file size validation"
Task T032: "Unit test for quota checking"

# After tests complete, launch models in parallel:
Task T033: "Create UploadRequest Pydantic model"
Task T034: "Create ParsingResult Pydantic model"
```

---

## Parallel Example: User Story 5 (Content Extraction)

```bash
# Launch all tests for User Story 5 together:
Task T047: "Unit test for PDF parser"
Task T048: "Unit test for chunking service"
Task T049: "Integration test for full parsing workflow"
Task T050: "Unit test for semantic chunking"

# After tests complete, launch base classes in parallel:
Task T051: "Create BaseParser abstract class"
Task T052: "Implement PDFParser class"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 5 Only)

1. Complete Phase 1: Setup → T001-T007
2. Complete Phase 2: Foundational (CRITICAL) → T008-T027
3. Complete Phase 3: User Story 1 (Single Upload) → T028-T046
4. Complete Phase 4: User Story 5 (Content Extraction) → T047-T069
5. **STOP and VALIDATE**: Test end-to-end workflow: upload PDF → parse → verify chunks created
6. Deploy/demo MVP (can upload and parse single PDF documents)

**MVP Deliverable**: Users can upload a single PDF, system automatically parses and chunks it, ready for search queries.

### Incremental Delivery

1. Complete Setup + Foundational → T001-T027 (Foundation ready)
2. Add User Story 1 + 5 → T028-T069 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 4 (Progress Tracking) → T070-T082 → Test independently → Deploy/Demo
4. Add User Story 2 (Format Support) → T083-T098 → Test independently → Deploy/Demo
5. Add User Story 3 (Batch Upload) → T099-T113 → Test independently → Deploy/Demo
6. Optional: Add User Story 6 (Resumable) → T114-T133 → Test independently
7. Optional: Add User Story 7 (Malware Scan) → T134-T144 → Test independently
8. Polish → T145-T165 → Production ready

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T027)
2. **Once Foundational is done, split work**:
   - **Developer A**: User Story 1 (Single Upload) → T028-T046
   - **Developer B**: User Story 5 (Content Extraction) → T047-T069
   - **Developer C**: User Story 4 (Progress Tracking) → T070-T082
3. **After P1 stories complete, continue in parallel**:
   - **Developer A**: User Story 2 (Format Support) → T083-T098
   - **Developer B**: User Story 3 (Batch Upload) → T099-T113
   - **Developer C**: Polish & Metrics → T145-T165
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 165

**By Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 20 tasks (BLOCKS everything)
- Phase 3 (US1 - Single Upload, P1): 19 tasks
- Phase 4 (US5 - Content Extraction, P1): 23 tasks
- Phase 5 (US4 - Progress Tracking, P2): 13 tasks
- Phase 6 (US2 - Format Support, P2): 16 tasks
- Phase 7 (US3 - Batch Upload, P3): 15 tasks
- Phase 8 (US6 - Resumable Uploads, P4): 22 tasks
- Phase 9 (US7 - Malware Scanning, P4): 11 tasks
- Phase 10 (Polish): 19 tasks

**By User Story**:
- User Story 1 (Single Upload): 19 tasks
- User Story 5 (Content Extraction): 23 tasks
- User Story 4 (Progress Tracking): 13 tasks
- User Story 2 (Format Support): 16 tasks
- User Story 3 (Batch Upload): 15 tasks
- User Story 6 (Resumable Uploads): 22 tasks (stretch)
- User Story 7 (Malware Scanning): 11 tasks (stretch)
- Infrastructure (Setup + Foundational): 27 tasks
- Polish: 19 tasks

**Parallel Opportunities**: 45+ tasks can run in parallel within their phases

**Independent Test Criteria**:
- US1: Upload single PDF → verify in database with job created
- US5: Parse uploaded PDF → verify text extracted and chunks created
- US4: Poll job status → verify progress updates from 0% to 100%
- US2: Upload PDF, DOCX, TXT → verify all formats parse correctly
- US3: Upload 10 files → verify all queued and processed
- US6: Upload large file in chunks → verify final document complete
- US7: Upload EICAR test file → verify rejection with malware error

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) + Phase 4 (US5) = 69 tasks

**Format Validation**: ✅ All 165 tasks follow the required checklist format with checkboxes, task IDs, parallelization markers, story labels, and file paths.

---

## Notes

- **[P] tasks** = different files, no dependencies - can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Verify tests fail** before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are specific and actionable for LLM execution
- Tests are included for comprehensive coverage (80%+ target)
