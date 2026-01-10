# Implementation Plan: Document Upload and Parsing

**Branch**: `002-doc-upload-parsing` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-doc-upload-parsing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a production-ready document upload and parsing system that allows users to upload documents in multiple formats (PDF, DOCX, TXT), extract text content, chunk documents for vector search, and track processing status asynchronously. The system will integrate with the existing FastAPI backend, PostgreSQL database with pgvector, and support batch uploads with real-time progress tracking.

**Key Requirements**: Multi-format document ingestion (PDF, DOCX, TXT), text extraction with 95%+ accuracy, asynchronous processing with retry logic, real-time status tracking, malware scanning, storage quota enforcement, and chunking for RAG pipelines.

**Technical Approach**: FastAPI multipart file upload endpoints, Docling for document parsing, async Celery/Dramatiq workers for background processing, PostgreSQL for metadata and chunks with pgvector embeddings, Redis for job queues and caching, and S3-compatible object storage for file persistence.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI 0.109+, Docling (IBM), python-magic (file type detection), python-multipart (file uploads), aiofiles (async I/O), Celery/Dramatiq (task queue), boto3 (S3 storage)  
**Storage**: PostgreSQL 16 with pgvector (metadata + chunks), S3-compatible object storage or local filesystem (original files), Redis 7 (job queue + caching)  
**Testing**: pytest 8.0+, pytest-asyncio (async tests), pytest-mock (mocking), httpx (API testing), faker (test data generation)  
**Target Platform**: Linux server (production), macOS (development)  
**Project Type**: Web application (FastAPI backend + Next.js frontend)  
**Performance Goals**: 
- Upload: Accept 50MB files within 30 seconds
- Parsing: Process 10MB documents within 2 minutes
- Throughput: Handle 100 concurrent uploads
- Accuracy: 95%+ text extraction accuracy

**Constraints**: 
- File size: 50MB maximum per upload
- Storage quota: Per-tenant limits enforced
- Network: Resumable uploads for large files
- Processing: Max 3 retry attempts with exponential backoff
- Malware scanning: ClamAV integration or cloud-based scanning

**Scale/Scope**: 
- Users: 1,000+ concurrent users
- Documents: 100,000+ documents per tenant
- Daily uploads: 10,000+ documents
- Formats: PDF, DOCX, TXT (initial), expandable architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Evaluation

**I. Modular Architecture** ✅
- Document parsing implemented in dedicated `ingestion_parsing/` module
- Clear separation: upload (API) → parsing (service) → storage (repository)
- No violations

**II. Type Safety (NON-NEGOTIABLE)** ✅
- All functions will have complete type annotations using Python 3.12 typing
- Pydantic models for API contracts and configuration
- mypy strict mode enforced
- No violations

**III. Test-First Development (NON-NEGOTIABLE)** ✅
- Tests written before implementation for all critical paths
- Target: 85%+ coverage for document parsing module
- Contract tests for API endpoints
- Integration tests for parsing workflows
- No violations

**IV. Async-First Pattern** ✅
- FastAPI async endpoints for uploads
- Async file I/O with aiofiles
- Async database operations with SQLAlchemy
- Background task processing decoupled from API
- No violations

**V. Multi-Tenant Isolation** ✅
- Row-level tenant_id enforcement on Document and ProcessingJob models
- Storage path isolation: `/{tenant_id}/{document_id}/`
- Quota enforcement per tenant
- No violations

**VI. Observability** ✅
- Structured logging with structlog for all operations
- Metrics: upload duration, parsing success rate, error types
- Request ID propagation through async tasks
- No violations

### Additional Standards

**Security Requirements** ✅
- File type validation (magic bytes, not extension)
- Malware scanning before storage
- Path traversal prevention
- Authentication required for all upload endpoints
- No violations

**Performance Standards** ✅
- Streaming uploads to avoid memory exhaustion
- Chunked processing for large documents
- Connection pooling for database and storage
- No violations

### GATE STATUS: ✅ PASSED

