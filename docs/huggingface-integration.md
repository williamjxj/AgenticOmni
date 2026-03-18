
# HuggingFace Datasets Integration Guide & Implementation Summary

## Overview


OmniAI now supports importing datasets from HuggingFace Hub directly into your RAG system. This integration allows you to:

- Import SQuAD and other HuggingFace datasets
- Automatically chunk text using your existing 512-token chunker
- Generate embeddings and store in pgvector
- Search imported datasets alongside your uploaded documents


## Implementation Summary

### ✅ Completed Tasks

1. Added `datasets` to requirements.txt
2. Updated `config/settings.py` to load `HUGGINGFACE_TOKEN`
3. Created ingestion and API routes for datasets
4. Created comprehensive documentation and test suite

### 📁 Files Created/Modified
- `src/ingestion_parsing/services/HF_TOKEN_REMOVED.py`
- `src/ingestion_parsing/tasks/HF_TOKEN_REMOVED.py`
- `src/api/routes/datasets.py`
- `docs/huggingface-integration.md`
- `QUICKSTART_HF.md`
- `test_HF_TOKEN_REMOVED.py`

---

### 🏗️ Architecture

#### Components
```
┌─────────────────────────────────────────────────────────┐
│                   API Layer                              │
│  /api/v1/datasets/import                                 │
│  /api/v1/datasets/validate/{name}                        │
│  /api/v1/datasets/supported                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Background Tasks (Dramatiq)                 │
│  import_HF_TOKEN_REMOVED()                                │
│  → Load from HF → Create docs → Chunk → Embed           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                Service Layer                             │
│  HFDatasetLoader: load_squad_dataset()                   │
│  ChunkingService: chunk_document()                       │
│  EmbeddingService: generate_embeddings()                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Database (PostgreSQL + pgvector)            │
│  documents → document_chunks → embeddings                │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 Data Flow

#### Import Process
1. **API Request** → User calls `/api/v1/datasets/import`
2. **Validation** → Check dataset name and parameters
3. **Task Queue** → Dramatiq task triggered (returns job_id)
4. **Load Dataset** → HFDatasetLoader fetches from HuggingFace
5. **Create Documents** → Store in `documents` table
6. **Chunking** → Split text (512 tokens, 50 overlap)
7. **Store Chunks** → Save to `document_chunks` table
8. **Embedding** → Trigger embedding generation task

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The `datasets==3.3.0` package has been added to your requirements.

### 2. Verify Environment Configuration

Your `.env` already has the HuggingFace token:
```bash
HUGGINGFACE_TOKEN=HF_TOKEN_REMOVED
```

This token is now loaded via `config/settings.py`.

## API Endpoints

### 1. Import Dataset

**Endpoint:** `POST /api/v1/datasets/import`

Import a HuggingFace dataset into the RAG system.

**Request Body:**
```json
{
  "dataset_name": "rajpurkar/squad",
  "tenant_id": 1,
  "split": "train",
  "limit": 500,
  "user_id": null
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/datasets/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "rajpurkar/squad",
    "tenant_id": 1,
    "split": "train",
    "limit": 500
  }'
```

**Response:**
```json
{
  "message": "Dataset import started. Processing 500 records from rajpurkar/squad.",
  "job_id": "abc123-def456",
  "dataset_name": "rajpurkar/squad",
  "split": "train",
  "limit": 500
}
```

### 2. Validate Dataset Access

**Endpoint:** `GET /api/v1/datasets/validate/{dataset_name}`

Check if a dataset is accessible before importing.

**Example:**
```bash
curl "http://localhost:8000/api/v1/datasets/validate/rajpurkar%2Fsquad"
```

**Response:**
```json
{
  "dataset_name": "rajpurkar/squad",
  "accessible": true,
  "message": "Dataset 'rajpurkar/squad' is accessible and ready to import"
}
```

### 3. List Supported Datasets

**Endpoint:** `GET /api/v1/datasets/supported`

Get a list of recommended datasets.

**Example:**
```bash
curl "http://localhost:8000/api/v1/datasets/supported"
```

## Usage Examples

### Example 1: Import SQuAD Dataset (500 samples)

```bash
# 1. Start your API server (if not running)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 2. Import SQuAD dataset
curl -X POST "http://localhost:8000/api/v1/datasets/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "rajpurkar/squad",
    "tenant_id": 1,
    "split": "train",
    "limit": 500
  }'

# 3. Check the job status (use job_id from response)
# You can query the jobs table or check logs
```

### Example 2: Validate Before Importing

```bash
# First validate access
curl "http://localhost:8000/api/v1/datasets/validate/rajpurkar%2Fsquad"

# If accessible, proceed with import
curl -X POST "http://localhost:8000/api/v1/datasets/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "rajpurkar/squad",
    "tenant_id": 1,
    "split": "validation",
    "limit": 100
  }'
```

### Example 3: Using Python Client

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Import SQuAD dataset
response = requests.post(
    f"{BASE_URL}/datasets/import",
    json={
        "dataset_name": "rajpurkar/squad",
        "tenant_id": 1,
        "split": "train",
        "limit": 500,
    }
)

result = response.json()
print(f"Job ID: {result['job_id']}")
print(f"Message: {result['message']}")
```

## How It Works

### Pipeline Flow

