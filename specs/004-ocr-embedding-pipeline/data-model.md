# Data Model: OCR and Embedding Pipeline

**Feature**: 004-ocr-embedding-pipeline  
**Date**: 2026-01-11  
**Status**: Draft

## Overview

This document defines the data entities, relationships, and storage schema for the OCR and Embedding Pipeline feature. The model extends existing entities (Document, DocumentChunk, ProcessingJob) and adds new fields for OCR, embeddings, and vector search.

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
│  (Enhanced)      ├────────►│   (New)         │
└──────┬───────────┘         └─────────────────┘
       │
       │ 1:N
       │
┌──────▼───────────┐         ┌─────────────────┐
│  DocumentChunk   │ 1:1     │   Embedding     │
│  (Enhanced)      ├────────►│   (New)         │
└──────────────────┘         └─────────────────┘
       │
       │ N:1
       │
┌──────▼───────────┐
│  ProcessingJob   │
│  (Enhanced)      │
└──────────────────┘

┌─────────────────┐
│  SearchQuery    │
│    (New)        │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼────────┐
    │ SearchResult│
    │   (New)     │
    └─────────────┘

┌─────────────────┐
│  FolderBatch    │
│  (Existing)     │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼────────┐
    │  Document   │
    └─────────────┘
```

## Entity Definitions

### 1. Document (Enhanced)

**Purpose**: Represents an uploaded file with OCR and embedding processing metadata.

**Status**: Extends existing `src/storage_indexing/models/document.py`

**New/Enhanced Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ocr_status | Enum | NOT NULL, DEFAULT='not_started' | OCR processing status: not_started, in_progress, completed, failed |
| ocr_confidence | FLOAT | 0.0-1.0, NULL | Average OCR confidence score across all extracted text |
| embedding_status | Enum | NOT NULL, DEFAULT='not_started' | Embedding generation status: not_started, in_progress, completed, failed |
| language_detected | VARCHAR(10) | NULL | ISO 639-1 code (en, zh, etc.) |
| page_count | INTEGER | NULL | Total number of pages in document |
| has_scanned_content | BOOLEAN | DEFAULT=false | True if document contains image-based content requiring OCR |
| ocr_engine_used | VARCHAR(50) | NULL | OCR engine used: paddleocr, tesseract, none |

**Existing Fields** (unchanged):
- `document_id` (PK)
- `tenant_id` (FK to Tenant)
- `filename`, `file_type`, `file_size`
- `storage_path`, `content_hash`
- `processing_status` (overall status)
- `document_metadata` (JSON)
- `created_at`, `updated_at`

**Relationships**:
- `tenant`: Many-to-One with Tenant
- `chunks`: One-to-Many with DocumentChunk
- `extracted_texts`: One-to-Many with ExtractedText
- `processing_jobs`: One-to-Many with ProcessingJob
- `folder_batch`: Many-to-One with FolderBatch (optional)

**Indexes**:
- Primary: `document_id`
- Foreign: `tenant_id`, `folder_batch_id`
- Composite: `(tenant_id, ocr_status)`, `(tenant_id, embedding_status)`
- Unique: `(tenant_id, content_hash)` - for duplicate detection

**State Transitions**:
```text
Processing Status:
uploaded → parsing → parsed → failed
             ↓
           failed

OCR Status:
not_started → in_progress → completed
                ↓
              failed

Embedding Status:
not_started → in_progress → completed
                ↓
              failed
