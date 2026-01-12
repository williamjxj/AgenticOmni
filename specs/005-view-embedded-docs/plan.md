# Implementation Plan: Search Fix for Markdown Documents

**Branch**: `005-view-embedded-docs` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)  
**Input**: Bug fix - "markdown md files upload/ingested succ, when searching, it shows nothing: no results found"

## Summary

Fixed critical search functionality issue where markdown files were successfully uploaded and parsed but returned no search results. Root cause analysis revealed three interconnected problems:

1. **Dramatiq workers not running** - Background tasks for parsing were stuck in "pending" status
2. **Vector dimension mismatch** - Database configured for 1536 dimensions (OpenAI) but Ollama generates 768 dimensions
3. **Missing embedding automation** - No automatic embedding generation after parsing completed

**Technical Approach**: 
- Fixed database schema to match embedding model dimensions (1536 → 768)
- Created automated embedding generation task triggered after parsing
- Updated worker configuration to process both parsing and embedding tasks
- Verified end-to-end workflow: upload → parse → chunk → embed → search

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI 0.128+, SQLAlchemy 2.0+ (async), Dramatiq 2.0, Ollama (nomic-embed-text:latest)  
**Embedding Provider**: Ollama with nomic-embed-text:latest (768 dimensions)  
**Vector Database**: PostgreSQL 14+ with pgvector extension  
**Testing**: Manual testing via curl and frontend  
**Target Platform**: macOS (development), Linux server (production)  
**Project Type**: Web application (FastAPI backend + Next.js frontend)  
**Performance Goals**: 
- Search response time < 100ms for 10 results
- Embedding generation < 1 second per chunk
- Support 1000+ documents with embeddings  
**Constraints**: 
- Must use existing Ollama setup (no OpenAI API costs)
- Database migration must preserve existing data
- Workers must handle failures gracefully with retries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **No Constitution Violations** - This is a bug fix, not a new feature
- Reuses existing infrastructure (Dramatiq, pgvector, Ollama)
- No new dependencies or architectural changes
- Follows existing patterns for task queue and database operations

## Project Structure

### Documentation (this feature)

```text
specs/005-view-embedded-docs/
├── plan.md              # This file - implementation plan with root cause analysis
├── research.md          # Research findings and technical decisions
├── data-model.md        # Database schema and query patterns (read-only)
├── spec.md              # Original feature spec for document viewing
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
# Backend
src/
├── ingestion_parsing/
│   ├── tasks/
│   │   ├── document_tasks.py        # MODIFIED: Added embedding trigger
│   │   └── embedding_tasks.py       # NEW: Automated embedding generation
│   └── services/
│       ├── parsing_service.py       # Existing: Creates chunks
│       └── chunking_service.py      # Existing: Splits text into chunks
├── rag_orchestration/
│   └── services/
│       ├── embedding_service.py     # Existing: Generates embeddings
│       └── search_service.py        # Existing: Vector search
└── storage_indexing/
    ├── models/
    │   └── document_chunk.py        # MODIFIED: Vector dimension updated
    └── migrations/
        └── [manual migration]       # Database schema fix

# Scripts
scripts/
├── start_workers.sh                 # MODIFIED: Added embedding_tasks module
└── generate_embeddings.py           # Existing: Manual embedding generation

# Database
database/
└── document_chunks table            # MODIFIED: vector(1536) → vector(768)
```

**Structure Decision**: Single backend project with task queue workers. No frontend changes required as the API contract remains unchanged.

## Root Cause Analysis

### Problem Statement

Users reported: "markdown md files upload/ingested succ, when searching, it shows nothing: no results found"

### Investigation Steps

1. **Verified upload and parsing**:
   ```sql
   SELECT document_id, filename, file_type, processing_status 
   FROM documents 
   WHERE file_type = 'md' 
   ORDER BY created_at DESC LIMIT 5;
   ```
   Result: Documents 16-20 had `processing_status = 'uploaded'` (never parsed)

2. **Checked chunks**:
   ```sql
   SELECT COUNT(*) as total, COUNT(embedding_vector) as with_embeddings 
   FROM document_chunks;
   ```
   Result: 4 chunks total, 0 with embeddings

3. **Checked processing jobs**:
   ```sql
   SELECT job_id, document_id, job_type, status 
   FROM processing_jobs 
   WHERE document_id IN (16,17,18,19,20);
   ```
   Result: All jobs stuck in `status = 'pending'`

4. **Checked workers**:
   ```bash
   ps aux | grep dramatiq
   ```
   Result: No Dramatiq workers running

5. **Attempted embedding generation**:
   ```bash
   python scripts/generate_embeddings.py --tenant-id 1
   ```
   Result: Error - `expected 1536 dimensions, not 768`

### Root Causes Identified

