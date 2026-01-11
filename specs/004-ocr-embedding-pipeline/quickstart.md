# Quickstart: OCR and Embedding Pipeline

**Feature**: 004-ocr-embedding-pipeline  
**Date**: 2026-01-11  
**Audience**: Developers implementing this feature

## Overview

This quickstart guide provides a step-by-step walkthrough for setting up, developing, and testing the OCR and Embedding Pipeline feature. Follow these instructions to get the feature running locally and understand the development workflow.

## Prerequisites

### System Requirements

- **Python**: 3.12+
- **PostgreSQL**: 14+ with pgvector extension installed
- **Redis**: 6.0+ (for Dramatiq task queue)
- **Hardware**:
  - CPU: 4+ cores
  - RAM: 8GB minimum, 16GB recommended
  - GPU: Optional but recommended (NVIDIA with CUDA 11.0+)
  - Disk: 10GB free space for models and test data

### Python Dependencies

The project uses `pyproject.toml` for dependency management. Key new dependencies to add:

```bash
# Add to pyproject.toml dependencies array
"sentence-transformers>=2.3.0",    # Embedding models
"paddleocr>=2.7.0",                 # OCR engine
"paddlpaddle-gpu>=2.6.0",           # GPU support (or paddlepaddle for CPU)
"langdetect>=1.0.9",                # Language detection
```

### Environment Setup

1. **Clone and activate virtual environment**:

```bash
cd /Users/william.jiang/my-apps/ai-edocuments
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. **Install dependencies**:

```bash
pip install -e ".[dev]"  # Install project in editable mode with dev dependencies
```

3. **Install pgvector extension** (if not already installed):

```bash
# Connect to PostgreSQL as superuser
psql -U postgres -d agenticomni

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

4. **Configure environment variables**:

Copy `.env.example` to `.env` and set:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/agenticomni

# Redis (for Dramatiq)
REDIS_URL=redis://localhost:6379/0

# OCR Settings
OCR_ENGINE=auto  # auto, paddleocr, tesseract
OCR_LANGUAGES=en,zh
OCR_CONFIDENCE_THRESHOLD=0.7
OCR_GPU_ENABLED=true  # Set to false if no GPU

# Embedding Settings
EMBEDDING_MODEL=multilingual-e5-base
EMBEDDING_BATCH_SIZE=32
EMBEDDING_GPU_ENABLED=true

# Processing Settings
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CONCURRENT_JOBS=4
```

5. **Run database migrations**:

```bash
# Apply all migrations including new OCR/embedding tables
alembic upgrade head
```

6. **Download embedding models**:

The embedding model will download automatically on first use, but you can pre-download:

```python
from sentence_transformers import SentenceTransformer

# Download model (this will cache locally)
model = SentenceTransformer('intfloat/multilingual-e5-base')
```

## Development Workflow

### Step 1: Database Migrations

Create and apply new migrations for OCR and embedding features:

```bash
# The migrations are already created in the plan, apply them
alembic upgrade head

