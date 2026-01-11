# Implementation Plan: Markdown File Ingestion

**Branch**: `003-markdown-ingestion` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-markdown-ingestion/spec.md`

## Summary

Extend the existing document processing pipeline to support markdown files (.md, .markdown) with comprehensive parsing capabilities including:
- **Single & Folder Upload**: Process individual markdown files or entire folder structures with recursive discovery
- **Advanced Parsing**: Extract frontmatter metadata, code blocks (including Mermaid diagrams), links, images, and tables
- **RAG Integration**: Chunk parsed content using existing 512-token chunking strategy for vector search and chat queries
- **Graceful Degradation**: Handle images and special content by extraction as metadata, deferring OCR for future enhancement

**Technical Approach**: Create `MarkdownParser` following existing `BaseParser` interface, integrate with `ParserFactory`, leverage Python-Markdown or marko library for parsing, implement folder traversal service, reuse existing chunking/RAG infrastructure.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI 0.128+, SQLAlchemy 2.0+ (async), Dramatiq 2.0, structlog 25.5+  
**Markdown Parsing**: marko 2.2.2 (already in requirements.txt), python-frontmatter (to add)  
**Storage**: PostgreSQL 14+ with pgvector for embeddings (1536-dimensional)  
**Testing**: pytest 9.0+, pytest-asyncio 1.3+, pytest-mock 3.15+  
**Target Platform**: Linux/macOS server (Docker containerized)  
**Project Type**: Web application (FastAPI backend + Next.js frontend)  
**Performance Goals**: 
- Parse 10,000-line markdown files in <30 seconds
- Process folder with 100 files in <5 minutes
- Handle 100 concurrent parsing jobs without degradation  
**Constraints**: 
- Existing file size limits (10 MB per document)
- Quota management per tenant
- Async processing via Dramatiq task queue
- 512-token chunks with 50-token overlap (tiktoken cl100k_base encoding)  
**Scale/Scope**: 
- Support 10-500 markdown files per folder upload
- Handle directory structures up to 20 levels deep
- Maintain 98% parsing accuracy for text extraction
- 85% RAG retrieval accuracy for chunked content

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles

✅ **Modularity**: Markdown parser implemented as standalone module following existing `BaseParser` interface  
✅ **Consistency**: Reuse existing patterns (ParserFactory, async Dramatiq tasks, chunking service, quota management)  
✅ **Testing**: TDD approach with unit tests for parser, integration tests for upload/parsing workflow  
✅ **Type Safety**: Full type annotations using Python 3.12+ syntax, mypy strict mode compliance  
✅ **Observability**: Structured logging with structlog for all parsing operations and folder traversal  
✅ **Error Handling**: Graceful degradation for malformed markdown, clear user-facing error messages

### Constraints

✅ **No New Infrastructure**: Leverage existing PostgreSQL, pgvector, Redis, Dramatiq infrastructure  
✅ **Backward Compatibility**: No breaking changes to existing Document/Chunk models or upload APIs  
✅ **Security**: Apply existing malware scanning (ClamAV) and validation patterns to markdown files  
✅ **Performance**: Reuse existing async patterns, no blocking I/O in API handlers

### Quality Gates

✅ **Code Coverage**: Maintain ≥80% coverage (project standard from pyproject.toml)  
✅ **Linting**: Pass Ruff checks with project configuration  
✅ **Type Checking**: Pass mypy strict checks  
✅ **Integration Tests**: Cover single file, batch folder, RAG query end-to-end flows

**Gate Status**: ✅ PASSED - No constitution violations. Feature extends existing architecture patterns without introducing complexity.

## Project Structure

### Documentation (this feature)

```text
specs/003-markdown-ingestion/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (completed)
├── research.md          # Phase 0 output (markdown libraries, Mermaid handling)
├── data-model.md        # Phase 1 output (MarkdownMetadata, FolderBatch entities)
├── quickstart.md        # Phase 1 output (developer setup, testing guide)
├── checklists/
│   └── requirements.md  # Spec validation checklist (completed)
└── contracts/
    ├── markdown-upload-api.yaml      # OpenAPI spec for markdown upload endpoint
    ├── folder-upload-api.yaml        # OpenAPI spec for folder upload endpoint
    └── markdown-parsing-events.yaml  # Dramatiq task contracts