```

---

### 2. ExtractedText (New Entity)

**Purpose**: Stores raw text extracted from documents, preserving source information and confidence scores.

**Table**: `extracted_texts`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| extracted_text_id | BIGSERIAL | PRIMARY KEY | Unique identifier |
| document_id | INTEGER | FK to documents, NOT NULL | Source document |
| page_number | INTEGER | NOT NULL | Page number (1-indexed) |
| extraction_method | VARCHAR(20) | NOT NULL | Method used: native, ocr_paddleocr, ocr_tesseract |
| text_content | TEXT | NOT NULL | Extracted text content |
| confidence_score | FLOAT | 0.0-1.0, NULL | OCR confidence (NULL for native extraction) |
| bounding_boxes | JSONB | NULL | Bounding box coordinates for OCR text regions |
| structural_metadata | JSONB | NULL | Headings, paragraphs, tables, lists detected |
| character_count | INTEGER | NOT NULL | Number of characters in text_content |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Extraction timestamp |

**Relationships**:
- `document`: Many-to-One with Document

**Indexes**:
- Primary: `extracted_text_id`
- Foreign: `document_id`
- Composite: `(document_id, page_number)` - for page-wise retrieval
- Full-text: `text_content` (optional, for keyword fallback search)

**Validation Rules**:
- `page_number` must be >= 1
- `confidence_score` must be between 0.0 and 1.0
- `extraction_method` must be one of: native, ocr_paddleocr, ocr_tesseract
- `text_content` cannot be empty string

---

### 3. DocumentChunk (Enhanced)

**Purpose**: Represents a segment of document text for embedding generation.

**Status**: Extends existing `src/storage_indexing/models/document_chunk.py`

**New/Enhanced Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| chunk_text | TEXT | NOT NULL | Chunk content (500 tokens max) |
| token_count | INTEGER | NOT NULL | Exact token count using tiktoken |
| chunk_sequence | INTEGER | NOT NULL | Sequence number within document (0-indexed) |
| page_start | INTEGER | NULL | Starting page number |
| page_end | INTEGER | NULL | Ending page number |
| char_offset_start | INTEGER | NULL | Character offset in original text |
| char_offset_end | INTEGER | NULL | Character offset in original text |
| section_heading | VARCHAR(255) | NULL | Nearest section/heading for context |
| embedding_vector | VECTOR(768) | NULL | pgvector embedding (768-dim for multilingual-e5-base) |
| embedding_model | VARCHAR(100) | NULL | Model used: multilingual-e5-base, multilingual-e5-large |
| embedding_generated_at | TIMESTAMPTZ | NULL | When embedding was created |

**Existing Fields** (unchanged):
- `chunk_id` (PK)
- `document_id` (FK to Document)
- `created_at`

**Relationships**:
- `document`: Many-to-One with Document

**Indexes**:
- Primary: `chunk_id`
- Foreign: `document_id`
- Composite: `(document_id, chunk_sequence)` - for ordered retrieval
- Vector: HNSW index on `embedding_vector` for similarity search
  - `CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding_vector vector_cosine_ops)`

**Validation Rules**:
- `token_count` must be <= 500 (spec requirement)
- `chunk_sequence` must be >= 0 and unique per document
- `page_start` <= `page_end` if both present
- `char_offset_start` < `char_offset_end` if both present
- `embedding_vector` must have exactly 768 or 1024 dimensions (depending on model)

---

### 4. Embedding (Conceptual - Stored in DocumentChunk)

**Purpose**: Vector representation of document chunk for semantic search.

**Implementation**: Stored as `embedding_vector` field in `document_chunks` table (denormalized for query performance).

**Properties**:
- **Dimensionality**: 768 (multilingual-e5-base) or 1024 (multilingual-e5-large)
- **Distance Metric**: Cosine similarity (pgvector `<=>` operator)
- **Normalization**: L2 normalized by embedding model
- **Storage**: ~3KB per 768-dim vector

**Index Strategy**:
- HNSW (Hierarchical Navigable Small World) for approximate nearest neighbor search
- Parameters: `m=16, ef_construction=64` (balanced speed/accuracy)
- Build time: ~1 minute for 10k vectors
- Query time: ~10-50ms for top-k search

---

### 5. ProcessingJob (Enhanced)

**Purpose**: Tracks asynchronous processing tasks for documents.

**Status**: Extends existing `src/storage_indexing/models/processing_job.py`

**New/Enhanced Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| job_type | VARCHAR(50) | NOT NULL | Type: ocr_extraction, embedding_generation, batch_processing |
| job_status | Enum | NOT NULL | Status: pending, in_progress, completed, failed, retrying |
| priority | INTEGER | DEFAULT=5 | Priority 1-10 (1=highest) |
| retry_count | INTEGER | DEFAULT=0 | Number of retry attempts |
| max_retries | INTEGER | DEFAULT=3 | Maximum retry attempts allowed |
| error_category | VARCHAR(50) | NULL | Error type: transient, permanent, resource_exhaustion |
| error_message | TEXT | NULL | Detailed error description |
| progress_percentage | INTEGER | 0-100, NULL | For batch jobs, percentage complete |
| started_at | TIMESTAMPTZ | NULL | When job started processing |
| completed_at | TIMESTAMPTZ | NULL | When job finished |
| task_id | VARCHAR(255) | NULL | Dramatiq task ID for tracking |
| job_metadata | JSONB | NULL | Job-specific data (file list for batch, OCR params, etc.) |

**Existing Fields**:
- `job_id` (PK)
- `document_id` (FK to Document, nullable for batch jobs)
- `created_at`, `updated_at`

**Relationships**:
- `document`: Many-to-One with Document (nullable for batch jobs)
- `folder_batch`: Many-to-One with FolderBatch (for batch processing)

**Indexes**:
- Primary: `job_id`
- Foreign: `document_id`, `folder_batch_id`
- Composite: `(job_status, priority)` - for job queue ordering
- Index: `task_id` - for Dramatiq task lookup

**State Transitions**:
```text
pending → in_progress → completed
            ↓              ↑
          failed → retrying
            ↓
          (dead letter queue after max_retries)