All constitution checks pass. No complexity violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-doc-upload-parsing/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - Technology decisions and best practices
├── data-model.md        # Phase 1 output - Extended schema for upload/parsing
├── quickstart.md        # Phase 1 output - Developer setup for document features
├── contracts/           # Phase 1 output - API specifications
│   ├── upload-api.yaml      # Document upload endpoints
│   ├── parsing-api.yaml     # Document parsing status endpoints
│   └── document-api.yaml    # Document management CRUD
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Backend structure (extends existing src/)
src/
├── api/
│   ├── main.py                      # Existing FastAPI app (update CORS, file size limits)
│   ├── dependencies.py              # Existing DI (add file storage, task queue deps)
│   ├── routes/
│   │   ├── health.py                # Existing
│   │   ├── documents.py             # NEW: Upload, list, get, delete documents
│   │   └── processing.py            # NEW: Job status, retry, cancel
│   └── middleware/
│       ├── request_id.py            # Existing or NEW: Request ID tracking
│       ├── error_handler.py         # Existing or NEW: Standardized error responses
│       └── logging.py               # Existing or NEW: Request/response logging
│
├── ingestion_parsing/
│   ├── __init__.py
│   ├── README.md                    # UPDATE: Module documentation
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base.py                  # NEW: Abstract parser interface
│   │   ├── pdf_parser.py            # NEW: Docling-based PDF parsing
│   │   ├── docx_parser.py           # NEW: python-docx parsing
│   │   ├── txt_parser.py            # NEW: Simple text parsing
│   │   └── parser_factory.py        # NEW: Format detection and parser selection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── upload_service.py        # NEW: Handle file uploads, validation
│   │   ├── parsing_service.py       # NEW: Orchestrate parsing workflow
│   │   ├── chunking_service.py      # NEW: Split documents into chunks
│   │   └── malware_scanner.py       # NEW: ClamAV or cloud-based scanning
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── file_storage.py          # NEW: S3 or local filesystem abstraction
│   │   └── quota_manager.py         # NEW: Track and enforce storage quotas
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── worker.py                # NEW: Celery/Dramatiq worker configuration
│   │   └── document_tasks.py        # NEW: Async parsing task definitions
│   └── models/
│       ├── __init__.py
│       ├── upload_request.py        # NEW: Pydantic models for API requests
│       └── parsing_result.py        # NEW: Pydantic models for parsing results
│
├── storage_indexing/
│   ├── database.py                  # Existing database connection
│   ├── models/
│   │   ├── document.py              # UPDATE: Add fields (content_hash, language, page_count)
│   │   ├── document_chunk.py        # UPDATE: Add fields (chunk_type, start_page, end_page)
│   │   ├── processing_job.py        # UPDATE: Add fields (progress_percent, estimated_time_remaining)
│   │   └── tenant.py                # UPDATE: Add storage_quota_bytes, storage_used_bytes
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── document_repository.py   # NEW: Document CRUD operations
│   │   ├── chunk_repository.py      # NEW: Chunk CRUD operations
│   │   └── job_repository.py        # NEW: Job status queries and updates
│   └── migrations/
│       └── versions/
│           └── XXXX_add_upload_fields.py  # NEW: Migration for extended schema
│
├── shared/
│   ├── config.py                    # UPDATE: Add upload settings, storage config
│   ├── exceptions.py                # UPDATE: Add upload-specific exceptions
│   ├── logging_config.py            # Existing
│   └── validators.py                # NEW: File type, size, content validators
│
└── rag_orchestration/               # Future integration point
    └── README.md                    # Document chunking integration

# Frontend structure (extends existing frontend/)
frontend/
├── app/
│   ├── documents/
│   │   ├── page.tsx                 # NEW: Document list page
│   │   ├── upload/
│   │   │   └── page.tsx             # NEW: Document upload page
│   │   └── [id]/
│   │       └── page.tsx             # NEW: Document detail page
│   └── api/                         # Optional: API route handlers
│       └── upload/
│           └── route.ts             # NEW: Client-side upload proxy (if needed)
│
├── components/
│   ├── documents/
│   │   ├── upload-dropzone.tsx      # NEW: Drag-and-drop upload component
│   │   ├── upload-progress.tsx      # NEW: Upload progress bars
│   │   ├── document-list.tsx        # NEW: Document table/grid
│   │   ├── document-card.tsx        # NEW: Individual document card
│   │   └── processing-status.tsx    # NEW: Job status badge
│   └── ui/                          # Existing shadcn components
│
└── lib/
    ├── api/
    │   ├── documents.ts             # NEW: Document API client functions
    │   └── uploads.ts               # NEW: Upload with progress tracking
    └── hooks/
        ├── use-upload.ts            # NEW: Upload hook with progress
        └── use-document-status.ts   # NEW: Polling hook for job status

