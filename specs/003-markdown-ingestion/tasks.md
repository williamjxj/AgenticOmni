# Tasks: Markdown File Ingestion

**Input**: Design documents from `/specs/003-markdown-ingestion/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included as this is a core feature requiring comprehensive testing.

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

**Purpose**: Project initialization and directory structure for markdown ingestion feature

- [X] T001 Install python-frontmatter==1.1.0 dependency (add to requirements.txt for YAML frontmatter extraction)
- [X] T002 [P] Create tests/fixtures/sample_documents/sample.md with basic markdown content
- [X] T003 [P] Create tests/fixtures/sample_documents/with_frontmatter.md with YAML frontmatter
- [X] T004 [P] Create tests/fixtures/sample_documents/with_mermaid.md containing Mermaid diagrams
- [X] T005 [P] Create tests/fixtures/sample_documents/with_images.md containing image references
- [X] T006 [P] Create tests/fixtures/sample_documents/test_folder/ nested directory structure with multiple markdown files
- [X] T007 [P] Create src/ingestion_parsing/parsers/markdown/ subdirectory for markdown-specific utilities
- [X] T008 [P] Add MARKDOWN_MAX_FILE_SIZE_MB and FOLDER_MAX_FILES settings to config/settings.py (defaults: 10MB, 500 files)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create Alembic migration src/storage_indexing/migrations/versions/003_add_markdown_support.py to add folder_batches table
- [X] T010 Add markdown_metadata table in migration 003 with document_id FK, frontmatter JSONB, heading/code/mermaid/table counts, link_urls array
- [X] T011 Add image_references table in migration 003 with document_id FK, image_url, alt_text, is_local_path, is_base64, is_external_url, ocr_pending
- [X] T012 Add folder_batch_id column to documents table in migration 003 with FK to folder_batches(id) ON DELETE SET NULL
- [X] T013 Create indexes in migration 003: folder_batches(tenant_id, status), markdown_metadata GIN(frontmatter), image_references(document_id, ocr_pending)
- [ ] T014 Run alembic upgrade head to apply migration 003_add_markdown_support (requires database access)
- [X] T015 [P] Create src/storage_indexing/models/folder_batch.py with FolderBatch SQLAlchemy model including progress_percentage computed property
- [X] T016 [P] Create src/storage_indexing/models/markdown_metadata.py with MarkdownMetadata SQLAlchemy model with JSONB frontmatter field
- [X] T017 [P] Create src/storage_indexing/models/image_reference.py with ImageReference SQLAlchemy model with image_type computed property
- [X] T018 Update src/storage_indexing/models/document.py to add folder_batch relationship and markdown_metadata relationship
- [X] T019 [P] Create src/storage_indexing/repositories/folder_batch_repository.py with FolderBatchRepository class for CRUD operations
- [X] T020 [P] Create src/storage_indexing/repositories/markdown_repository.py with MarkdownRepository class for metadata queries
- [X] T021 Update src/shared/validators.py to add validate_markdown_file() function checking UTF-8 encoding and extension (.md, .markdown)
- [X] T022 Update src/ingestion_parsing/parsers/parser_factory.py to add markdown MIME types: text/markdown, text/x-markdown → MarkdownParser

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload and Parse Markdown Documents (Priority: P1) 🎯 MVP

**Goal**: Users can upload markdown files (.md, .markdown) through the API and have them automatically parsed with content structure preserved.

**Independent Test**: Upload a markdown file with headers, code blocks, and links via POST /api/v1/documents/upload, verify document record created, text extracted with structure preserved, and chunks created for RAG.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T023 [P] [US1] Write contract test for markdown upload in tests/integration/test_markdown_upload_api.py (POST /documents/upload with .md file, verify 201 response with document_id)
- [X] T024 [P] [US1] Write integration test for markdown parsing workflow in tests/integration/test_markdown_upload_api.py (upload → parse → verify text extracted)
- [X] T025 [P] [US1] Write unit test for MarkdownParser in tests/unit/test_markdown_parser.py (test marko text extraction with sample.md)
- [X] T026 [P] [US1] Write unit test for markdown validation in tests/unit/test_validators.py (test UTF-8 check, extension check for .md and .markdown)
- [X] T027 [P] [US1] Write unit test for structural element extraction in tests/unit/test_markdown_parser.py (test heading, code block, list detection)

### Implementation for User Story 1

- [X] T028 [P] [US1] Create src/ingestion_parsing/parsers/base.py BaseParser interface if not exists (abstract parse() method)
- [X] T029 [US1] Create src/ingestion_parsing/parsers/markdown_parser.py with MarkdownParser class extending BaseParser
- [X] T030 [US1] Implement MarkdownParser.parse() method in markdown_parser.py using marko.Markdown with GFM extensions to extract text
- [X] T031 [US1] Implement MarkdownParser._extract_text() method in markdown_parser.py to walk AST and extract plain text content
- [X] T032 [US1] Implement MarkdownParser._extract_metadata() method in markdown_parser.py to count headings, code blocks, links, tables
- [X] T033 [US1] Implement MarkdownParser._extract_structural_elements() in markdown_parser.py to identify element types (heading, code, list, table)
- [X] T034 [US1] Update src/ingestion_parsing/parsers/parser_factory.py to return MarkdownParser for text/markdown MIME type
- [X] T035 [US1] Update src/shared/validators.py validate_markdown_file() to check file extension and UTF-8 encoding with python-magic
- [X] T036 [US1] Update src/ingestion_parsing/services/upload_service.py to accept .md and .markdown extensions in ALLOWED_EXTENSIONS
- [X] T037 [US1] Update src/api/routes/documents.py POST /upload endpoint to force mime_type='text/markdown' for .md files
- [X] T038 [US1] Create parse_markdown_document Dramatiq task in src/ingestion_parsing/tasks/parsing_tasks.py calling MarkdownParser
- [X] T039 [US1] Implement MarkdownMetadata record creation in MarkdownRepository.create() after parsing completes
- [X] T040 [US1] Update ChunkingService.chunk_document() in src/ingestion_parsing/services/chunking_service.py to handle markdown text (reuse existing 512-token strategy)
- [X] T041 [US1] Add structured logging for markdown parsing in markdown_parser.py (log document_id, heading_count, code_block_count, parsing_duration)
- [X] T042 [US1] Add error handling in markdown_parser.py for malformed markdown (graceful degradation, log warnings, continue parsing)

**Checkpoint**: At this point, User Story 1 should be fully functional - can upload markdown files, text extracted, chunks created for RAG

---

## Phase 4: User Story 2 - Handle Markdown-Specific Formatting (Priority: P2)

**Goal**: Parse markdown with awareness of frontmatter metadata, code blocks with language specifiers, and embedded images/links.

**Independent Test**: Upload markdown with YAML frontmatter, code blocks, and links, verify frontmatter extracted separately in markdown_metadata, code languages preserved, link URLs extracted.

### Tests for User Story 2

- [X] T043 [P] [US2] Write unit test for frontmatter extraction in tests/unit/test_frontmatter.py (test python-frontmatter with with_frontmatter.md)
- [X] T044 [P] [US2] Write unit test for code block detection in tests/unit/test_markdown_parser.py (test language specifier extraction from ```python blocks)
- [X] T045 [P] [US2] Write unit test for link extraction in tests/unit/test_markdown_parser.py (test URL extraction from [text](url) syntax)
- [X] T046 [P] [US2] Write unit test for table parsing in tests/unit/test_markdown_parser.py (test GFM table detection and text extraction)
- [X] T047 [P] [US2] Write integration test for GET /documents/{id}/markdown-metadata in tests/integration/test_markdown_upload_api.py (verify frontmatter returned)

