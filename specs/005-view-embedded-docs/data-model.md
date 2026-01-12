# Data Model: View Ingested and Embedded Documents

**Feature**: 005-view-embedded-docs  
**Date**: 2026-01-11  
**Status**: Draft

## Overview

This document defines the data entities, relationships, and queries required for the document viewing feature. This feature is **read-only** and does not introduce new database tables or schemas. It leverages existing entities from the ingestion and embedding pipeline to provide users with visibility into their document library.

## Entity Relationship Diagram

```text
┌──────────────┐
│   Tenant     │
└──────┬───────┘
       │
       │ 1:N
       │
┌──────▼───────────┐         ┌─────────────────┐
│    Document      │ 1:N     │ ExtractedText   │
│                  ├────────►│                 │
└──────┬───────────┘         └─────────────────┘
       │
       │ 1:N
       │
┌──────▼───────────┐         ┌─────────────────┐
│  DocumentChunk   │ 1:1     │   Embedding     │
│                  ├────────►│   (vector)      │
└──────────────────┘         └─────────────────┘
       │
       │ N:1
       │
┌──────▼───────────┐
│  ProcessingJob   │
│                  │
└──────────────────┘

┌─────────────────┐
│  FolderBatch    │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼────────┐
    │  Document   │
    └─────────────┘
```

## Entity Definitions

### 1. Document (Read Access)

**Purpose**: Primary entity representing uploaded files with processing and embedding metadata.

**Table**: `documents`

**Key Fields Used**:

| Field | Type | Description |
|-------|------|-------------|
| document_id | INTEGER | PRIMARY KEY - Unique identifier |
| tenant_id | INTEGER | FK to tenants - For multi-tenant isolation |
| filename | VARCHAR(255) | Original filename for display |
| file_type | VARCHAR(50) | File extension (pdf, docx, txt, md) |
| file_size | BIGINT | File size in bytes |
| storage_path | TEXT | Path to stored file |
| content_hash | VARCHAR(64) | SHA-256 hash for deduplication |
| processing_status | VARCHAR(20) | Overall status: uploaded, parsing, parsed, failed |
| ocr_status | VARCHAR(20) | OCR status: not_started, in_progress, completed, failed |
| ocr_confidence | FLOAT | Average OCR confidence score (0.0-1.0) |
| embedding_status | VARCHAR(20) | Embedding status: not_started, in_progress, completed, failed |
| language_detected | VARCHAR(10) | ISO 639-1 language code |
| page_count | INTEGER | Total pages in document |
| has_scanned_content | BOOLEAN | Whether document required OCR |
| ocr_engine_used | VARCHAR(50) | OCR engine: paddleocr, tesseract, none |
| document_metadata | JSONB | Additional metadata (author, title, etc.) |
| created_at | TIMESTAMPTZ | Upload timestamp |
| updated_at | TIMESTAMPTZ | Last modification timestamp |

**Relationships**:
- `tenant`: Many-to-One with Tenant
- `chunks`: One-to-Many with DocumentChunk
- `extracted_texts`: One-to-Many with ExtractedText
- `processing_jobs`: One-to-Many with ProcessingJob
- `folder_batch`: Many-to-One with FolderBatch (optional)

**Indexes Used**:
- Primary: `document_id`
- Foreign: `tenant_id`
- Composite: `(tenant_id, ocr_status)` - For filtering by OCR status
- Composite: `(tenant_id, embedding_status)` - For filtering by embedding status
- Index: `created_at` - For date range filtering
- Index: `file_type` - For file type filtering

---

### 2. DocumentChunk (Read Access)

**Purpose**: Represents text segments with embeddings for semantic search.

**Table**: `document_chunks`

**Key Fields Used**:

| Field | Type | Description |
|-------|------|-------------|
| chunk_id | BIGSERIAL | PRIMARY KEY - Unique identifier |
| document_id | INTEGER | FK to documents |
| chunk_text | TEXT | Actual text content of chunk |
| token_count | INTEGER | Number of tokens in chunk |
| chunk_sequence | INTEGER | Sequence number within document (0-indexed) |
| page_start | INTEGER | Starting page number |
| page_end | INTEGER | Ending page number |
| section_heading | VARCHAR(255) | Nearest section heading for context |
| embedding_vector | VECTOR(768) | pgvector embedding |
| embedding_model | VARCHAR(100) | Model used for embedding |
| embedding_generated_at | TIMESTAMPTZ | When embedding was created |
| created_at | TIMESTAMPTZ | Chunk creation timestamp |

**Relationships**:
- `document`: Many-to-One with Document

**Indexes Used**:
- Primary: `chunk_id`
- Foreign: `document_id`
- Composite: `(document_id, chunk_sequence)` - For ordered chunk retrieval

---

### 3. ExtractedText (Read Access)

**Purpose**: Stores raw text extracted from documents with confidence scores.

**Table**: `extracted_texts`

**Key Fields Used**:

| Field | Type | Description |
|-------|------|-------------|
| extracted_text_id | BIGSERIAL | PRIMARY KEY - Unique identifier |
| document_id | INTEGER | FK to documents |
| page_number | INTEGER | Page number (1-indexed) |
| extraction_method | VARCHAR(20) | native, ocr_paddleocr, ocr_tesseract |
| text_content | TEXT | Extracted text content |
| confidence_score | FLOAT | OCR confidence (NULL for native) |
| character_count | INTEGER | Number of characters |
| created_at | TIMESTAMPTZ | Extraction timestamp |

**Relationships**:
- `document`: Many-to-One with Document

**Indexes Used**:
- Primary: `extracted_text_id`
- Foreign: `document_id`
- Composite: `(document_id, page_number)` - For page-wise text retrieval

---

### 4. ProcessingJob (Read Access)

**Purpose**: Tracks asynchronous processing tasks and their status.

**Table**: `processing_jobs`

**Key Fields Used**:

| Field | Type | Description |
|-------|------|-------------|
| job_id | BIGSERIAL | PRIMARY KEY - Unique identifier |
| document_id | INTEGER | FK to documents (nullable for batch jobs) |
| job_type | VARCHAR(50) | ocr_extraction, embedding_generation, batch_processing |
| job_status | VARCHAR(20) | pending, in_progress, completed, failed, retrying |
| error_category | VARCHAR(50) | transient, permanent, resource_exhaustion |
| error_message | TEXT | Detailed error description |
| progress_percentage | INTEGER | Progress (0-100) |
| started_at | TIMESTAMPTZ | Job start time |
| completed_at | TIMESTAMPTZ | Job completion time |
| created_at | TIMESTAMPTZ | Job creation time |

**Relationships**:
- `document`: Many-to-One with Document

**Indexes Used**:
- Primary: `job_id`
- Foreign: `document_id`

---

### 5. FolderBatch (Read Access)

**Purpose**: Groups documents uploaded together in a batch operation.

**Table**: `folder_batches`

**Key Fields Used**:

| Field | Type | Description |
|-------|------|-------------|
| batch_id | INTEGER | PRIMARY KEY - Unique identifier |
| tenant_id | INTEGER | FK to tenants |
| batch_name | VARCHAR(255) | User-provided batch name |
| total_files | INTEGER | Number of files in batch |
| processed_files | INTEGER | Number of processed files |
| created_at | TIMESTAMPTZ | Batch creation time |

**Relationships**:
- `documents`: One-to-Many with Document

**Indexes Used**:
- Primary: `batch_id`
- Foreign: `tenant_id`

---

## Query Patterns

### 1. List All Documents with Metadata

**Purpose**: Retrieve paginated list of documents for main library view.

**Query**:
```sql
SELECT 
    d.document_id,
    d.filename,
    d.file_type,
    d.file_size,
    d.processing_status,
    d.ocr_status,
    d.embedding_status,
    d.page_count,
    d.created_at,
    COUNT(DISTINCT dc.chunk_id) as chunk_count,
    COUNT(DISTINCT et.extracted_text_id) as extracted_text_pages
FROM documents d
LEFT JOIN document_chunks dc ON d.document_id = dc.document_id
LEFT JOIN extracted_texts et ON d.document_id = et.document_id
WHERE d.tenant_id = :tenant_id
GROUP BY d.document_id
ORDER BY d.created_at DESC
LIMIT :page_size OFFSET :offset;
```