# Testing structure
tests/
├── unit/
│   ├── test_parsers.py              # NEW: Unit tests for each parser
│   ├── test_upload_service.py       # NEW: Upload service logic tests
│   ├── test_chunking_service.py     # NEW: Chunking algorithm tests
│   ├── test_validators.py           # NEW: File validation tests
│   └── test_quota_manager.py        # NEW: Quota enforcement tests
│
├── integration/
│   ├── test_upload_api.py           # NEW: End-to-end upload flow
│   ├── test_parsing_workflow.py    # NEW: Full parsing pipeline
│   ├── test_document_api.py         # NEW: Document CRUD operations
│   └── test_storage.py              # NEW: File storage integration
│
└── fixtures/
    ├── sample_documents/            # NEW: Test files (PDF, DOCX, TXT)
    │   ├── sample.pdf
    │   ├── sample.docx
    │   ├── sample.txt
    │   ├── large.pdf                # NEW: Large file for testing
    │   ├── corrupted.pdf            # NEW: Invalid file for error testing
    │   └── malicious.txt            # NEW: Malware test file (EICAR)
    └── document_factory.py          # NEW: Test data factories

# Configuration
config/
└── settings.py                      # UPDATE: Add UploadSettings, StorageSettings

# Scripts
scripts/
├── setup_storage.sh                 # NEW: Initialize S3 buckets or local storage
├── test_parsers.py                  # NEW: Manual parser testing script
└── seed_documents.py                # NEW: Create test documents in DB

# Docker
docker-compose.yml                   # UPDATE: Add Celery/Dramatiq worker, optional ClamAV
```

**Structure Decision**: Web application (backend + frontend) structure selected based on existing AgenticOmni architecture. The backend extends the `src/` modular design with a fully implemented `ingestion_parsing/` module that was previously scaffolded. Frontend extends the existing Next.js 14 structure with document-specific pages and components. All paths reference the existing project structure captured in the project layout.

## Complexity Tracking

> **No complexity violations detected. This section intentionally left empty.**

---

## Phase 0: Research & Technology Decisions

### Research Tasks

The following research tasks must be completed before proceeding to Phase 1 design:

1. **Document Parsing Library Selection**
   - Evaluate Docling (IBM) vs. PyMuPDF vs. pypdf vs. pdfplumber
   - Requirements: Text extraction accuracy, table handling, OCR integration, license compatibility
   - Decision criteria: Accuracy (95%+), performance (<2 min for 10MB), maintainability

2. **File Type Detection Strategy**
   - Research python-magic vs. filetype vs. puremagic
   - Requirements: Magic byte inspection, MIME type detection, malicious file detection
   - Decision criteria: Accuracy, cross-platform compatibility (Linux + macOS)

3. **Asynchronous Task Queue**
   - Evaluate Celery vs. Dramatiq vs. Huey vs. RQ
   - Requirements: Redis backend, retry logic, progress tracking, monitoring
   - Decision criteria: FastAPI integration, reliability, observability

4. **Object Storage Solution**
   - Research S3 (AWS) vs. MinIO (self-hosted) vs. local filesystem with backup
   - Requirements: Scalability, cost, multi-tenant isolation, backup strategy
   - Decision criteria: Development simplicity, production readiness, cost

5. **Malware Scanning Approach**
   - Evaluate ClamAV (self-hosted) vs. VirusTotal API vs. cloud-based services
   - Requirements: Real-time scanning, false positive rate, cost
   - Decision criteria: Security, latency (<5s), operational complexity

6. **Document Chunking Strategy**
   - Research semantic chunking vs. fixed-size vs. sentence-based
   - Requirements: Preserve context, optimal for vector search, handle tables/lists
   - Decision criteria: RAG retrieval accuracy, implementation complexity

7. **Resumable Upload Implementation**
   - Evaluate tus protocol vs. custom multipart uploads vs. presigned URLs
   - Requirements: Handle network interruptions, progress tracking, browser compatibility
   - Decision criteria: Client library availability, server complexity

8. **DOCX Parsing Library**
   - Research python-docx vs. docx2txt vs. mammoth
   - Requirements: Text extraction, formatting preservation, table handling
   - Decision criteria: Accuracy, active maintenance, edge case handling

### Research Output

A `research.md` file will be generated with the following structure for each decision:

```markdown
## Decision: [Technology/Approach Name]

### Rationale
[Why this was chosen based on requirements and criteria]

### Alternatives Considered
- **Alternative 1**: [Pros/Cons, why rejected]
- **Alternative 2**: [Pros/Cons, why rejected]

### Implementation Notes
[Key considerations for implementation, gotchas, configuration]