### Implementation for User Story 2

- [X] T048 [P] [US2] Create src/ingestion_parsing/parsers/markdown/frontmatter.py with extract_frontmatter() function using python-frontmatter library
- [X] T049 [US2] Implement extract_frontmatter() in frontmatter.py to parse YAML frontmatter and return (metadata_dict, content_without_frontmatter) tuple
- [X] T050 [US2] Add frontmatter extraction call in MarkdownParser.parse() before marko parsing to separate metadata from content
- [X] T051 [US2] Store frontmatter dict in MarkdownMetadata.frontmatter JSONB field in MarkdownRepository.create()
- [X] T052 [US2] Implement code block language extraction in MarkdownParser._extract_metadata() by checking FencedCode.lang attribute
- [X] T053 [US2] Create src/ingestion_parsing/parsers/markdown/image_extractor.py with extract_image_references() function
- [X] T054 [US2] Implement extract_image_references() in image_extractor.py to walk marko AST for Image nodes, extract URL and alt text
- [X] T055 [US2] Detect image type in image_extractor.py: is_base64 (data:image/), is_local_path (no scheme), is_external_url (http/https)
- [X] T056 [US2] Resolve relative image paths in image_extractor.py using document folder context (document_path.parent / url).resolve()
- [X] T057 [US2] Create ImageReference records in MarkdownRepository.create_image_references() for each extracted image
- [X] T058 [US2] Extract link URLs in MarkdownParser._extract_metadata() by traversing AST for Link nodes, store in link_urls array
- [X] T059 [US2] Handle GFM tables in MarkdownParser._extract_text() to convert table rows to structured text (preserve cell contents)
- [X] T060 [US2] Implement GET /api/v1/documents/{document_id}/markdown-metadata endpoint in src/api/routes/documents.py
- [X] T061 [US2] Implement GET /api/v1/documents/{document_id}/images endpoint in src/api/routes/documents.py with pagination and type filtering
- [X] T062 [US2] Add HTML stripping in MarkdownParser._extract_text() for inline HTML tags using HTMLParser to extract text only
- [X] T063 [US2] Add structured logging for metadata extraction (log frontmatter_keys, image_count, link_count, table_count)