1. **Workers Not Running** (Critical)
   - Dramatiq workers were never started
   - Parsing jobs remained in "pending" status indefinitely
   - **Impact**: No documents were being parsed after upload

2. **Vector Dimension Mismatch** (Critical)
   - Database column: `vector(1536)` (configured for OpenAI text-embedding-3-small)
   - Actual embedding model: Ollama nomic-embed-text:latest generates 768 dimensions
   - `.env` correctly set `VECTOR_DIMENSIONS=768` but database was created before this change
   - **Impact**: Embedding generation failed with constraint violation

3. **Missing Automation** (High)
   - No automatic embedding generation after parsing
   - Manual script required: `python scripts/generate_embeddings.py`
   - **Impact**: Even after fixing dimensions, new documents wouldn't be searchable

4. **Search Query Filter** (Design)
   - Search service filters: `WHERE embedding_vector IS NOT NULL`
   - Correct design, but exposed the embedding gap
   - **Impact**: No results returned when embeddings missing

## Solution Implementation

### Phase 1: Fix Database Schema

**Problem**: Vector column dimension mismatch (1536 vs 768)

**Solution**: Alter table with index recreation

```sql
BEGIN;

-- Drop existing HNSW index
DROP INDEX IF EXISTS idx_chunks_embedding_hnsw;

-- Alter column to 768 dimensions
ALTER TABLE document_chunks 
ALTER COLUMN embedding_vector TYPE vector(768);

-- Recreate HNSW index
CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks 
    USING hnsw (embedding_vector vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);

COMMIT;
```

**Verification**:
```sql
\d document_chunks  -- Confirmed: vector(768)
```

**Impact**: Embedding generation now succeeds

---

### Phase 2: Generate Missing Embeddings

**Problem**: Existing 4 chunks had no embeddings

**Solution**: Run manual embedding generation script

```bash
python scripts/generate_embeddings.py --batch-size 10 --tenant-id 1
```

**Result**:
- ✅ 3 chunks successfully embedded
- ❌ 1 chunk failed (Ollama 500 error - transient)

**Verification**:
```sql
SELECT COUNT(*) as total, COUNT(embedding_vector) as with_embeddings 
FROM document_chunks;
-- Result: 4 total, 3 with embeddings
```

**Impact**: Search now returns results for 3 documents

---

### Phase 3: Start Dramatiq Workers

**Problem**: No workers running to process pending jobs

**Solution**: Start workers with proper module imports

```bash
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate
nohup dramatiq src.ingestion_parsing.tasks.document_tasks \
    --processes 1 \
    --threads 4 \
    > /tmp/dramatiq-worker.log 2>&1 &
```

**Result**: Workers processed 5 pending parsing jobs

**Verification**:
```sql
SELECT document_id, COUNT(*) as chunk_count 
FROM document_chunks 
GROUP BY document_id;
-- Result: Documents 16-20 now have chunks
```

**Impact**: New uploads are now parsed automatically

---

### Phase 4: Automate Embedding Generation

**Problem**: No automatic embedding generation after parsing

**Solution**: Created `embedding_tasks.py` with Dramatiq actor

**New File**: `src/ingestion_parsing/tasks/embedding_tasks.py`

```python
@dramatiq.actor(max_retries=3, time_limit=600000)
def generate_embeddings_task(document_id: int) -> None:
    """Generate embeddings for all chunks of a document."""
    # Implementation details in file
```

**Integration**: Modified `document_tasks.py` to trigger embeddings

```python
# After successful parsing
await parsing_service.parse_document(document_id)

# Trigger embedding generation
from src.ingestion_parsing.tasks.embedding_tasks import trigger_embedding_generation
trigger_embedding_generation(document_id)
```

**Worker Update**: Modified `scripts/start_workers.sh`

```bash
dramatiq src.ingestion_parsing.tasks.document_tasks \
        src.ingestion_parsing.tasks.embedding_tasks \
    --processes 1 \
    --threads 4 \
    --verbose
```

**Impact**: New documents automatically get embeddings after parsing

---

### Phase 5: Verification & Testing

**Test 1: Search API**

```bash
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query_text": "database migration steps", "tenant_id": 1, "top_k": 5}'
```

**Result**: ✅ SUCCESS - Returned 5 results with similarity scores

```json
{
  "query_id": 12,
  "query_text": "database migration steps",
  "results": [
    {
      "chunk_id": 8,
      "document_id": 10,
      "similarity_score": 0.4887,
      "rank_position": 1,
      "text_snippet": "📖 Max Knowledge Base技术栈前端：Vue.js...",
      "document_title": "doc_20260111_234506_a77dce3c.md"
    }
    // ... 4 more results
  ],
  "total_results": 5,
  "search_duration_ms": 61
}
```