```

### Source Code (repository root)

```text
src/
├── ingestion_parsing/
│   ├── parsers/
│   │   ├── base.py                 # [Existing] BaseParser interface
│   │   ├── parser_factory.py       # [Modified] Add markdown MIME types
│   │   ├── pdf_parser.py           # [Existing] Reference implementation
│   │   ├── markdown_parser.py      # [New] MarkdownParser implementation
│   │   └── markdown/               # [New] Markdown-specific utilities
│   │       ├── __init__.py
│   │       ├── frontmatter.py      # YAML frontmatter extraction
│   │       ├── mermaid.py          # Mermaid diagram detection
│   │       ├── image_extractor.py  # Image reference extraction
│   │       └── structure.py        # Structural element identification
│   ├── services/
│   │   ├── chunking_service.py     # [Existing] Reuse for markdown chunks
│   │   ├── upload_service.py       # [Modified] Add markdown validation
│   │   ├── folder_service.py       # [New] Folder traversal & batch processing
│   │   └── malware_scanner.py      # [Existing] Apply to markdown files
│   ├── tasks/
│   │   ├── parsing_tasks.py        # [Modified] Add markdown parsing task
│   │   └── folder_tasks.py         # [New] Folder batch processing task
│   └── models/
│       ├── parsing_result.py       # [Modified] Add markdown-specific metadata
│       └── folder_batch.py         # [New] FolderBatch entity
│
├── storage_indexing/
│   ├── models/
│   │   ├── document.py             # [Existing] Reuse for markdown documents
│   │   ├── chunk.py                # [Existing] Reuse for markdown chunks
│   │   ├── markdown_metadata.py   # [New] MarkdownMetadata model
│   │   └── folder_batch.py        # [New] FolderBatch ORM model
│   ├── repositories/
│   │   └── markdown_repository.py  # [New] Markdown-specific queries
│   └── migrations/
│       └── versions/
│           └── XXXX_add_markdown_support.py  # [New] Migration script
│
├── api/
│   └── routes/
│       ├── documents.py            # [Modified] Add folder upload endpoint
│       └── processing.py           # [Existing] Reuse for folder batch status
│
└── shared/
    ├── config.py                   # [Modified] Add markdown-specific settings
    └── validators.py               # [Modified] Add markdown file validators

tests/
├── unit/
│   ├── test_markdown_parser.py     # [New] Parser unit tests
│   ├── test_folder_service.py      # [New] Folder traversal tests
│   ├── test_frontmatter.py         # [New] Frontmatter extraction tests
│   └── test_mermaid.py             # [New] Mermaid detection tests
├── integration/
│   ├── test_markdown_upload_api.py # [New] Single file upload tests
│   ├── test_folder_upload_api.py   # [New] Folder upload integration tests
│   └── test_markdown_rag.py        # [New] End-to-end RAG query tests
└── fixtures/
    └── sample_documents/
        ├── sample.md               # [New] Basic markdown test file
        ├── with_frontmatter.md     # [New] Markdown with YAML frontmatter
        ├── with_mermaid.md         # [New] Markdown with Mermaid diagrams
        ├── with_images.md          # [New] Markdown with image references
        └── test_folder/            # [New] Nested folder structure for testing
            ├── doc1.md
            ├── doc2.md
            └── subfolder/
                └── doc3.md