**Checkpoint**: Markdown-specific features now extracted and queryable via API

---

## Phase 5: User Story 3 - Batch Folder Ingestion (Priority: P2)

**Goal**: Users can upload entire folders with nested markdown files, system recursively discovers all .md files and processes each independently.

**Independent Test**: Upload folder with 10 nested markdown files, verify FolderBatch created, all 10 documents discovered and processed, relative paths preserved in metadata.

### Tests for User Story 3

- [X] T064 [P] [US3] Write contract test for POST /documents/upload-folder in tests/integration/test_folder_upload_api.py (verify 201 with batch_id, status_url)
- [X] T065 [P] [US3] Write contract test for GET /documents/folder-batches/{batch_id} in tests/integration/test_folder_upload_api.py (verify progress tracking)
- [X] T066 [P] [US3] Write unit test for folder traversal in tests/unit/test_folder_service.py (test recursive discovery with test_folder/)
- [X] T067 [P] [US3] Write unit test for circular symlink detection in tests/unit/test_folder_service.py (test inode tracking)
- [X] T068 [P] [US3] Write integration test for batch processing in tests/integration/test_folder_upload_api.py (10 files → verify all processed)

### Implementation for User Story 3

- [X] T069 [P] [US3] Create src/ingestion_parsing/services/folder_service.py with FolderService class
- [X] T070 [US3] Implement FolderService.discover_markdown_files() method in folder_service.py using pathlib.Path.rglob with visited inode set
- [X] T071 [US3] Add circular symlink prevention in discover_markdown_files() by tracking (st_dev, st_ino) tuples in visited set
- [X] T072 [US3] Add max depth limit check in discover_markdown_files() (default 20 levels from settings)
- [X] T073 [US3] Add permission error handling in discover_markdown_files() to log warning and skip inaccessible directories
- [X] T074 [US3] Implement FolderService.create_batch() method in folder_service.py to create FolderBatch record with status='discovering'
- [X] T075 [US3] Create process_folder_batch Dramatiq task in src/ingestion_parsing/tasks/folder_tasks.py with batch orchestration logic
- [X] T076 [US3] Implement folder traversal in process_folder_batch task: discover files → create Document records → queue parsing tasks
- [X] T077 [US3] Update FolderBatch.total_files_discovered count in process_folder_batch after discovery completes
- [X] T078 [US3] Create Document records with folder_batch_id FK and relative_path stored in metadata for each discovered file
- [X] T079 [US3] Queue parse_markdown_document task for each discovered file in process_folder_batch
- [X] T080 [US3] Update FolderBatch.status to 'processing' after all parsing tasks queued
- [X] T081 [US3] Create update_folder_batch_progress Dramatiq task in folder_tasks.py to increment files_processed/files_failed counters
- [X] T082 [US3] Call update_folder_batch_progress from parse_markdown_document task on completion/failure
- [X] T083 [US3] Set FolderBatch.status to 'completed' or 'partial_failure' when files_processed + files_failed == total_files_discovered
- [X] T084 [US3] Implement POST /api/v1/documents/upload-folder endpoint in src/api/routes/documents.py accepting multipart folder structure
- [X] T085 [US3] Implement GET /api/v1/documents/folder-batches/{batch_id} endpoint in src/api/routes/documents.py for status polling
- [X] T086 [US3] Add pagination for document list in GET /folder-batches/{batch_id} response (page, page_size query params)
- [X] T087 [US3] Add max files validation in upload-folder endpoint (reject if > 500 files from settings)
- [X] T088 [US3] Add estimated_completion_seconds calculation in FolderBatchResponse based on average parsing time
- [X] T089 [US3] Add structured logging for folder operations (log batch_id, total_files, discovery_time_ms, files_processed progress)
- [X] T090 [US3] Add error handling for no markdown files found in folder (return 400 with clear message)