### References
- [Documentation links, benchmarks, community discussions]
```

---

## Phase 1: Design & Contracts

### Deliverable 1: Data Model Extensions (`data-model.md`)

Extend the existing database schema with fields and entities for document upload and parsing:

#### Extended Entities

**Document Model Updates**:
- Add `content_hash` (string, SHA-256): Detect duplicate uploads
- Add `language` (string, ISO 639-1): Extracted document language
- Add `page_count` (int, nullable): Number of pages in document
- Add `uploaded_by` (int, FK to users.user_id): Uploading user
- Add `original_filename` (string): Preserve original name
- Add `mime_type` (string): Detected MIME type

**DocumentChunk Model Updates**:
- Add `chunk_type` (enum: text, table, list, heading): Semantic type
- Add `start_page` (int, nullable): Starting page number
- Add `end_page` (int, nullable): Ending page number
- Add `token_count` (int): Approximate tokens for LLM context

**ProcessingJob Model Updates**:
- Add `progress_percent` (float, 0-100): Current progress
- Add `estimated_time_remaining` (int, seconds, nullable): ETA
- Add `started_by` (int, FK to users.user_id): User who initiated job

**Tenant Model Updates**:
- Add `storage_quota_bytes` (bigint): Maximum storage allowed
- Add `storage_used_bytes` (bigint, default 0): Current storage usage

#### New Entity: UploadSession

```python
class UploadSession:
    """Tracks resumable upload progress for large files"""
    session_id: UUID (PK)
    tenant_id: int (FK, indexed)
    user_id: int (FK)
    filename: str
    total_size_bytes: int
    uploaded_size_bytes: int (default 0)
    chunk_size_bytes: int (default 5MB)
    storage_path: str (temporary location)
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
```

#### Validation Rules

- `file_size` must be ≤ 50MB (configurable via settings)
- `content_hash` must be unique per tenant (duplicate detection)
- `storage_used_bytes` + new file size must be ≤ `storage_quota_bytes`
- `processing_status` transitions: uploaded → parsing → parsed → failed
- `chunk_order` must be sequential and unique per document

#### State Transitions

**ProcessingJob Status Flow**:
```
pending → processing → completed
                    ↓
                  failed ← retrying