# Verify tables were created
psql -U postgres -d agenticomni -c "\d extracted_texts"
psql -U postgres -d agenticomni -c "\d document_chunks"
```

### Step 2: Implement Core Services

Follow this implementation order (aligns with P1, P2, P3 priorities):

#### Phase 1: Text Extraction (P1 - MVP)

1. **OCR Service** (`src/ingestion_parsing/services/ocr_service.py`):
   - Integrate PaddleOCR for image-based text extraction
   - Integrate Tesseract as fallback
   - Extract text with confidence scores
   - Store results in `extracted_texts` table

2. **Document Parser Integration** (`src/ingestion_parsing/parsers/docling_parser.py`):
   - Use Docling for native PDF/DOCX parsing
   - Route image content to OCR service
   - Preserve document structure

3. **API Endpoints** (`src/api/routes/ocr.py`):
   - `POST /api/v1/documents/{id}/ocr` - Trigger OCR
   - `GET /api/v1/documents/{id}/ocr/status` - Check status
   - `GET /api/v1/documents/{id}/extracted-text` - Get results

#### Phase 2: Embeddings & Search (P2)

1. **Chunking Service** (`src/ingestion_parsing/services/chunking_service.py`):
   - Implement 500-token chunking with 50-token overlap
   - Use tiktoken for accurate token counting
   - Preserve page/section context

2. **Embedding Service** (`src/ingestion_parsing/services/embedding_service.py`):
   - Load multilingual-e5-base model
   - Generate embeddings in batches
   - Store vectors in `document_chunks.embedding_vector`

3. **Vector Search Service** (`src/rag_orchestration/services/vector_search.py`):
   - Implement similarity search with pgvector
   - Support metadata filtering
   - Return ranked results with snippets

4. **API Endpoints** (`src/api/routes/search.py`):
   - `POST /api/v1/search` - Semantic search
   - `GET /api/v1/documents/{id}/similar` - Find similar docs
   - `GET /api/v1/documents/{id}/embeddings` - Embedding status

#### Phase 3: Batch Processing (P3)

1. **Batch Service** (`src/ingestion_parsing/services/batch_service.py`):
   - Handle multi-document uploads
   - Parallel processing coordination
   - Progress tracking

2. **Dramatiq Actors** (`src/ingestion_parsing/tasks/`):
   - `ocr_actor.py` - OCR processing tasks
   - `embedding_actor.py` - Embedding generation tasks
   - `batch_actor.py` - Batch orchestration

### Step 3: Testing

#### Unit Tests

```bash
# Run unit tests for new services
pytest tests/unit/test_ocr_service.py -v
pytest tests/unit/test_chunking_service.py -v
pytest tests/unit/test_embedding_service.py -v
pytest tests/unit/test_vector_search.py -v
```

Example unit test structure:

```python
# tests/unit/test_chunking_service.py
import pytest
from src.ingestion_parsing.services.chunking_service import ChunkingService

@pytest.fixture
def chunking_service():
    return ChunkingService(chunk_size=500, overlap=50)

def test_chunk_short_document(chunking_service):
    """Test chunking of document shorter than chunk size."""
    text = "This is a short document with less than 500 tokens."
    chunks = chunking_service.chunk_text(text)
    
    assert len(chunks) == 1
    assert chunks[0].token_count < 500

def test_chunk_long_document_with_overlap(chunking_service):
    """Test that overlap is correctly applied between chunks."""
    text = "word " * 600  # Create 600-word document
    chunks = chunking_service.chunk_text(text)
    
    assert len(chunks) > 1
    # Verify overlap exists
    overlap_text = chunks[0].chunk_text[-100:]  # Last 100 chars of chunk 1
    assert overlap_text in chunks[1].chunk_text  # Should appear in chunk 2
```

#### Integration Tests

```bash
# Run integration tests with real database
pytest tests/integration/test_ocr_pipeline.py -v
pytest tests/integration/test_embedding_pipeline.py -v
pytest tests/integration/test_search_api.py -v
```

Example integration test:

```python
# tests/integration/test_ocr_pipeline.py
import pytest
from httpx import AsyncClient
from tests.conftest import test_app, async_session