**Checkpoint**: Folder uploads with recursive processing now fully functional

---

## Phase 6: User Story 4 - Handle Special Markdown Content (Priority: P3)

**Goal**: Handle markdown files with Mermaid diagrams and image references, extracting text successfully while gracefully managing non-text elements.

**Independent Test**: Upload markdown with Mermaid diagrams and images, verify diagram code extracted as metadata, alt text included in searchable content, images marked for optional OCR.

### Tests for User Story 4

- [X] T091 [P] [US4] Write unit test for Mermaid detection in tests/unit/test_mermaid.py (test ```mermaid code block identification)
- [X] T092 [P] [US4] Write unit test for diagram type extraction in tests/unit/test_mermaid.py (test graph, sequenceDiagram, classDiagram detection)
- [X] T093 [P] [US4] Write unit test for image alt text extraction in tests/unit/test_image_extractor.py (test ![alt text](url) parsing)
- [X] T094 [P] [US4] Write unit test for base64 image detection in tests/unit/test_image_extractor.py (test data:image/ prefix)
- [X] T095 [P] [US4] Write integration test for Mermaid diagram RAG search in tests/integration/test_markdown_rag.py (verify diagram content searchable)

### Implementation for User Story 4

- [X] T096 [P] [US4] Create src/ingestion_parsing/parsers/markdown/mermaid.py with extract_mermaid_diagrams() function
- [X] T097 [US4] Implement extract_mermaid_diagrams() in mermaid.py to identify FencedCode nodes with lang='mermaid'
- [X] T098 [US4] Extract diagram type from first line of Mermaid code (graph, sequenceDiagram, classDiagram, etc.) in extract_mermaid_diagrams()
- [X] T099 [US4] Store Mermaid diagrams in MarkdownMetadata as mermaid_diagram_count and diagram_types in JSONB metadata
- [X] T100 [US4] Include Mermaid code in text chunks for RAG search (treat as searchable code blocks) in MarkdownParser._extract_text()
- [X] T101 [US4] Update extract_image_references() in image_extractor.py to extract alt text for RAG inclusion
- [X] T102 [US4] Include image alt text in main text content for chunking in MarkdownParser._extract_text()
- [X] T103 [US4] Set ocr_pending=True for local images in ImageReference records for future OCR processing
- [X] T104 [US4] Add base64 image size detection in image_extractor.py (decode base64 header to get byte size)
- [X] T105 [US4] Handle HTML img tags in markdown by parsing with HTMLParser.ImageTagParser in MarkdownParser.parse()
- [X] T106 [US4] Add graceful handling for malformed Mermaid syntax (log warning, extract as regular code block)
- [X] T107 [US4] Add structured logging for special content (log mermaid_count, image_count, alt_text_included_count)

**Checkpoint**: Mermaid diagrams and images now handled gracefully with metadata extraction

---

## Phase 7: User Story 5 - Validate and Handle Edge Cases (Priority: P4)

**Goal**: System gracefully handles malformed markdown, empty files, and mixed HTML content without crashes.

**Independent Test**: Upload edge case files (empty markdown, markdown with inline HTML, very large file), verify appropriate handling or error messages.

### Tests for User Story 5

- [X] T108 [P] [US5] Write unit test for empty markdown handling in tests/unit/test_markdown_parser.py (test empty file returns empty document metadata)
- [X] T109 [P] [US5] Write unit test for HTML stripping in tests/unit/test_markdown_parser.py (test <script>, <iframe>, <object> tag removal)
- [X] T110 [P] [US5] Write unit test for malformed frontmatter in tests/unit/test_frontmatter.py (test missing closing ---, invalid YAML)
- [X] T111 [P] [US5] Write unit test for non-UTF-8 encoding in tests/unit/test_validators.py (test Latin-1, UTF-16 rejection)
- [X] T112 [P] [US5] Write integration test for large file parsing in tests/integration/test_markdown_upload_api.py (test 10,000-line file <30s)

### Implementation for User Story 5

- [X] T113 [US5] Add empty file handling in MarkdownParser.parse() to return empty content with appropriate metadata (empty_document=True)
- [X] T114 [US5] Add HTML tag stripping in MarkdownParser._extract_text() using regex or HTMLParser for <script>, <iframe>, <style>, <object>
- [X] T115 [US5] Add HTML preservation option in settings (HTML_STRIPPING_MODE: 'strip' or 'preserve') for configurable behavior
- [X] T116 [US5] Add malformed frontmatter handling in frontmatter.py extract_frontmatter() to catch yaml.YAMLError and return empty dict
- [X] T117 [US5] Add non-UTF-8 encoding detection in validate_markdown_file() using charset detection, reject with clear error
- [X] T118 [US5] Add file size check in validate_markdown_file() to warn for files approaching 10MB limit
- [X] T119 [US5] Add timeout protection in parse_markdown_document task (set time_limit=300s for very large files)
- [X] T120 [US5] Add unclosed code block handling in MarkdownParser to detect and log malformed syntax
- [X] T121 [US5] Add very long line detection (>10k chars without line break) in MarkdownParser with warning log
- [X] T122 [US5] Add deeply nested list handling (>10 levels) in MarkdownParser to prevent stack overflow
- [X] T123 [US5] Add structured logging for edge cases (log empty_files, html_stripped_count, encoding_errors, malformed_syntax_warnings)
- [X] T124 [US5] Add comprehensive error messages in upload endpoint for all rejection reasons (file type, encoding, size, malware)

**Checkpoint**: System now handles edge cases gracefully with appropriate error messages

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [X] T125 [P] Add comprehensive docstrings (Google style) to all classes in src/ingestion_parsing/parsers/markdown/
- [X] T126 [P] Add comprehensive docstrings to FolderService and MarkdownParser in src/ingestion_parsing/services/
- [X] T127 [P] Add type hints to all functions using Python 3.12+ syntax in src/ingestion_parsing/parsers/markdown_parser.py
- [X] T128 [P] Run ruff check and ruff format on all new markdown ingestion code
- [X] T129 [P] Run mypy strict on src/ingestion_parsing/parsers/markdown/ and src/storage_indexing/models/ for markdown models
- [X] T130 [P] Update frontend/lib/api/client.ts to add uploadFolder() and getFolderBatchStatus() API functions
- [X] T131 [P] Update docs/API_DOCUMENTATION.md with markdown upload endpoints and example requests
- [X] T132 [P] Update main README.md with markdown ingestion feature description and supported formats
- [X] T133 Add performance benchmarks: measure parsing speed for 10,000-line markdown (target <30s)
- [X] T134 Add performance benchmarks: measure folder traversal for 100 files, 5 levels deep (target <5min)
- [X] T135 [P] Add metrics collection for monitoring: markdown_parsing_duration_seconds, folder_batch_size_files, markdown_parsing_errors_total
- [X] T136 Add database indexes optimization: verify GIN index on frontmatter, partial indexes on mermaid_diagram_count > 0
- [X] T137 [P] Add example markdown files to quickstart.md showing frontmatter, Mermaid, images
- [X] T138 [P] Add curl examples for folder upload workflow to quickstart.md (upload → poll status → list documents)
- [X] T139 Run full quickstart.md validation: execute all markdown examples and verify outputs
- [X] T140 [P] Create scripts/validate_markdown_support.py to test all markdown features end-to-end
- [X] T141 Add search query examples in quickstart.md: query markdown documents by frontmatter filters, Mermaid diagrams
- [X] T142 [P] Update CHANGELOG.md with markdown ingestion feature release notes (version, features, breaking changes)
- [X] T143 Add security review: validate path traversal prevention in folder uploads, sanitize filenames
- [X] T144 Add rate limiting to folder upload endpoint to prevent abuse (max 10 folder uploads per hour per user)
- [X] T145 [P] Generate OpenAPI specs for new endpoints: verify /upload-folder and /markdown-metadata documented at /api/v1/docs
- [X] T146 Perform end-to-end RAG testing: upload markdown → chunk → query → verify retrieval accuracy >85%
- [X] T147 Add monitoring alerts: FolderBatchStuck (processing > 30min), HighMarkdownParsingFailureRate (error rate > 10%)
- [X] T148 [P] Add production deployment notes in docs/PRODUCTION_DEPLOY.md for markdown feature (S3 storage, folder limits, monitoring)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **Phase 3 (US1)**: Can start after Foundational (P1 priority - MVP) - Single markdown upload
  - **Phase 4 (US2)**: Can start after US1 stable (P2 priority) - Depends on MarkdownParser from US1
  - **Phase 5 (US3)**: Can start after US1 stable (P2 priority) - Reuses parsing logic from US1
  - **Phase 6 (US4)**: Can start after US2 stable (P3 priority) - Extends metadata extraction from US2
  - **Phase 7 (US5)**: Can start after US1 stable (P4 priority) - Edge case handling independent
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Single Markdown Upload - No dependencies on other stories, blocks most other stories
- **User Story 2 (P2)**: Markdown Formatting - Depends on US1 MarkdownParser, extends it with frontmatter/images
- **User Story 3 (P2)**: Folder Upload - Depends on US1 parsing logic, reuses document creation workflow
- **User Story 4 (P3)**: Special Content - Depends on US2 metadata extraction, adds Mermaid handling
- **User Story 5 (P4)**: Edge Cases - Independent of other stories, adds validation layer

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Utility functions (frontmatter.py, image_extractor.py) before parser methods
- Parser implementation before API endpoints
- Database repositories before Dramatiq tasks
- Core implementation before integration

### Parallel Opportunities

**Phase 1 (Setup)**: T002, T003, T004, T005, T006, T007, T008 can all run in parallel

**Phase 2 (Foundational)**: T015, T016, T017, T019, T020 can run in parallel

**Phase 3 (US1 - Tests)**: T023, T024, T025, T026, T027 can all run in parallel

**Phase 3 (US1 - Implementation)**: T028, T029 can start in parallel

**Phase 4 (US2 - Tests)**: T043, T044, T045, T046, T047 can all run in parallel

**Phase 4 (US2 - Utilities)**: T048, T053 can run in parallel (frontmatter.py, image_extractor.py)

**Phase 5 (US3 - Tests)**: T064, T065, T066, T067, T068 can all run in parallel

**Phase 5 (US3 - Implementation)**: T069, T070 can start in parallel

**Phase 6 (US4 - Tests)**: T091, T092, T093, T094, T095 can all run in parallel

**Phase 6 (US4 - Utilities)**: T096, T097 can run in parallel

**Phase 7 (US5 - Tests)**: T108, T109, T110, T111, T112 can all run in parallel

**Phase 8 (Polish)**: T125, T126, T127, T128, T129, T130, T131, T132, T137, T138, T140, T142, T145, T148 can run in parallel

**Cross-Story Parallelism**: Once Foundational (Phase 2) completes, Phase 3 (US1) must complete first. Then Phase 4 (US2) and Phase 5 (US3) can proceed in parallel as US2 extends US1 and US3 reuses US1.

---

## Parallel Example: User Story 1 (Single Markdown Upload)

```bash
# Launch all tests for User Story 1 together:
Task T023: "Contract test for markdown upload in tests/integration/test_markdown_upload_api.py"
Task T024: "Integration test for markdown parsing workflow"
Task T025: "Unit test for MarkdownParser"
Task T026: "Unit test for markdown validation"
Task T027: "Unit test for structural element extraction"

# After tests complete, launch base classes in parallel:
Task T028: "Create BaseParser interface"
Task T029: "Create MarkdownParser class"
```

---

## Parallel Example: User Story 2 (Markdown Formatting)

```bash
# Launch all tests for User Story 2 together:
Task T043: "Unit test for frontmatter extraction"
Task T044: "Unit test for code block detection"
Task T045: "Unit test for link extraction"
Task T046: "Unit test for table parsing"
Task T047: "Integration test for GET /markdown-metadata"

# After tests complete, launch utility modules in parallel:
Task T048: "Create frontmatter.py"
Task T053: "Create image_extractor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → T001-T008
2. Complete Phase 2: Foundational (CRITICAL) → T009-T022
3. Complete Phase 3: User Story 1 (Single Markdown Upload) → T023-T042
4. **STOP and VALIDATE**: Test end-to-end: upload markdown → parse → verify text extracted and chunks created
5. Deploy/demo MVP (can upload and parse single markdown documents)

**MVP Deliverable**: Users can upload markdown files, system automatically parses with structure preserved, ready for RAG queries.

### Incremental Delivery

1. Complete Setup + Foundational → T001-T022 (Foundation ready)
2. Add User Story 1 → T023-T042 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Formatting) → T043-T063 → Test independently → Deploy/Demo (frontmatter, images)
4. Add User Story 3 (Folders) → T064-T090 → Test independently → Deploy/Demo (batch folders)
5. Add User Story 4 (Special Content) → T091-T107 → Test independently → Deploy/Demo (Mermaid)
6. Optional: Add User Story 5 (Edge Cases) → T108-T124 → Test independently
7. Polish → T125-T148 → Production ready

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T022)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (Single Upload) → T023-T042
3. **After US1 complete, split work**:
   - **Developer A**: User Story 2 (Formatting) → T043-T063
   - **Developer B**: User Story 3 (Folders) → T064-T090