**Performance**: O(n log n) with proper indexes on `tenant_id` and `created_at`

---

### 2. Get Document Details

**Purpose**: Retrieve detailed information for a single document.

**Query**:
```sql
SELECT 
    d.*,
    fb.batch_name,
    COUNT(DISTINCT dc.chunk_id) as total_chunks,
    COUNT(DISTINCT et.extracted_text_id) as total_extracted_pages,
    AVG(et.confidence_score) as avg_ocr_confidence,
    MIN(dc.embedding_generated_at) as first_embedding_time,
    MAX(dc.embedding_generated_at) as last_embedding_time
FROM documents d
LEFT JOIN folder_batches fb ON d.folder_batch_id = fb.batch_id
LEFT JOIN document_chunks dc ON d.document_id = dc.document_id
LEFT JOIN extracted_texts et ON d.document_id = et.document_id
WHERE d.document_id = :document_id 
    AND d.tenant_id = :tenant_id
GROUP BY d.document_id, fb.batch_name;
```

**Performance**: O(1) lookup by primary key with joins

---

### 3. Get Embedding Details for Document

**Purpose**: Retrieve embedding statistics and chunk information.

**Query**:
```sql
SELECT 
    dc.chunk_id,
    dc.chunk_sequence,
    dc.token_count,
    dc.page_start,
    dc.page_end,
    dc.section_heading,
    dc.embedding_model,
    dc.embedding_generated_at,
    LENGTH(dc.chunk_text) as character_count
FROM document_chunks dc
WHERE dc.document_id = :document_id
ORDER BY dc.chunk_sequence ASC;
```

**Performance**: O(n) where n = number of chunks, typically 20-100 per document

---

### 4. Get Extracted Text Preview

**Purpose**: Retrieve first N characters of extracted text for preview.

**Query**:
```sql
SELECT 
    et.page_number,
    et.extraction_method,
    et.confidence_score,
    LEFT(et.text_content, 1000) as text_preview
FROM extracted_texts et
WHERE et.document_id = :document_id
ORDER BY et.page_number ASC
LIMIT 5;
```

**Performance**: O(1) with limit on pages and character truncation

---

### 5. Filter Documents by Status

**Purpose**: Filter documents by processing, OCR, or embedding status.

**Query**:
```sql
SELECT 
    d.document_id,
    d.filename,
    d.file_type,
    d.processing_status,
    d.ocr_status,
    d.embedding_status,
    d.created_at
FROM documents d
WHERE d.tenant_id = :tenant_id
    AND (:filter_processing_status IS NULL OR d.processing_status = :filter_processing_status)
    AND (:filter_ocr_status IS NULL OR d.ocr_status = :filter_ocr_status)
    AND (:filter_embedding_status IS NULL OR d.embedding_status = :filter_embedding_status)
ORDER BY d.created_at DESC
LIMIT :page_size OFFSET :offset;
```

**Performance**: O(log n) with composite indexes on status fields

---

### 6. Filter Documents by File Type

**Purpose**: Filter documents by file extension.

**Query**:
```sql
SELECT 
    d.document_id,
    d.filename,
    d.file_type,
    d.file_size,
    d.created_at
FROM documents d
WHERE d.tenant_id = :tenant_id
    AND d.file_type = :file_type
ORDER BY d.created_at DESC
LIMIT :page_size OFFSET :offset;
```

**Performance**: O(log n) with index on `file_type`

---

### 7. Filter Documents by Date Range

**Purpose**: Filter documents by upload date range.

**Query**:
```sql
SELECT 
    d.document_id,
    d.filename,
    d.file_type,
    d.created_at
FROM documents d
WHERE d.tenant_id = :tenant_id
    AND d.created_at >= :start_date
    AND d.created_at <= :end_date
ORDER BY d.created_at DESC
LIMIT :page_size OFFSET :offset;
```

**Performance**: O(log n) with index on `created_at`

---

### 8. Search Documents by Filename