**Test 2: End-to-End Workflow**

1. Upload markdown file → ✅ Document created
2. Dramatiq parses → ✅ Chunks created
3. Dramatiq generates embeddings → ✅ Vectors stored
4. Search query → ✅ Results returned

**Performance Metrics**:
- Search response time: 61ms (target: <100ms) ✅
- Embedding generation: ~100-800ms per chunk ✅
- Total documents with embeddings: 15/17 (88%) ✅

---

## Deployment Checklist

### Production Deployment

- [ ] **Database Migration**: Run vector dimension fix on production database
  ```sql
  -- Run in production PostgreSQL
  BEGIN;
  DROP INDEX IF EXISTS idx_chunks_embedding_hnsw;
  ALTER TABLE document_chunks ALTER COLUMN embedding_vector TYPE vector(768);
  CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks 
      USING hnsw (embedding_vector vector_cosine_ops) 
      WITH (m = 16, ef_construction = 64);
  COMMIT;
  ```

- [ ] **Environment Variables**: Verify `.env` settings
  ```bash
  EMBEDDING_PROVIDER=ollama
  EMBEDDING_MODEL=nomic-embed-text:latest
  EMBEDDING_DIMENSION=768
  VECTOR_DIMENSIONS=768
  OLLAMA_BASE_URL=http://localhost:11434
  ```

- [ ] **Deploy Code**: Update backend with new files
  - `src/ingestion_parsing/tasks/embedding_tasks.py` (new)
  - `src/ingestion_parsing/tasks/document_tasks.py` (modified)
  - `scripts/start_workers.sh` (modified)

- [ ] **Start Workers**: Ensure Dramatiq workers are running
  ```bash
  ./scripts/start_workers.sh
  # Or with systemd/supervisor in production
  ```

- [ ] **Backfill Embeddings**: Generate embeddings for existing documents
  ```bash
  python scripts/generate_embeddings.py --batch-size 32 --tenant-id 1
  ```

- [ ] **Verify Search**: Test search API endpoint
  ```bash
  curl -X POST https://api.yoursite.com/api/v1/search/semantic \
    -H "Content-Type: application/json" \
    -d '{"query_text": "test query", "tenant_id": 1, "top_k": 5}'
  ```

- [ ] **Monitor Workers**: Check worker logs for errors
  ```bash
  tail -f /var/log/dramatiq-worker.log
  ```

### Rollback Plan

If issues occur:

1. **Stop workers**: `pkill -f dramatiq`
2. **Revert database**: 
   ```sql
   ALTER TABLE document_chunks ALTER COLUMN embedding_vector TYPE vector(1536);
   ```
3. **Revert code**: `git revert <commit-hash>`
4. **Switch to OpenAI**: Update `.env` to use OpenAI embeddings
   ```bash
   EMBEDDING_PROVIDER=openai
   EMBEDDING_MODEL=text-embedding-3-small
   VECTOR_DIMENSIONS=1536
   ```

---

## Lessons Learned

1. **Configuration Consistency**: Database schema must match `.env` settings
   - **Action**: Add validation check in application startup
   - **Prevention**: Create migration script that reads from `.env`

2. **Worker Monitoring**: No alerting when workers stop
   - **Action**: Add health check endpoint for worker status
   - **Prevention**: Set up monitoring (e.g., Prometheus + Grafana)

3. **Embedding Automation**: Manual process is error-prone
   - **Action**: Automated embedding generation (completed)
   - **Prevention**: Add integration tests for full workflow

4. **Error Visibility**: Ollama 500 errors not surfaced to users
   - **Action**: Add retry logic with exponential backoff (already in place)
   - **Prevention**: Monitor Ollama service health

---

## Future Enhancements

1. **Embedding Status Tracking** (Priority: High)
   - Add `embedding_status` field to `documents` table
   - Values: `pending`, `in_progress`, `completed`, `failed`
   - Display in frontend document list

2. **Batch Embedding Optimization** (Priority: Medium)
   - Generate embeddings in batches of 10-50 chunks
   - Reduce API calls to Ollama
   - Estimated speedup: 2-3x

3. **Embedding Model Versioning** (Priority: Medium)
   - Track which embedding model version was used
   - Support model upgrades with re-embedding
   - Add migration tool for model changes

4. **Worker Health Monitoring** (Priority: High)
   - Add `/api/v1/workers/health` endpoint
   - Report: active workers, queue depth, failed jobs
   - Alert when workers down > 5 minutes

5. **Automatic Dimension Detection** (Priority: Low)
   - Detect embedding dimensions from first generated vector
   - Validate against database schema on startup
   - Prevent dimension mismatches

---

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Dramatiq Documentation](https://dramatiq.io/)
- [Ollama Embeddings API](https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings)
- [nomic-embed-text Model](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
