# Feature Specification: Markdown File Ingestion

**Feature Branch**: `003-markdown-ingestion`  
**Created**: 2026-01-10  
**Status**: Draft  
**Input**: User description: "ingest markdown files process"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Parse Markdown Documents (Priority: P1)

Users need to upload markdown (.md, .markdown) files to the document intelligence platform and have them automatically parsed, validated, and stored with their content structure preserved.

**Why this priority**: This is the core functionality that enables markdown support. Without this, users cannot work with markdown documents at all. It's the foundation for all other markdown-related features.

**Independent Test**: Can be fully tested by uploading a valid markdown file through the API and verifying that the text content is extracted and stored in the database. Delivers immediate value by making markdown documents accessible in the system.

**Acceptance Scenarios**:

1. **Given** a user has a valid markdown file (under size limits), **When** they upload it via the upload API, **Then** the system accepts the file, creates a document record, and returns a document ID
2. **Given** a markdown file is uploaded, **When** the parsing job executes, **Then** the system extracts plain text content, preserves document structure (headings, lists, code blocks), and marks the job as completed
3. **Given** a markdown file with standard formatting (headers, links, code blocks, tables), **When** the parser processes it, **Then** the content is extracted with structural information preserved in metadata
4. **Given** a user uploads a file with .md or .markdown extension, **When** the system validates it, **Then** it is routed to the markdown parser

---

### User Story 2 - Handle Markdown-Specific Formatting (Priority: P2)

Users want markdown documents to be parsed with awareness of markdown-specific elements like frontmatter metadata, code blocks with syntax highlighting indicators, and embedded images/links.

**Why this priority**: Enhances the quality of parsed content and makes search/retrieval more accurate. Not critical for basic ingestion but significantly improves user experience for markdown-heavy workflows.

**Independent Test**: Can be tested by uploading markdown files with frontmatter, code blocks, and links, then verifying that metadata is extracted separately and structural elements are identified in the parsing result.

**Acceptance Scenarios**:

1. **Given** a markdown file contains YAML frontmatter (title, author, tags), **When** the parser processes it, **Then** frontmatter is extracted as document metadata separate from body content
2. **Given** a markdown file contains code blocks with language specifiers, **When** parsed, **Then** code block content is identified and language information is preserved in metadata
3. **Given** a markdown file contains images and external links, **When** parsed, **Then** link URLs and image references are extracted as metadata
4. **Given** a markdown file contains tables, **When** parsed, **Then** table content is extracted as structured text

---

### User Story 3 - Batch Folder Ingestion with Recursive Processing (Priority: P2)

Users need to upload entire folders containing markdown files and have the system recursively discover and process all markdown files within the folder structure, creating individual document records for each file.

**Why this priority**: Critical for bulk documentation ingestion. Users often have documentation organized in folder hierarchies (e.g., GitHub repos, knowledge bases). This enables efficient onboarding of large documentation sets.

**Independent Test**: Can be tested by uploading a folder with nested subfolders containing multiple markdown files, then verifying that all files are discovered, processed individually, and stored with their relative paths preserved.

**Acceptance Scenarios**:

1. **Given** a user uploads a folder containing markdown files in nested subdirectories, **When** the system processes the folder, **Then** it recursively discovers all .md and .markdown files regardless of depth
2. **Given** a folder with 50 markdown files across multiple subdirectories is uploaded, **When** processing begins, **Then** each file is treated as a separate document with its own parsing job and progress tracking
3. **Given** a folder upload is initiated, **When** files are discovered, **Then** the system preserves the relative folder path as part of the document metadata
4. **Given** a folder contains both markdown and non-markdown files, **When** processed, **Then** only markdown files are ingested and other files are ignored without errors

---

### User Story 4 - Handle Special Markdown Content (Priority: P3)

System needs to handle markdown files containing special content types like Mermaid diagrams, embedded images, and complex formatting, extracting text content while gracefully handling non-text elements.

**Why this priority**: Enhances parsing quality for technical documentation. Many modern markdown documents include diagrams and images. While full processing is optional, graceful handling prevents parsing failures.

**Independent Test**: Can be tested by uploading markdown with Mermaid diagrams and image references, verifying that text is extracted successfully and special content is either processed or safely ignored.

**Acceptance Scenarios**:

1. **Given** a markdown file contains Mermaid diagram code blocks, **When** parsed, **Then** the diagram code is identified, extracted as metadata, and optionally converted to text description
2. **Given** a markdown file contains image references with alt text, **When** parsed, **Then** image URLs are extracted as metadata and alt text is included in the main content
3. **Given** a markdown file contains embedded base64 images, **When** parsed, **Then** the system extracts them as metadata and continues processing without failure
4. **Given** a markdown file contains local image paths, **When** parsed, **Then** paths are extracted as metadata and marked for optional OCR processing in future

---

### User Story 5 - Validate and Handle Edge Cases (Priority: P4)

System needs to gracefully handle malformed markdown, empty files, and mixed content (markdown with HTML) without crashing or losing data.

**Why this priority**: Improves robustness and user trust. While important for production quality, basic parsing can work without perfect handling of all edge cases.

**Independent Test**: Can be tested by uploading various edge case files (empty markdown, markdown with HTML tags, files with unusual formatting) and verifying appropriate error messages or successful fallback behavior.

**Acceptance Scenarios**:

1. **Given** a markdown file contains inline HTML, **When** parsed, **Then** HTML tags are either stripped or preserved based on system configuration, and parsing does not fail
2. **Given** an empty or whitespace-only markdown file is uploaded, **When** parsed, **Then** system handles it gracefully with appropriate metadata (e.g., "empty document") and does not crash
3. **Given** a very large markdown file (approaching size limits), **When** parsed, **Then** system processes it without timeout or memory issues
4. **Given** a markdown file with malformed syntax (unclosed code blocks, broken links), **When** parsed, **Then** system extracts available content and logs warnings without failing the job

---

### Edge Cases