**Purpose**: Filter documents by filename substring match.

**Query**:
```sql
SELECT 
    d.document_id,
    d.filename,
    d.file_type,
    d.created_at
FROM documents d
WHERE d.tenant_id = :tenant_id
    AND d.filename ILIKE :search_pattern
ORDER BY d.created_at DESC
LIMIT :page_size OFFSET :offset;
```

**Performance**: O(n) full table scan unless trigram index added (optional enhancement)

**Enhancement**: Add GIN trigram index for better performance:
```sql
CREATE INDEX idx_documents_filename_trgm ON documents USING gin (filename gin_trgm_ops);
```

---

### 9. Get Processing Errors for Document

**Purpose**: Retrieve error messages from failed processing jobs.

**Query**:
```sql
SELECT 
    pj.job_id,
    pj.job_type,
    pj.job_status,
    pj.error_category,
    pj.error_message,
    pj.retry_count,
    pj.started_at,
    pj.completed_at
FROM processing_jobs pj
WHERE pj.document_id = :document_id
    AND pj.job_status IN ('failed', 'retrying')
ORDER BY pj.started_at DESC;
```

**Performance**: O(log n) with index on `document_id`

---

### 10. Get In-Progress Document Status

**Purpose**: Retrieve current processing status and progress for in-progress documents.

**Query**:
```sql
SELECT 
    pj.job_id,
    pj.job_type,
    pj.job_status,
    pj.progress_percentage,
    pj.started_at
FROM processing_jobs pj
WHERE pj.document_id = :document_id
    AND pj.job_status = 'in_progress'
ORDER BY pj.started_at DESC
LIMIT 1;
```

**Performance**: O(log n) with index on `document_id`

---

## API Response Models

### DocumentListItem

```json
{
  "document_id": 123,
  "filename": "technical_report.pdf",
  "file_type": "pdf",
  "file_size": 2048576,
  "processing_status": "parsed",
  "ocr_status": "completed",
  "embedding_status": "completed",
  "page_count": 25,
  "chunk_count": 42,
  "created_at": "2026-01-11T10:30:00Z",
  "updated_at": "2026-01-11T10:35:00Z"
}
```

### DocumentDetails

```json
{
  "document_id": 123,
  "filename": "technical_report.pdf",
  "file_type": "pdf",
  "file_size": 2048576,
  "storage_path": "/uploads/1/abc123/technical_report.pdf",
  "content_hash": "sha256_hash_here",
  "processing_status": "parsed",
  "ocr_status": "completed",
  "ocr_confidence": 0.95,
  "embedding_status": "completed",
  "language_detected": "en",
  "page_count": 25,
  "has_scanned_content": true,
  "ocr_engine_used": "paddleocr",
  "document_metadata": {
    "author": "John Doe",
    "title": "Technical Report 2026"
  },
  "batch_name": "Q1 Reports",
  "total_chunks": 42,
  "total_extracted_pages": 25,
  "avg_ocr_confidence": 0.95,
  "first_embedding_time": "2026-01-11T10:32:00Z",
  "last_embedding_time": "2026-01-11T10:35:00Z",
  "created_at": "2026-01-11T10:30:00Z",
  "updated_at": "2026-01-11T10:35:00Z"
}
```

### EmbeddingDetails

```json
{
  "embedding_model": "multilingual-e5-base",
  "vector_dimensions": 768,
  "total_chunks": 42,
  "average_chunk_size": 485,
  "chunks": [
    {
      "chunk_id": 1001,
      "chunk_sequence": 0,
      "token_count": 482,
      "character_count": 2145,
      "page_start": 1,
      "page_end": 2,
      "section_heading": "Introduction",
      "embedding_generated_at": "2026-01-11T10:32:15Z"
    }
  ]
}
```

### TextPreview

```json
{
  "pages": [
    {
      "page_number": 1,
      "extraction_method": "ocr_paddleocr",
      "confidence_score": 0.97,
      "text_preview": "This is the first page of the document..."
    },
    {
      "page_number": 2,
      "extraction_method": "ocr_paddleocr",
      "confidence_score": 0.94,
      "text_preview": "Continuing from the previous page..."
    }
  ]
}
```