```

**Structure Decision**: Web application pattern (Option 2) - backend-focused with FastAPI. This feature primarily extends backend document processing capabilities. Frontend changes are minimal (reuse existing upload UI, add folder selection). The implementation follows the established modular architecture with clear separation between parsers, services, models, and API routes.

## Complexity Tracking

> **No violations identified - this section intentionally left empty per constitution compliance.**

---

## Phase 0: Research & Planning

*Output file: `research.md`*

### Research Tasks

The following areas require investigation to resolve technical decisions before implementation:

1. **Markdown Parsing Library Selection**
   - **Question**: Which Python markdown library best supports CommonMark/GFM, frontmatter extraction, and structural element identification?
   - **Options**: marko (already in requirements.txt), python-markdown, markdown-it-py, mistune
   - **Criteria**: GFM table support, code block metadata, extensibility for custom syntax, performance
   - **Research**: Compare parsing accuracy, API ergonomics, maintenance status, community support

2. **Frontmatter Extraction**
   - **Question**: Best approach for YAML/TOML frontmatter parsing from markdown?
   - **Options**: python-frontmatter library, manual regex extraction, markdown library extensions
   - **Criteria**: Robustness (malformed YAML), performance, error handling
   - **Research**: Test with edge cases (multiple delimiters, nested YAML, missing closing delimiter)

3. **Mermaid Diagram Handling**
   - **Question**: How to identify, extract, and optionally convert Mermaid diagrams to text descriptions?
   - **Options**: 
     - Extract as-is (code string) for metadata
     - Convert to plaintext description via mermaid-py
     - Defer rendering, store syntax for future visualization
   - **Criteria**: RAG search utility, implementation complexity, future extensibility
   - **Research**: Assess impact on search quality, library availability for conversion

4. **Folder Traversal Strategy**
   - **Question**: Optimal approach for recursive folder processing with symbolic link handling?
   - **Options**: 
     - os.walk with link following detection
     - pathlib.Path.rglob with visited set
     - asyncio concurrent traversal
   - **Criteria**: Circular reference prevention, performance for large trees, memory efficiency
   - **Research**: Test with symlink cycles, deeply nested structures, large file counts

5. **Image Reference Extraction**
   - **Question**: How to extract and validate image references (URLs, local paths, base64)?
   - **Options**: Regex patterns, markdown AST traversal, PIL for base64 validation
   - **Criteria**: Accuracy (handle edge cases), alt text extraction, relative path resolution
   - **Research**: Test with various markdown image syntaxes, embedded HTML img tags

6. **Batch Processing Orchestration**
   - **Question**: Should folder upload create single batch job or individual jobs per file?
   - **Options**:
     - Single FolderBatch job → spawns child parsing jobs (hierarchical)
     - Flat structure: create all document records upfront, queue parsing tasks
   - **Criteria**: Progress tracking granularity, retry logic, partial failure handling
   - **Research**: Align with existing batch upload patterns in spec 002

7. **MIME Type Handling**
   - **Question**: Proper MIME type detection for .md files (varies: text/markdown, text/plain, text/x-markdown)?
   - **Options**: python-magic detection, file extension mapping, Accept header negotiation
   - **Criteria**: Consistency with existing parsers, robustness across file sources
   - **Research**: Test python-magic detection accuracy, define canonical MIME type

### Expected Research Outcomes

**Decision Log**: Documented choices for each research area with:
- Selected option and rationale
- Alternatives considered and rejection reasons
- Implementation considerations
- Test strategy for the chosen approach

**Prototype Validation**: Small proof-of-concept scripts for:
- Markdown parsing with selected library
- Folder traversal with circular reference handling
- Frontmatter extraction with edge cases

**Performance Baselines**: Benchmarks for:
- Parsing 10,000-line markdown file
- Traversing folder with 100 files, 5 levels deep
- Chunking markdown with complex formatting

---

## Phase 1: Design & Implementation Artifacts

*Output files: `data-model.md`, `contracts/`, `quickstart.md`*

### Data Model

**New Entities** (detailed in `data-model.md`):

1. **MarkdownMetadata** (extends DocumentMetadata)
   - Fields: frontmatter (JSONB), heading_count, code_block_count, mermaid_diagram_count, table_count, link_urls, image_references
   - Relationships: One-to-one with Document
   - Indexes: frontmatter JSONB GIN index for metadata queries

2. **FolderBatch**
   - Fields: batch_id, tenant_id, user_id, folder_path, total_files_discovered, files_processed, files_failed, status, created_at, completed_at
   - Relationships: One-to-many with Document (documents discovered in batch)
   - Status enum: discovering, processing, completed, partial_failure, failed

3. **ImageReference**
   - Fields: document_id, image_url, alt_text, is_local_path, is_base64, relative_path, ocr_pending
   - Relationships: Many-to-one with Document
   - Future use: ocr_pending flag for optional image-to-text processing

4. **StructuralElement** (extended)
   - New type: mermaid_diagram (add to existing heading, paragraph, list, code_block, table)
   - Fields: element_type, content, metadata (JSONB for diagram_type, language, level)

**Modified Entities**:

- **Document**: No schema changes required (mime_type handles text/markdown)
- **ParsingJob**: No schema changes required (reuse existing status tracking)
- **Chunk**: No schema changes required (markdown chunks use same structure)

### API Contracts

**New Endpoints** (detailed OpenAPI specs in `contracts/`):

1. **POST /api/v1/documents/upload-folder**
   - Request: multipart/form-data with folder structure (FormData with multiple files)
   - Response: FolderBatch with batch_id, total_files_discovered, status URL
   - Behavior: Recursively discover .md files, create FolderBatch and Document records, queue parsing tasks

2. **GET /api/v1/documents/folder-batches/{batch_id}**
   - Response: FolderBatch status with progress (files_processed / total_files_discovered)
   - Include list of document IDs for successfully processed files

**Modified Endpoints**:

3. **POST /api/v1/documents/upload** (existing)
   - Add support for .md and .markdown extensions
   - Add markdown MIME type validation

4. **POST /api/v1/documents/batch-upload** (existing)
   - Already supports multiple files; ensure markdown files are accepted

**Dramatiq Tasks** (contracts in `contracts/markdown-parsing-events.yaml`):

5. **parse_markdown_document**
   - Input: document_id, file_path
   - Output: parsing_result with text content, metadata, structural elements
   - Emits: document_parsed event

6. **process_folder_batch**
   - Input: batch_id
   - Output: batch status update
   - Behavior: Orchestrates individual markdown parsing tasks

### Integration Points

- **Existing Chunking Service**: Pass parsed markdown text to `ChunkingService.chunk_document()`
- **Existing Upload Service**: Extend `UploadService.validate_file()` for markdown MIME types
- **Existing Malware Scanner**: Apply `MalwareScanner.scan_file()` to markdown files
- **Existing RAG Pipeline**: Markdown chunks indexed in pgvector same as PDF/DOCX chunks

### Migration Strategy

**Database Migration** (`migrations/versions/XXXX_add_markdown_support.py`):
1. Add `markdown_metadata` table with foreign key to documents
2. Add `folder_batches` table
3. Add `image_references` table
4. Create indexes: markdown_metadata.frontmatter (GIN), folder_batches.status
5. Add check constraint: document.mime_type IN ('text/markdown', 'text/x-markdown')

**Backward Compatibility**:
- No changes to existing Document/Chunk schemas
- Existing upload endpoints continue to work unchanged
- New markdown support is additive only

### Testing Strategy

**Unit Tests**:
- MarkdownParser: frontmatter extraction, code block identification, Mermaid detection
- FolderService: recursive traversal, symlink handling, file count accuracy
- Image extractor: URL extraction, alt text parsing, base64 detection

**Integration Tests**:
- Single markdown upload → parsing → chunking → RAG query
- Folder upload → batch processing → partial failure handling
- Markdown with various edge cases (empty, malformed, HTML)

**Performance Tests**:
- 10,000-line markdown file parsing <30s
- 100-file folder processing <5 minutes
- 100 concurrent markdown parsing jobs

---

## Phase 2: Task Breakdown

*DEFERRED: This phase is handled by the `/speckit.tasks` command (not part of `/speckit.plan`).*

Task breakdown will include:
- [ ] Implement MarkdownParser with BaseParser interface
- [ ] Create folder traversal service
- [ ] Add database migrations for new entities
- [ ] Extend ParserFactory for markdown MIME types
- [ ] Implement folder upload API endpoint
- [ ] Add comprehensive test suite
- [ ] Update documentation and examples

---

## Next Steps

1. ✅ **Specification Complete**: `spec.md` approved with all requirements defined
2. ✅ **Planning Complete**: This document (`plan.md`) provides technical approach
3. **Execute Phase 0**: Generate `research.md` by investigating the 7 research areas above
4. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md` after research conclusions
5. **Update Agent Context**: Run `.specify/scripts/bash/update-agent-context.sh cursor-agent` to add markdown-specific context
6. **Task Breakdown**: Run `/speckit.tasks` to create actionable implementation tasks

**Ready for**: Phase 0 Research execution (`research.md` generation)