- What happens when a markdown file contains only frontmatter and no body content?
- How does system handle markdown files with non-UTF-8 encoding (e.g., UTF-16, Latin-1)?
- What happens when a markdown file has deeply nested structures (e.g., lists within lists 10+ levels deep)?
- How does system handle markdown files that are actually other file types renamed to .md?
- What happens when markdown contains very long lines (10,000+ characters without line breaks)?
- How does system handle relative image paths and embedded base64 images?
- What happens when a folder contains hundreds or thousands of markdown files?
- How does system handle symbolic links or circular references in folder structures?
- What happens when folder paths exceed system path length limits?
- How does system handle markdown files with Mermaid diagrams that have syntax errors?
- What happens when a folder upload is interrupted mid-processing?
- How does system handle duplicate filenames in different subdirectories?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept files with `.md` and `.markdown` extensions through the existing upload endpoints
- **FR-002**: System MUST validate uploaded markdown files for proper encoding (UTF-8 preferred) and reject files that fail validation with clear error messages
- **FR-003**: System MUST parse markdown files to extract plain text content while preserving document structure (headings, paragraphs, lists, code blocks)
- **FR-004**: System MUST extract YAML frontmatter from markdown files and store it as document metadata separate from body content
- **FR-005**: System MUST identify and preserve code block language specifiers (e.g., ```python, ```javascript) in parsing metadata
- **FR-006**: System MUST handle markdown files containing inline HTML by stripping HTML tags to extract plain text
- **FR-007**: System MUST detect and extract external links and image references from markdown content and store them in metadata
- **FR-008**: System MUST process markdown tables and convert them to structured text representation
- **FR-009**: System MUST integrate markdown parser into the existing parser factory pattern following the BaseParser interface
- **FR-010**: System MUST support the same chunking strategy (512-token chunks with 50-token overlap) for markdown content as used for other document types
- **FR-011**: System MUST handle empty or whitespace-only markdown files gracefully without failing the parsing job
- **FR-012**: System MUST log parsing errors and warnings (malformed syntax, encoding issues) without stopping the ingestion process
- **FR-013**: System MUST respect existing file size limits and quota management rules for markdown files
- **FR-014**: System MUST maintain the same async processing workflow (Dramatiq tasks) for markdown as for PDF/DOCX/TXT
- **FR-015**: System MUST return the same processing status updates (0-100% progress) for markdown parsing jobs
- **FR-016**: System MUST accept folder uploads containing markdown files and recursively discover all .md and .markdown files regardless of subdirectory depth
- **FR-017**: System MUST preserve relative folder paths as part of document metadata to maintain organizational context
- **FR-018**: System MUST create separate document records and parsing jobs for each markdown file discovered in a folder upload
- **FR-019**: System MUST ignore non-markdown files in folder uploads without generating errors or stopping the batch process
- **FR-020**: System MUST handle symbolic links in folder structures by either following them once or skipping them to prevent circular references
- **FR-021**: System MUST detect and handle duplicate filenames across different subdirectories by including relative path in unique identification
- **FR-022**: System MUST identify Mermaid diagram code blocks (```mermaid) and extract them as special metadata separate from regular code blocks
- **FR-023**: System MUST extract alt text from image references in markdown and include it in the searchable content
- **FR-024**: System MUST store image URLs and paths as metadata without requiring immediate image processing
- **FR-025**: System MUST mark documents containing images for optional OCR processing in future without blocking current ingestion
- **FR-026**: System MUST chunk markdown content for RAG integration maintaining the existing 512-token chunks with 50-token overlap strategy
- **FR-027**: System MUST ensure all ingested markdown content is immediately available for RAG-based chat and query operations after chunking completes

### Key Entities

- **MarkdownDocument**: Represents an uploaded markdown file with extracted content and metadata
  - Inherits from existing Document model
  - Contains: document_id, filename, file_size, mime_type (text/markdown), upload timestamp
  - Relationships: Associated with parsing_job, chunks, and tenant

- **MarkdownMetadata**: Structured metadata extracted from markdown files
  - Attributes: frontmatter (JSON/YAML), heading_count, code_block_count, link_urls, image_references, table_count
  - Associated with parent Document record

- **StructuralElement**: Identified structural components within markdown
  - Types: heading, paragraph, list, code_block, table, blockquote, mermaid_diagram
  - Attributes: element_type, level (for headings), language (for code blocks), position in document

- **FolderBatch**: Represents a batch upload of a folder containing multiple markdown files
  - Attributes: batch_id, folder_path, total_files_discovered, files_processed, files_failed, upload_timestamp
  - Relationships: Associated with multiple Document records, one BatchJob for orchestration
  - Status tracking: discovering, processing, completed, partial_failure, failed

- **ImageReference**: Extracted image metadata from markdown files
  - Attributes: image_url, alt_text, is_local_path, is_base64, relative_path_to_md
  - Relationships: Associated with parent Document record
  - Future use: Marked for optional OCR processing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload and successfully parse markdown files containing up to 10,000 lines within 30 seconds
- **SC-002**: Markdown parser correctly extracts YAML frontmatter from 95% of test documents with standard frontmatter formats
- **SC-003**: System handles 100 concurrent markdown parsing jobs without degradation in performance
- **SC-004**: Parsing accuracy for markdown documents (text extraction completeness) is at least 98% compared to manual extraction
- **SC-005**: Empty or malformed markdown files result in graceful handling (no crashes) with appropriate error messages
- **SC-006**: Markdown files with mixed HTML content are processed successfully with HTML tags properly handled
- **SC-007**: 90% of users successfully upload and retrieve markdown document content on first attempt without errors
- **SC-008**: Folder uploads containing 100 markdown files across nested subdirectories are fully discovered and processed within 5 minutes
- **SC-009**: Recursive folder traversal handles directory structures up to 20 levels deep without errors or stack overflow
- **SC-010**: Mermaid diagrams are correctly identified and extracted in 95% of markdown files containing standard Mermaid syntax
- **SC-011**: Image references (URLs and local paths) are successfully extracted as metadata in 98% of markdown files
- **SC-012**: Chunked markdown content is available for RAG queries within 60 seconds after parsing completion
- **SC-013**: RAG query results from ingested markdown show at least 85% retrieval accuracy for relevant content chunks

### Assumptions

- Markdown files will use CommonMark or GitHub Flavored Markdown (GFM) syntax standards
- Most markdown files will be under 10 MB in size (consistent with existing document size limits)
- UTF-8 encoding is standard; other encodings will be attempted with fallback conversion
- Frontmatter, if present, will use YAML format (most common convention)
- HTML stripping is the default behavior for inline HTML tags (configurable if needed in future)
- Existing security scanning (malware detection) applies to markdown files same as other formats
- Chunking for RAG purposes treats markdown as continuous text after structure extraction
- Folder uploads will typically contain 10-500 markdown files (configurable batch size limits)
- Folder structures will not exceed 20 levels of nesting (reasonable for most documentation)
- Symbolic links in folders will be followed once but circular references will be detected and skipped
- Mermaid diagrams use standard syntax (graph, sequenceDiagram, classDiagram, etc.)
- Image processing (OCR from embedded images) is deferred to a future enhancement and is optional for initial release
- Images can be safely skipped during text extraction without impacting primary content quality
- RAG integration uses existing vector embeddings infrastructure (pgvector with 1536-dimensional embeddings)
- Chat and query operations will use standard retrieval-augmented generation patterns already established in the system