```

---

### 6. SearchQuery (New Entity)

**Purpose**: Logs search queries for analytics and caching.

**Table**: `search_queries`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| query_id | BIGSERIAL | PRIMARY KEY | Unique identifier |
| tenant_id | INTEGER | FK to tenants, NOT NULL | User's tenant |
| user_id | INTEGER | FK to users, NULL | User who performed search |
| query_text | TEXT | NOT NULL | Original search query text |
| query_type | VARCHAR(20) | NOT NULL | Type: semantic_search, similar_documents |
| source_document_id | INTEGER | FK to documents, NULL | For "find similar" queries |
| filters_applied | JSONB | NULL | Metadata filters used (date, folder, etc.) |
| result_count | INTEGER | NULL | Number of results returned |
| search_duration_ms | INTEGER | NULL | Query execution time in milliseconds |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | When query was executed |

**Relationships**:
- `tenant`: Many-to-One with Tenant
- `user`: Many-to-One with User (nullable)
- `source_document`: Many-to-One with Document (for similarity search)
- `results`: One-to-Many with SearchResult

**Indexes**:
- Primary: `query_id`
- Foreign: `tenant_id`, `user_id`, `source_document_id`
- Composite: `(tenant_id, created_at)` - for analytics queries

**Use Cases**:
- Search analytics and trending queries
- Query performance monitoring
- Result caching (future enhancement)
- User behavior analysis

---

### 7. SearchResult (New Entity)

**Purpose**: Captures individual search results for analysis and caching.

**Table**: `search_results`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| result_id | BIGSERIAL | PRIMARY KEY | Unique identifier |
| query_id | BIGINT | FK to search_queries, NOT NULL | Associated search query |
| chunk_id | BIGINT | FK to document_chunks, NOT NULL | Matching chunk |
| document_id | INTEGER | FK to documents, NOT NULL | Matching document |
| similarity_score | FLOAT | 0.0-1.0, NOT NULL | Cosine similarity score |
| rank_position | INTEGER | NOT NULL | Result position (1-based) |
| result_snippet | TEXT | NULL | Text snippet for preview |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | When result was captured |

**Relationships**:
- `query`: Many-to-One with SearchQuery
- `chunk`: Many-to-One with DocumentChunk
- `document`: Many-to-One with Document

**Indexes**:
- Primary: `result_id`
- Foreign: `query_id`, `chunk_id`, `document_id`
- Composite: `(query_id, rank_position)` - for ordered retrieval

**Validation Rules**:
- `similarity_score` must be between 0.0 and 1.0
- `rank_position` must be >= 1

---

### 8. FolderBatch (Existing - No Changes)

**Purpose**: Represents batch upload operations with folder structure.

**Status**: No changes needed for this feature.

**Usage**: Documents in a batch are linked via `folder_batch_id` foreign key.

---

## Database Migrations

### Migration 1: Add OCR and Embedding Fields to Documents

```sql
-- Add new columns to documents table
ALTER TABLE documents 
ADD COLUMN ocr_status VARCHAR(20) NOT NULL DEFAULT 'not_started',
ADD COLUMN ocr_confidence FLOAT CHECK (ocr_confidence >= 0 AND ocr_confidence <= 1),
ADD COLUMN embedding_status VARCHAR(20) NOT NULL DEFAULT 'not_started',
ADD COLUMN language_detected VARCHAR(10),
ADD COLUMN page_count INTEGER,
ADD COLUMN has_scanned_content BOOLEAN DEFAULT FALSE,
ADD COLUMN ocr_engine_used VARCHAR(50);