```

---

### Deliverable 2: API Contracts (`contracts/`)

Generate OpenAPI 3.0 specifications for three new API groups:

#### Upload API (`contracts/upload-api.yaml`)

**POST /api/v1/documents/upload**
- Request: `multipart/form-data` with file, metadata
- Response: `201 Created` with document ID and job ID
- Errors: `400` (invalid file), `413` (too large), `507` (quota exceeded)

**POST /api/v1/documents/upload/resumable**
- Request: Initialize resumable upload session
- Response: `201 Created` with session ID and upload URL
- Errors: `400` (invalid params), `507` (quota exceeded)

**PATCH /api/v1/documents/upload/resumable/{session_id}**
- Request: Upload chunk with byte range
- Response: `200 OK` with progress or `201 Created` when complete
- Errors: `400` (invalid range), `404` (session not found), `410` (session expired)

**POST /api/v1/documents/batch-upload**
- Request: `multipart/form-data` with multiple files
- Response: `202 Accepted` with array of document IDs and job IDs
- Errors: `400` (invalid files), `413` (batch too large), `507` (quota exceeded)

#### Document Management API (`contracts/document-api.yaml`)

**GET /api/v1/documents**
- Query params: `page`, `limit`, `status`, `file_type`, `search`
- Response: `200 OK` with paginated document list
- Errors: `400` (invalid params)

**GET /api/v1/documents/{document_id}**
- Response: `200 OK` with document details and metadata
- Errors: `404` (not found), `403` (forbidden - wrong tenant)

**GET /api/v1/documents/{document_id}/download**
- Response: `200 OK` with file stream
- Errors: `404` (not found), `403` (forbidden)

**DELETE /api/v1/documents/{document_id}**
- Response: `204 No Content`
- Errors: `404` (not found), `403` (forbidden)

**GET /api/v1/documents/{document_id}/chunks**
- Query params: `page`, `limit`
- Response: `200 OK` with paginated chunk list
- Errors: `404` (document not found)

#### Processing API (`contracts/processing-api.yaml`)

**GET /api/v1/processing/jobs/{job_id}**
- Response: `200 OK` with job status, progress, errors
- Errors: `404` (not found), `403` (forbidden)

**POST /api/v1/processing/jobs/{job_id}/retry**
- Response: `202 Accepted` with new job status
- Errors: `404` (not found), `409` (already processing), `400` (max retries reached)

**POST /api/v1/processing/jobs/{job_id}/cancel**
- Response: `200 OK` with cancelled status
- Errors: `404` (not found), `409` (already completed)

**GET /api/v1/processing/stats**
- Response: `200 OK` with processing statistics (pending, completed, failed counts)
- Errors: None (returns empty stats for new tenants)

---

### Deliverable 3: Quickstart Guide (`quickstart.md`)

A developer onboarding document with the following sections:

1. **Prerequisites**
   - Python 3.12+, Redis 7, PostgreSQL 16 with pgvector
   - Celery or Dramatiq installed
   - Optional: ClamAV for malware scanning
   - AWS S3 credentials or MinIO setup

2. **Installation Steps**
   ```bash
   # Install new dependencies
   pip install -e .[document-parsing]
   
   # Run new migrations
   alembic upgrade head
   
   # Configure storage (S3 or local)
   ./scripts/setup_storage.sh
   
   # Start Celery worker
   celery -A src.ingestion_parsing.tasks.worker worker --loglevel=info
   
   # Start FastAPI server
   uvicorn src.api.main:app --reload
   ```

3. **Configuration**
   - Add to `.env`: `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB`, `STORAGE_BACKEND`, `S3_BUCKET`
   - Configure task queue: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
   - Optional: `CLAMAV_HOST`, `CLAMAV_PORT`

4. **Smoke Tests**
   ```bash
   # Upload a test document
   curl -X POST http://localhost:8000/api/v1/documents/upload \
     -F "file=@tests/fixtures/sample_documents/sample.pdf" \
     -F "metadata={\"title\":\"Test Document\"}"
   
   # Check processing status
   curl http://localhost:8000/api/v1/processing/jobs/{job_id}
   
   # List documents
   curl http://localhost:8000/api/v1/documents?limit=10
   ```

5. **Troubleshooting**
   - Worker not processing: Check Celery logs, Redis connection
   - Upload fails: Check file size limits, storage quota, disk space
   - Parsing fails: Check Docling installation, test file validity

6. **Development Workflow**
   - Add new parser: Implement `BaseParser` interface in `parsers/`
   - Test parser: Use `scripts/test_parsers.py` with sample files
   - Monitor jobs: Check Redis queues, FastAPI logs, database

---

### Deliverable 4: Agent Context Update

Run the agent context update script to add new technologies:

```bash
.specify/scripts/bash/update-agent-context.sh cursor-agent
```

Technologies to add between `BEGIN TECH CONTEXT` and `END TECH CONTEXT` markers:
- **Docling**: IBM document parsing library for PDF/DOCX
- **python-magic**: File type detection via magic bytes
- **aiofiles**: Async file I/O operations
- **Celery/Dramatiq**: Asynchronous task queue for background processing
- **boto3**: AWS S3 SDK for object storage
- **python-multipart**: Multipart form data parsing for file uploads
- **ClamAV** (optional): Malware scanning engine

---

## Implementation Phases (Future - `/speckit.tasks`)

The task breakdown will be generated by `/speckit.tasks` command and will include:

### Phase 1: Core Upload Infrastructure (P1)
- Multipart file upload endpoint
- File validation (type, size, malware)
- Storage abstraction layer (S3/local)
- Upload session model and API

### Phase 2: Document Parsing (P1)
- Parser interface and factory
- PDF parser with Docling
- DOCX parser with python-docx
- TXT parser
- Chunking service

### Phase 3: Async Processing (P1)
- Celery/Dramatiq worker setup
- Background parsing tasks
- Job status tracking
- Retry logic with exponential backoff

### Phase 4: API Completion (P2)
- Document list/get/delete endpoints
- Processing status endpoints
- Batch upload endpoint
- Quota enforcement

### Phase 5: Frontend Integration (P2)
- Upload dropzone component
- Progress tracking UI
- Document list page
- Status polling

### Phase 6: Advanced Features (P3)
- Resumable uploads
- Duplicate detection
- Language detection
- Page count extraction

---

## Next Steps

1. **Generate `research.md`**: Research and document technology decisions for the 8 areas listed in Phase 0
2. **Generate design artifacts**: Create `data-model.md`, `contracts/`, and `quickstart.md` as specified in Phase 1
3. **Update agent context**: Run update script to add new technologies
4. **Run `/speckit.tasks`**: Generate detailed task breakdown from this plan

---

## References

- **Feature Specification**: [spec.md](./spec.md)
- **Existing Data Model**: [../001-app-skeleton-init/data-model.md](../001-app-skeleton-init/data-model.md)
- **Existing Architecture**: [../../docs/implementation-summary.md](../../docs/implementation-summary.md)
- **AgenticOmni README**: [../../README.md](../../README.md)
- **Docling Documentation**: https://github.com/docling-project/docling (to be researched)
- **FastAPI File Uploads**: https://fastapi.tiangolo.com/tutorial/request-files/
- **Celery Documentation**: https://docs.celeryq.dev/