```
HuggingFace Hub
      ↓
1. Load Dataset (HFDatasetLoader)
      ↓
2. Create Document Records (DocumentRepository)
      ↓
3. Chunk Text (ChunkingService - 512 tokens)
      ↓
4. Store Chunks (ChunkRepository)
      ↓
5. Generate Embeddings (Dramatiq Task)
      ↓
6. Store in pgvector (VectorStore)
      ↓
7. Ready for Search & RAG!
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Loader Service** | `src/ingestion_parsing/services/HF_TOKEN_REMOVED.py` | Loads datasets from HuggingFace |
| **Background Task** | `src/ingestion_parsing/tasks/HF_TOKEN_REMOVED.py` | Async processing with Dramatiq |
| **API Endpoint** | `src/api/routes/datasets.py` | REST API for import/validation |
| **Settings** | `config/settings.py` | Configuration with HF token |

### Data Storage

Imported datasets are stored as regular documents:

- **Storage Path:** `hf://{dataset_name}/{split}/{index}`
- **File Type:** `text/plain`
- **Metadata:** Includes dataset name, split, title, etc.
- **Deduplication:** Content hash prevents duplicates

## Supported Datasets

| Dataset | Identifier | Use Case | Recommended Limit |
|---------|-----------|----------|-------------------|
| **SQuAD** | `rajpurkar/squad` | QA over documents | 500 |
| **PubMed QA** | `pubmed_qa` | Scientific doc RAG | 1000 |
| **Natural Questions** | `google-research-datasets/natural_questions` | General QA | 500 |
| **MultiDoc2Dial** | `multidoc2dial` | Multi-doc dialogue | 500 |
| **WikiText** | `wikitext` | General knowledge | 1000 |
| **DocumentVQA** | `HuggingFaceM4/DocumentVQA` | Visual QA | 100 |

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# HuggingFace Configuration
HUGGINGFACE_TOKEN=HF_TOKEN_REMOVED  # Already set in your .env
```

### Settings

The token is loaded automatically via `config/settings.py`:

```python
huggingface_token: str | None = Field(
    default=None,
    description="HuggingFace API token for dataset access",
)
```

## Best Practices

### 1. Start Small

Always test with a small limit first:
```json
{
  "limit": 100
}
```

### 2. Monitor Background Jobs

The import runs asynchronously via Dramatiq. Monitor:
- Check Redis for job status
- View logs: `tail -f logs/app.log`
- Query the `jobs` table in PostgreSQL

### 3. Handle Duplicates

The system automatically deduplicates based on `content_hash`. Re-importing the same dataset won't create duplicates.

### 4. Tenant Isolation

Use `tenant_id=1` for testing. Create separate tenants for different projects:
```json
{
  "tenant_id": 1  // Default tenant
}
```

### 5. Batch Processing

For large datasets, use streaming and limits:
```json
{
  "limit": 10000,  // Max per import
  "split": "train"
}
```

## Troubleshooting

### Issue: "Dataset not accessible"

**Solution:**
1. Verify your HuggingFace token is set in `.env`
2. Check token has access to the dataset
3. Try validation endpoint first:
   ```bash
   curl "http://localhost:8000/api/v1/datasets/validate/rajpurkar%2Fsquad"
   ```

### Issue: "Import takes too long"

**Solution:**
1. Reduce the `limit` parameter
2. Check Dramatiq worker is running
3. Monitor Redis connection
4. Check database connection pool

### Issue: "Embeddings not generated"

**Solution:**
1. Verify Ollama is running: `curl http://localhost:11434`
2. Check embedding model is available: `ollama list`
3. Review embedding task logs
4. Ensure `EMBEDDING_PROVIDER=ollama` in `.env`

## Testing

### Quick Test

```bash
# 1. Validate access
curl "http://localhost:8000/api/v1/datasets/validate/rajpurkar%2Fsquad"

# 2. Import small batch
curl -X POST "http://localhost:8000/api/v1/datasets/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "rajpurkar/squad",
    "tenant_id": 1,
    "limit": 10
  }'

# 3. Search for imported content
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "tenant_id": 1,
    "limit": 5
  }'
```

### Verify Import

```sql
-- Check documents
SELECT document_id, filename, storage_path, document_metadata 
FROM documents 
WHERE storage_path LIKE 'hf://%';

-- Check chunks
SELECT COUNT(*) as chunk_count
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.document_id
WHERE d.storage_path LIKE 'hf://%';
```

## Architecture

### Database Schema

Imported datasets use existing tables:

- **documents:** Document metadata
- **document_chunks:** Chunked text (512 tokens)
- **jobs:** Import job tracking

### Background Processing

```python
# Task flow
import_HF_TOKEN_REMOVED
  → load_squad_dataset()
  → create_document()
  → chunk_document()
  → create_chunk()
  → trigger_embedding_generation()
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

Navigate to the "datasets" section to see all endpoints.

## Next Steps

1. **Test the Integration:**
   ```bash
   pip install -r requirements.txt
   uvicorn src.api.main:app --reload
   ```

2. **Import SQuAD Dataset:**
   Use the curl examples above

3. **Verify Search:**
   Test if imported content is searchable

4. **Scale Up:**
   Increase limits after testing

5. **Add More Datasets:**
   Try other supported datasets

## Support

For issues or questions:
- Check logs: `logs/app.log`
- Review Dramatiq queue: Redis keys `dramatiq:*`
- Query jobs table: `SELECT * FROM jobs ORDER BY created_at DESC;`

---

**Status:** ✅ Ready to use
**Version:** v0.2.0
**Last Updated:** 2026-02-21