-- Add indexes for new columns
CREATE INDEX idx_documents_ocr_status ON documents(tenant_id, ocr_status);
CREATE INDEX idx_documents_embedding_status ON documents(tenant_id, embedding_status);

-- Add check constraints
ALTER TABLE documents 
ADD CONSTRAINT chk_ocr_status CHECK (ocr_status IN ('not_started', 'in_progress', 'completed', 'failed')),
ADD CONSTRAINT chk_embedding_status CHECK (embedding_status IN ('not_started', 'in_progress', 'completed', 'failed'));
```

### Migration 2: Create ExtractedTexts Table

```sql
-- Create extracted_texts table
CREATE TABLE extracted_texts (
    extracted_text_id BIGSERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL CHECK (page_number >= 1),
    extraction_method VARCHAR(20) NOT NULL CHECK (extraction_method IN ('native', 'ocr_paddleocr', 'ocr_tesseract')),
    text_content TEXT NOT NULL CHECK (text_content != ''),
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    bounding_boxes JSONB,
    structural_metadata JSONB,
    character_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_extracted_texts_document ON extracted_texts(document_id);
CREATE INDEX idx_extracted_texts_page ON extracted_texts(document_id, page_number);

-- Optional: Full-text search index for fallback keyword search
CREATE INDEX idx_extracted_texts_fts ON extracted_texts USING gin(to_tsvector('english', text_content));
```

### Migration 3: Enhance DocumentChunks Table

```sql
-- Add new columns to document_chunks table
ALTER TABLE document_chunks
ADD COLUMN chunk_text TEXT NOT NULL,
ADD COLUMN token_count INTEGER NOT NULL CHECK (token_count <= 500),
ADD COLUMN chunk_sequence INTEGER NOT NULL,
ADD COLUMN page_start INTEGER,
ADD COLUMN page_end INTEGER CHECK (page_end IS NULL OR page_end >= page_start),
ADD COLUMN char_offset_start INTEGER,
ADD COLUMN char_offset_end INTEGER CHECK (char_offset_end IS NULL OR char_offset_end > char_offset_start),
ADD COLUMN section_heading VARCHAR(255),
ADD COLUMN embedding_vector vector(768),  -- pgvector extension
ADD COLUMN embedding_model VARCHAR(100),
ADD COLUMN embedding_generated_at TIMESTAMPTZ;

-- Add indexes
CREATE INDEX idx_chunks_sequence ON document_chunks(document_id, chunk_sequence);
CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks 
    USING hnsw (embedding_vector vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);

-- Add unique constraint
ALTER TABLE document_chunks
ADD CONSTRAINT uq_chunk_sequence_per_doc UNIQUE (document_id, chunk_sequence);
```

### Migration 4: Enhance ProcessingJobs Table

```sql
-- Add new columns to processing_jobs table
ALTER TABLE processing_jobs
ADD COLUMN job_type VARCHAR(50) NOT NULL,
ADD COLUMN job_status VARCHAR(20) NOT NULL DEFAULT 'pending',
ADD COLUMN priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
ADD COLUMN retry_count INTEGER DEFAULT 0,
ADD COLUMN max_retries INTEGER DEFAULT 3,
ADD COLUMN error_category VARCHAR(50),
ADD COLUMN error_message TEXT,
ADD COLUMN progress_percentage INTEGER CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
ADD COLUMN started_at TIMESTAMPTZ,
ADD COLUMN completed_at TIMESTAMPTZ,
ADD COLUMN task_id VARCHAR(255),
ADD COLUMN job_metadata JSONB;

-- Add indexes
CREATE INDEX idx_jobs_status_priority ON processing_jobs(job_status, priority);
CREATE INDEX idx_jobs_task_id ON processing_jobs(task_id);

-- Add check constraints
ALTER TABLE processing_jobs
ADD CONSTRAINT chk_job_type CHECK (job_type IN ('ocr_extraction', 'embedding_generation', 'batch_processing')),
ADD CONSTRAINT chk_job_status CHECK (job_status IN ('pending', 'in_progress', 'completed', 'failed', 'retrying'));
```

### Migration 5: Create SearchQueries and SearchResults Tables

```sql
-- Create search_queries table
CREATE TABLE search_queries (
    query_id BIGSERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    query_type VARCHAR(20) NOT NULL CHECK (query_type IN ('semantic_search', 'similar_documents')),
    source_document_id INTEGER REFERENCES documents(document_id) ON DELETE SET NULL,
    filters_applied JSONB,
    result_count INTEGER,
    search_duration_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create search_results table
CREATE TABLE search_results (
    result_id BIGSERIAL PRIMARY KEY,
    query_id BIGINT NOT NULL REFERENCES search_queries(query_id) ON DELETE CASCADE,
    chunk_id BIGINT NOT NULL REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    rank_position INTEGER NOT NULL CHECK (rank_position >= 1),
    result_snippet TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_search_queries_tenant ON search_queries(tenant_id, created_at);
CREATE INDEX idx_search_queries_type ON search_queries(query_type);
CREATE INDEX idx_search_results_query ON search_results(query_id, rank_position);
CREATE INDEX idx_search_results_chunk ON search_results(chunk_id);
```

---

## Data Lifecycle

### Document Processing Flow

```text
1. Upload → Document created (processing_status=uploaded)
2. Validation → Malware scan, format check
3. Parsing → Extract native text (processing_status=parsing)
4. OCR → Extract text from images (ocr_status=in_progress)
5. Store ExtractedText records (ocr_status=completed)
6. Chunking → Create DocumentChunk records
7. Embedding → Generate vectors (embedding_status=in_progress)
8. Index → Update embedding_vector in chunks (embedding_status=completed)
9. Complete → Document ready for search (processing_status=parsed)
```

### Search Flow

```text
1. User submits query → Create SearchQuery record
2. Generate query embedding (same model as documents)
3. Vector search: SELECT * FROM document_chunks ORDER BY embedding_vector <=> query_vector LIMIT 10
4. Apply metadata filters (tenant_id, folder, date range)
5. Retrieve parent documents and snippets
6. Create SearchResult records for analytics
7. Return results with scores and metadata
```

### Batch Processing Flow

```text
1. User uploads folder → Create FolderBatch record
2. Create Document records for each file
3. Create ProcessingJob (job_type=batch_processing)
4. Spawn individual OCR/embedding jobs for each document
5. Track progress in ProcessingJob.progress_percentage
6. Mark batch complete when all documents processed
```

---

## Storage Estimates

### Per Document (20-page typical document)

| Component | Size | Notes |
|-----------|------|-------|
| Original file | ~1 MB | PDF/DOCX |
| ExtractedText | ~100 KB | 20 pages × 5KB text per page |
| DocumentChunks (text) | ~120 KB | ~40 chunks × 3KB per chunk |
| Embeddings | ~120 KB | 40 chunks × 3KB per vector |
| Metadata | ~5 KB | JSON fields, relationships |
| **Total per document** | **~1.35 MB** | With embeddings |

### Collection Scale (10,000 documents)

| Component | Size | Notes |
|-----------|------|-------|
| Documents table | ~10 MB | Metadata only |
| Original files | ~10 GB | Storage layer (S3/filesystem) |
| ExtractedTexts | ~1 GB | Extracted text content |
| DocumentChunks | ~1.2 GB | Text + metadata |
| Embeddings | ~1.2 GB | Vector data |
| Indexes | ~500 MB | HNSW + B-tree indexes |
| **Total database** | **~4 GB** | PostgreSQL |
| **Total storage** | **~14 GB** | Database + files |

---

## Performance Considerations

### Query Optimization

1. **Tenant Isolation**: Always filter by `tenant_id` first (row-level security)
2. **Vector Search**: Use HNSW index for sub-linear search time
3. **Metadata Filtering**: Apply filters before vector search when possible
4. **Result Caching**: Cache popular queries in Redis (future enhancement)
5. **Pagination**: Use cursor-based pagination for large result sets

### Write Optimization

1. **Batch Inserts**: Insert chunks in batches of 100-500 for efficiency
2. **Deferred Indexing**: Build HNSW index after bulk uploads, not incrementally
3. **Connection Pooling**: Use SQLAlchemy async pool (already configured)
4. **Transaction Batching**: Commit in batches during bulk operations

### Storage Optimization

1. **Compression**: Enable PostgreSQL TOAST compression for TEXT fields
2. **Archival**: Move old ExtractedText to cold storage after 90 days (future)
3. **Vacuum**: Regular VACUUM ANALYZE on high-churn tables
4. **Partitioning**: Consider partitioning by tenant_id for large multi-tenant deployments (future)

---

## Data Validation Rules Summary

### Document
- `ocr_confidence` ∈ [0.0, 1.0]
- `ocr_status` ∈ {not_started, in_progress, completed, failed}
- `embedding_status` ∈ {not_started, in_progress, completed, failed}
- `page_count` >= 1 (if set)

### ExtractedText
- `page_number` >= 1
- `confidence_score` ∈ [0.0, 1.0]
- `extraction_method` ∈ {native, ocr_paddleocr, ocr_tesseract}
- `text_content` != '' (not empty)
- `character_count` > 0

### DocumentChunk
- `token_count` <= 500
- `chunk_sequence` >= 0, unique per document
- `page_start` <= `page_end` (if both set)
- `char_offset_start` < `char_offset_end` (if both set)
- `embedding_vector` dimension ∈ {768, 1024}

### ProcessingJob
- `priority` ∈ [1, 10]
- `retry_count` <= `max_retries`
- `progress_percentage` ∈ [0, 100]
- `job_type` ∈ {ocr_extraction, embedding_generation, batch_processing}
- `job_status` ∈ {pending, in_progress, completed, failed, retrying}

### SearchResult
- `similarity_score` ∈ [0.0, 1.0]
- `rank_position` >= 1

---

## Rollback Strategy

If migrations need to be rolled back:

1. **Migration 5**: Drop search_queries and search_results tables (safe, no data dependencies)
2. **Migration 4**: Remove added columns from processing_jobs (preserve existing data)
3. **Migration 3**: Remove added columns from document_chunks (WARNING: loses embeddings)
4. **Migration 2**: Drop extracted_texts table (WARNING: loses OCR data)
5. **Migration 1**: Remove added columns from documents (safe, no critical data)

**Critical**: Always backup database before migrations. Embeddings can be regenerated but is time-consuming.

---

## Future Enhancements

1. **Multimodal Embeddings**: Store image embeddings for visual similarity search
2. **Metadata Embeddings**: Generate separate embeddings for titles, summaries
3. **Hierarchical Chunking**: Parent-child chunk relationships for context
4. **Hybrid Search**: Combine BM25 keyword search with vector search
5. **Query Expansion**: Use LLM to expand user queries before search
6. **Result Caching**: Cache search results in Redis for popular queries
7. **Feedback Loop**: Store user feedback on search results for relevance tuning

---

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [SQLAlchemy 2.0 Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL HNSW Index](https://github.com/pgvector/pgvector#hnsw)
- [Vector Storage Best Practices](https://www.timescale.com/blog/vector-database-basics/)