@pytest.mark.asyncio
async def test_ocr_extraction_end_to_end(async_client: AsyncClient):
    """Test complete OCR extraction workflow."""
    # 1. Upload a scanned PDF
    with open("tests/fixtures/sample_scanned.pdf", "rb") as f:
        response = await async_client.post(
            "/api/v1/documents",
            files={"file": ("scanned.pdf", f, "application/pdf")}
        )
    assert response.status_code == 201
    document_id = response.json()["document_id"]
    
    # 2. Trigger OCR processing
    response = await async_client.post(
        f"/api/v1/documents/{document_id}/ocr",
        json={"engine": "paddleocr", "languages": ["en"]}
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    # 3. Wait for processing to complete (or poll status)
    # In real tests, use polling or test workers
    
    # 4. Verify extracted text
    response = await async_client.get(
        f"/api/v1/documents/{document_id}/extracted-text"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_pages"] > 0
    assert len(data["pages"]) > 0
    assert data["pages"][0]["extraction_method"] in ["ocr_paddleocr", "ocr_tesseract"]
```

### Step 4: Local Testing

#### Start Services

1. **Start Redis** (if not running):

```bash
redis-server
```

2. **Start Dramatiq Workers**:

```bash
# In a separate terminal
dramatiq src.ingestion_parsing.tasks.ocr_actor \
         src.ingestion_parsing.tasks.embedding_actor \
         src.ingestion_parsing.tasks.batch_actor \
         --processes 4 \
         --threads 2
```

3. **Start FastAPI Server**:

```bash
# In another terminal
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Verify services are running**:

```bash
# Check API health
curl http://localhost:8000/health

# Check Redis connection
redis-cli ping

# Check database connection
psql -U postgres -d agenticomni -c "SELECT 1"
```

#### Manual Testing with Sample Documents

```bash
# 1. Upload a scanned PDF
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@tests/fixtures/sample_scanned.pdf"

# Response: {"document_id": 42, ...}

# 2. Trigger OCR
curl -X POST http://localhost:8000/api/v1/documents/42/ocr \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"engine": "auto", "languages": ["en", "zh"]}'

# Response: {"job_id": 1234, "status": "pending", ...}

# 3. Check OCR status
curl http://localhost:8000/api/v1/documents/42/ocr/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Once OCR completes, generate embeddings
curl -X POST http://localhost:8000/api/v1/documents/42/embeddings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "multilingual-e5-base"}'

# 5. Perform semantic search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the payment terms?",
    "limit": 10,
    "filters": {"document_ids": [42]}
  }'

# 6. Find similar documents
curl http://localhost:8000/api/v1/documents/42/similar?limit=5 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 5: Performance Testing

Test with realistic document volumes:

```bash
# Generate test load with multiple documents
python scripts/test_load.py \
  --documents 100 \
  --concurrent 10 \
  --endpoint http://localhost:8000

# Monitor resource usage
htop  # CPU/Memory
nvidia-smi  # GPU (if applicable)
redis-cli INFO  # Redis stats
```

## Common Development Tasks

### Adding a New OCR Engine

1. Create engine adapter in `src/ingestion_parsing/parsers/ocr/`:

```python
# src/ingestion_parsing/parsers/ocr/custom_ocr.py
class CustomOCREngine:
    def extract_text(self, image, languages=None):
        # Implement extraction logic
        return {
            "text": extracted_text,
            "confidence": confidence_score,
            "bounding_boxes": boxes
        }
```

2. Register engine in OCR service:

```python
# src/ingestion_parsing/services/ocr_service.py
OCR_ENGINES = {
    "paddleocr": PaddleOCREngine,
    "tesseract": TesseractEngine,
    "custom": CustomOCREngine,  # Add here
}
```

3. Add tests for new engine.

### Switching Embedding Models

1. Update environment variable:

```bash
EMBEDDING_MODEL=multilingual-e5-large  # Or other model
```

2. Download new model:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-large')
```

3. Regenerate embeddings for existing documents:

```bash
# Use API endpoint
curl -X POST http://localhost:8000/api/v1/documents/batch/embeddings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "document_ids": [1, 2, 3, ...],
    "model": "multilingual-e5-large",
    "regenerate": true
  }'
```

### Debugging OCR Issues

1. **Check OCR logs**:

```bash
# View structured logs
tail -f logs/ocr.log | jq .

# Filter for errors
cat logs/ocr.log | jq 'select(.level == "error")'
```

2. **Inspect extracted text**:

```sql
-- Check confidence scores
SELECT document_id, page_number, confidence_score, 
       LEFT(text_content, 100) as preview
FROM extracted_texts
WHERE confidence_score < 0.7
ORDER BY confidence_score ASC;
```

3. **Test OCR on individual image**:

```python
from src.ingestion_parsing.services.ocr_service import OCRService
from PIL import Image

service = OCRService(engine="paddleocr")
image = Image.open("problem_image.png")
result = service.extract_text(image, languages=["en"])
print(result)
```

### Monitoring Vector Search Performance

1. **Check HNSW index stats**:

```sql
-- Index size and coverage
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';
```

2. **Analyze query performance**:

```sql
-- Enable query timing
EXPLAIN ANALYZE
SELECT chunk_id, 1 - (embedding_vector <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM document_chunks
WHERE tenant_id = 1
ORDER BY embedding_vector <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

3. **Monitor search latency**:

```bash
# Search latency percentiles
cat logs/search.log | jq '.search_duration_ms' | \
  awk '{sum+=$1; sumsq+=$1*$1; count++} 
       END {print "Avg:", sum/count, "ms"; 
            print "Std:", sqrt(sumsq/count - (sum/count)^2), "ms"}'
```

## Troubleshooting

### Issue: OCR extraction is very slow

**Symptoms**: OCR jobs take minutes per page

**Solutions**:
1. Enable GPU acceleration: `OCR_GPU_ENABLED=true`
2. Reduce image resolution before OCR (e.g., 300 DPI max)
3. Use Tesseract for simple documents (faster than PaddleOCR)
4. Increase Dramatiq worker count

### Issue: Embedding generation fails with out-of-memory

**Symptoms**: Worker crashes during embedding generation

**Solutions**:
1. Reduce batch size: `EMBEDDING_BATCH_SIZE=16` (down from 32)
2. Use smaller model: `multilingual-e5-base` instead of `large`
3. Process documents sequentially instead of parallel
4. Add more RAM or use GPU with larger VRAM

### Issue: Search results are not relevant

**Symptoms**: Semantic search returns poor matches

**Solutions**:
1. Verify embeddings were generated: Check `embedding_status = 'completed'`
2. Increase `min_score` threshold to filter low-quality matches
3. Check that documents and query are in supported languages (en, zh)
4. Rebuild HNSW index: `REINDEX INDEX idx_chunks_embedding_hnsw`
5. Try different embedding model (e.g., upgrade to `multilingual-e5-large`)

### Issue: pgvector similarity search is slow

**Symptoms**: Search queries take >2 seconds

**Solutions**:
1. Verify HNSW index exists: `\d+ document_chunks`
2. Rebuild index with tuned parameters:
   ```sql
   DROP INDEX IF EXISTS idx_chunks_embedding_hnsw;
   CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks 
   USING hnsw (embedding_vector vector_cosine_ops) 
   WITH (m = 32, ef_construction = 128);  -- Increase from 16, 64
   ```
3. Filter by `tenant_id` before vector search
4. Use smaller result limits (`limit=10` instead of `limit=100`)

## Next Steps

After completing this quickstart:

1. **Review the full plan**: See `plan.md` for architecture details
2. **Implement tasks**: Follow `tasks.md` for specific implementation steps
3. **Set up CI/CD**: Configure GitHub Actions for automated testing
4. **Deploy to staging**: Test with real document volumes
5. **Monitor in production**: Set up alerting for processing failures

## Additional Resources

- **API Contracts**: See `contracts/` directory for detailed API specifications
- **Data Model**: See `data-model.md` for database schema details
- **Research**: See `research.md` for technology choices and rationale
- **PaddleOCR Docs**: https://github.com/PaddlePaddle/PaddleOCR
- **Sentence Transformers**: https://www.sbert.net/
- **pgvector Guide**: https://github.com/pgvector/pgvector
- **Dramatiq Docs**: https://dramatiq.io/

## Getting Help

- **Internal**: Post in #ai-edocuments Slack channel
- **Issues**: Open GitHub issue with `004-ocr-embedding-pipeline` label
- **Code Review**: Tag `@ai-platform-team` in PRs

---

**Last Updated**: 2026-01-11  
**Maintainer**: AI Platform Team