### ProcessingError

```json
{
  "job_id": 5678,
  "job_type": "embedding_generation",
  "job_status": "failed",
  "error_category": "transient",
  "error_message": "Embedding service temporarily unavailable. Will retry automatically.",
  "retry_count": 2,
  "started_at": "2026-01-11T10:32:00Z",
  "completed_at": "2026-01-11T10:32:30Z"
}
```

---

## Performance Considerations

### Query Optimization

1. **Tenant Isolation**: Always filter by `tenant_id` first to leverage row-level security and reduce dataset
2. **Pagination**: Use LIMIT/OFFSET for initial implementation; consider cursor-based pagination for large datasets
3. **Aggregation Caching**: Cache document counts and statistics in Redis for frequently accessed metrics
4. **Join Optimization**: Use LEFT JOIN only when needed; prefer separate queries for detail views
5. **Index Coverage**: Ensure all WHERE and ORDER BY columns are indexed

### Read Performance

| Query Type | Expected Performance | Notes |
|------------|---------------------|-------|
| Document list (paginated) | < 100ms | With 10,000 documents |
| Document details | < 50ms | Single document lookup |
| Embedding details | < 200ms | 50-100 chunks per document |
| Text preview | < 50ms | Limited to 5 pages |
| Status filtering | < 150ms | With composite indexes |
| Filename search | < 300ms | Without trigram index |
| Filename search (optimized) | < 100ms | With trigram index |

### Caching Strategy

1. **Document Lists**: Cache for 30 seconds (documents rarely change after processing)
2. **Document Details**: Cache for 60 seconds (static once processing complete)
3. **Embedding Details**: Cache for 300 seconds (immutable after generation)
4. **Processing Status**: NO caching (must show real-time updates)
5. **Error Messages**: Cache for 60 seconds (unlikely to change)

### Database Connection Management

- **Read-only Connections**: Use connection pooling with max 20 connections
- **Query Timeout**: Set 30-second timeout for all read queries
- **Retry Strategy**: Retry transient errors up to 3 times with exponential backoff

---

## Data Validation Rules

### Filter Validation

- `file_type`: Must be one of the supported types (pdf, docx, txt, md, etc.)
- `processing_status`: Must be one of: uploaded, parsing, parsed, failed
- `ocr_status`: Must be one of: not_started, in_progress, completed, failed
- `embedding_status`: Must be one of: not_started, in_progress, completed, failed
- `date_range`: start_date must be <= end_date
- `page_size`: Must be between 1 and 100
- `offset`: Must be >= 0

### Security Validation

- All queries MUST include `tenant_id` filter for multi-tenant isolation
- Document access requires tenant ownership verification
- No raw SQL injection - use parameterized queries only

---

## Migration Requirements

**Status**: No new migrations required.

This feature uses existing database schema from:
- `001_initial_schema` - Base document tables
- `004_ocr_embedding_pipeline` - OCR and embedding fields

**Optional Index Enhancement**:

If filename search performance is poor (>300ms), add trigram index:

```sql
-- Add pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Add trigram index for filename search
CREATE INDEX idx_documents_filename_trgm 
ON documents USING gin (filename gin_trgm_ops);
```

---

## Assumptions

1. **Database Schema Exists**: All referenced tables and columns are already created by previous migrations
2. **Read-Only Access**: This feature only reads data, no writes or updates to database
3. **Multi-tenant Isolation**: All queries respect tenant boundaries via `tenant_id` filtering
4. **Processing Pipeline Active**: Background jobs keep document status fields up-to-date
5. **Pagination Required**: Document libraries can grow to 10,000+ documents requiring pagination
6. **Real-time Status**: Users expect processing status to update within 5 seconds of actual state change

---

## References

- Feature 004: OCR and Embedding Pipeline (provides data model foundation)
- PostgreSQL Documentation: [Indexes](https://www.postgresql.org/docs/current/indexes.html)
- SQLAlchemy: [Query Optimization](https://docs.sqlalchemy.org/en/20/faq/performance.html)