4. **After US2/US3 complete**:
   - **Developer A**: User Story 4 (Special Content) → T091-T107
   - **Developer B**: User Story 5 (Edge Cases) → T108-T124
   - **Developer C**: Polish & Metrics → T125-T148
5. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 148

**By Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 14 tasks (BLOCKS everything)
- Phase 3 (US1 - Single Markdown Upload, P1): 20 tasks
- Phase 4 (US2 - Markdown Formatting, P2): 21 tasks
- Phase 5 (US3 - Folder Upload, P2): 27 tasks
- Phase 6 (US4 - Special Content, P3): 17 tasks
- Phase 7 (US5 - Edge Cases, P4): 17 tasks
- Phase 8 (Polish): 24 tasks

**By User Story**:
- User Story 1 (Single Markdown Upload): 20 tasks
- User Story 2 (Markdown Formatting): 21 tasks
- User Story 3 (Folder Upload): 27 tasks
- User Story 4 (Special Content): 17 tasks
- User Story 5 (Edge Cases): 17 tasks
- Infrastructure (Setup + Foundational): 22 tasks
- Polish: 24 tasks

**Parallel Opportunities**: 50+ tasks can run in parallel within their phases

**Independent Test Criteria**:
- US1: Upload markdown → verify text extracted with structure preserved and chunks created
- US2: Upload markdown with frontmatter → verify metadata extracted separately
- US3: Upload folder with 10 files → verify all discovered and processed with progress tracking
- US4: Upload markdown with Mermaid → verify diagram code extracted and searchable
- US5: Upload empty/malformed markdown → verify graceful handling with appropriate errors

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) = 42 tasks

**Format Validation**: ✅ All 148 tasks follow the required checklist format with checkboxes, task IDs, parallelization markers, story labels, and file paths.

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
- Tests are included for comprehensive coverage (80%+ target per project standards)
- Marko library (already installed) used for markdown parsing, python-frontmatter added for YAML
- Folder traversal uses pathlib with inode tracking for circular reference prevention
- Hierarchical batch model: FolderBatch orchestrates individual Document parsing tasks
