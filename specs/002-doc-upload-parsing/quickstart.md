# Quickstart Guide: Document Upload and Parsing

**Feature**: 002-doc-upload-parsing  
**Date**: 2026-01-09  
**Status**: Development

---

## Overview

This guide walks you through setting up and testing the document upload and parsing feature locally. By the end, you'll have:

- Document parsing workers running
- API endpoints for upload/download/status
- Test documents uploaded and parsed
- Real-time job status tracking working

**Estimated Setup Time**: 30 minutes

---

## Prerequisites

Before starting, ensure you have the base application skeleton running:

- ✅ Python 3.12+ with virtual environment activated
- ✅ PostgreSQL 16 with pgvector (via Docker)
- ✅ Redis 7 (via Docker)
- ✅ FastAPI server running on port 8000
- ✅ Base migrations applied (`alembic upgrade head`)

**Verify Base Setup**:

```bash
# Check services are running
docker-compose ps

# Expected output:
#   postgres    running    0.0.0.0:5436->5432/tcp
#   redis       running    0.0.0.0:6379->6379/tcp

# Check API health
curl http://localhost:8000/api/v1/health

# Expected: {"status":"healthy",...}
```

If any checks fail, see [../../README.md](../../README.md) for base setup instructions.

---

## Step 1: Install New Dependencies

Install document parsing and task queue dependencies:

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install document parsing dependencies
pip install docling python-docx python-magic aiofiles

# Install task queue
pip install dramatiq[redis] dramatiq[watch]

# Install file upload support
pip install python-multipart

# Install storage client (for S3, optional)
pip install boto3

# Install for token counting
pip install tiktoken

# Optional: ClamAV for malware scanning
pip install clamd

# Verify installations
python -c "import docling; print('Docling OK')"
python -c "import dramatiq; print('Dramatiq OK')"
python -c "import magic; print('python-magic OK')"
```

**macOS Note**: If `python-magic` fails, install libmagic:

```bash
brew install libmagic
```

**Linux Note**: Install libmagic1 if not present:

```bash
sudo apt-get install libmagic1
```

---

## Step 2: Configure Environment

Add document upload settings to your `.env` file:

```bash
# Open .env file
nano .env  # or use your preferred editor

# Add these settings (copy-paste):
# ===========================================
# Document Upload Settings
# ===========================================
# Storage backend: 'local' or 's3'
STORAGE_BACKEND=local

# Local storage directory (for development)
UPLOAD_DIR=./uploads
TEMP_UPLOAD_DIR=./tmp/uploads

# File upload limits
MAX_UPLOAD_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,txt

# Processing settings
MAX_CONCURRENT_PARSING_JOBS=5
PARSING_TIMEOUT_SECONDS=300

# Chunk settings for RAG
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
MIN_CHUNK_SIZE_TOKENS=100

# Task queue (Dramatiq)
DRAMATIQ_BROKER_URL=redis://localhost:6379/1
DRAMATIQ_RESULT_BACKEND=redis://localhost:6379/1

# Malware scanning (optional, set to false if ClamAV not installed)
ENABLE_MALWARE_SCANNING=false
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# S3 settings (only if STORAGE_BACKEND=s3)
# S3_BUCKET=agenticomni-documents
# S3_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Save and close** the file.

**Validate Configuration**:

```bash
python -c "from config.settings import Settings; s=Settings(); print(f'Upload dir: {s.UPLOAD_DIR}')"

# Expected output: Upload dir: ./uploads
```

---

## Step 3: Create Storage Directories

Create local directories for file storage:

```bash
# Run setup script
./scripts/setup_storage.sh

# OR manually:
mkdir -p uploads
mkdir -p tmp/uploads
chmod 755 uploads tmp/uploads

# Verify
ls -ld uploads tmp/uploads

# Expected:
#   drwxr-xr-x  ... uploads
#   drwxr-xr-x  ... tmp/uploads
```

---

## Step 4: Run Database Migrations

Apply the new migrations to add document upload fields:

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add document upload and parsing fields"

# Review generated migration
ls src/storage_indexing/migrations/versions/

# Apply migration
alembic upgrade head

# Verify
alembic current

# Expected: <revision_id> (head)
```

**Verify Schema Changes**:

```bash
# Connect to database
psql postgresql://agenti_user:agenti_user@localhost:5436/agenticomni

# Check new fields
\d documents

# Expected columns: content_hash, language, page_count, uploaded_by, original_filename, mime_type

# Check new table
\d upload_sessions

# Expected: session_id, tenant_id, user_id, filename, total_size_bytes, ...

# Exit psql
\q
```

---

## Step 5: Seed Test Data (Optional)

Create test tenant, user, and documents for testing:

```bash
# Run seed script
python scripts/seed_documents.py

# Expected output:
#   ✓ Created test tenant: test-tenant (ID: 1)
#   ✓ Created test user: test@example.com (ID: 1)
#   ✓ Seeding complete!
```

**Verify Seeded Data**:

```bash
psql postgresql://agenti_user:agenti_user@localhost:5436/agenticomni -c "SELECT tenant_id, name, domain FROM tenants;"

# Expected:
#  tenant_id |    name     |   domain
# -----------+-------------+-----------
#          1 | Test Tenant | test-tenant
```

---

## Step 6: Start Dramatiq Worker

Open a **new terminal window** and start the background processing worker:

```bash
# Navigate to project directory
cd /Users/william.jiang/my-apps/ai-edocuments

# Activate virtual environment
source venv/bin/activate

# Start Dramatiq worker with auto-reload (development mode)
dramatiq src.ingestion_parsing.tasks.document_tasks --watch src --processes 2 --threads 4

# Expected output:
#  [INFO] Dramatiq broker: redis://localhost:6379/1
#  [INFO] Worker started with 2 processes, 4 threads
#  [INFO] Watching for changes in: src/
#  [INFO] Registered actors: parse_document, generate_embeddings
```

**Leave this terminal running**. The worker will process document parsing jobs in the background.

**Troubleshooting**:

```bash
# If worker fails to start, check Redis connection
redis-cli -h localhost -p 6379 ping

# Expected: PONG

# Check for Python errors
python -c "from src.ingestion_parsing.tasks.document_tasks import parse_document; print('Tasks OK')"
```

---

## Step 7: Start FastAPI Server

In **another terminal window**, start (or restart) the FastAPI server:

```bash
# Navigate to project directory
cd /Users/william.jiang/my-apps/ai-edocuments

# Activate virtual environment
source venv/bin/activate

# Start server with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
#  INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
#  INFO: Started reloader process
#  INFO: Started server process
#  INFO: Waiting for application startup.
#  INFO: Application startup complete.
```

**Verify API is running**:

```bash
curl http://localhost:8000/api/v1/health

# Expected:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-09T...",
#   "version": "0.1.0",
#   "checks": {
#     "database": {"status": "healthy", "response_time_ms": 5},
#     "redis": {"status": "healthy", "response_time_ms": 2}
#   }
# }
```

---

## Step 8: Test Document Upload

Now test uploading a document through the API:

### 8.1: Prepare Test Document

```bash
# Create sample test documents directory
mkdir -p tests/fixtures/sample_documents

# Create a simple text document
echo "This is a test document for AgenticOmni parsing system." > tests/fixtures/sample_documents/test.txt

# Verify
cat tests/fixtures/sample_documents/test.txt
```

**Or download sample PDF**:

```bash
curl -o tests/fixtures/sample_documents/sample.pdf https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

### 8.2: Upload Document via API

```bash
# Upload the test document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer test-token-replace-with-real-token" \
  -F "file=@tests/fixtures/sample_documents/test.txt" \
  -F "title=Test Document" \
  -F "metadata={\"tags\":[\"test\",\"sample\"]}"

# Expected response:
# {
#   "document_id": 1,
#   "job_id": 1,
#   "status": "parsing",
#   "filename": "doc_20260109_abc123.txt",
#   "message": "Document uploaded successfully and queued for processing"
# }
```

**Note**: For this test, authentication might be simplified or bypassed during development. Update the `Authorization` header with a valid JWT token for production testing.

### 8.3: Check Processing Status

```bash
# Get job status (replace 1 with actual job_id from upload response)
curl http://localhost:8000/api/v1/processing/jobs/1 \
  -H "Authorization: Bearer test-token"

# Expected response (initial):
# {
#   "job_id": 1,
#   "document_id": 1,
#   "job_type": "parse_document",
#   "status": "processing",
#   "progress_percent": 45.0,
#   "estimated_time_remaining": 30,
#   "retry_count": 0,
#   "max_retries": 3,
#   "created_at": "2026-01-09T10:30:00Z",
#   ...
# }

# Wait a few seconds and check again
sleep 5
curl http://localhost:8000/api/v1/processing/jobs/1 \
  -H "Authorization: Bearer test-token"

# Expected response (completed):
# {
#   "job_id": 1,
#   "status": "completed",
#   "progress_percent": 100.0,
#   "completed_at": "2026-01-09T10:30:45Z",
#   ...
# }
```

### 8.4: Verify Document Parsed

```bash
# Get document details
curl http://localhost:8000/api/v1/documents/1 \
  -H "Authorization: Bearer test-token"

# Expected response:
# {
#   "document_id": 1,
#   "filename": "Test Document",
#   "file_type": "txt",
#   "processing_status": "parsed",
#   "chunk_count": 1,
#   "language": "en",
#   ...
# }
```

### 8.5: View Document Chunks

```bash
# Get parsed chunks
curl http://localhost:8000/api/v1/documents/1/chunks \
  -H "Authorization: Bearer test-token"

# Expected response:
# {
#   "total": 1,
#   "page": 1,
#   "limit": 20,
#   "chunks": [
#     {
#       "chunk_id": 1,
#       "chunk_order": 0,
#       "chunk_type": "text",
#       "content_text": "This is a test document for AgenticOmni parsing system.",
#       "token_count": 11,
#       "has_embedding": true,
#       ...
#     }
#   ]
# }
```

---

## Step 9: Test Batch Upload (Optional)

Test uploading multiple documents at once:

```bash
# Create additional test files
echo "Document 2 content" > tests/fixtures/sample_documents/doc2.txt
echo "Document 3 content" > tests/fixtures/sample_documents/doc3.txt

# Batch upload
curl -X POST http://localhost:8000/api/v1/documents/batch-upload \
  -H "Authorization: Bearer test-token" \
  -F "files=@tests/fixtures/sample_documents/doc2.txt" \
  -F "files=@tests/fixtures/sample_documents/doc3.txt"

# Expected response:
# {
#   "total": 2,
#   "successful": 2,
#   "failed": 0,
#   "uploads": [
#     {"filename": "doc2.txt", "status": "success", "document_id": 2, "job_id": 2},
#     {"filename": "doc3.txt", "status": "success", "document_id": 3, "job_id": 3}
#   ]
# }

# Check worker logs to see parsing jobs
# (Switch to terminal with Dramatiq worker running)
# Expected logs:
#   [INFO] Actor parse_document received message ...
#   [INFO] Parsing document ID: 2
#   [INFO] Successfully parsed document ID: 2 (1 chunks)
```

---

## Step 10: Test API Documentation

Explore the auto-generated API documentation:

```bash
# Open Swagger UI in browser
open http://localhost:8000/api/v1/docs

# Or ReDoc
open http://localhost:8000/api/v1/redoc
```

**Test Endpoints via Swagger UI**:

1. Click "Authorize" button
2. Enter test JWT token
3. Try "POST /documents/upload" endpoint
4. Upload a file and see the response
5. Try "GET /documents" to list documents
6. Try "GET /processing/jobs/{job_id}" to check status

---

## Troubleshooting

### Issue: Upload fails with "File type not allowed"

**Solution**: Check `ALLOWED_FILE_TYPES` in `.env`:

```bash
# Should include: pdf,docx,txt
grep ALLOWED_FILE_TYPES .env
```

### Issue: Worker not processing jobs

**Symptoms**: Job status stays in "pending"

**Solutions**:

1. Check worker is running:
   ```bash
   ps aux | grep dramatiq
   ```

2. Check Redis connection:
   ```bash
   redis-cli -h localhost -p 6379 llen dramatiq:default
   # Expected: number of pending jobs
   ```

3. Check worker logs for errors

4. Restart worker:
   ```bash
   # Stop: Ctrl+C in worker terminal
   # Start: dramatiq src.ingestion_parsing.tasks.document_tasks --watch src
   ```

### Issue: Parser fails with "Module not found"

**Symptoms**: Job status is "failed" with error "No module named 'docling'"

**Solution**: Install dependencies in correct virtual environment:

```bash
# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install docling python-docx python-magic
```

### Issue: Upload exceeds quota

**Symptoms**: `507 Quota Exceeded` error

**Solution**: Increase tenant storage quota:

```bash
psql postgresql://agenti_user:agenti_user@localhost:5436/agenticomni

UPDATE tenants SET storage_quota_bytes = 107374182400 WHERE tenant_id = 1;  -- 100GB

\q
```

### Issue: Malware scan fails

**Symptoms**: Upload fails with "Malware scanning error"

**Solution**: Disable ClamAV if not installed:

```bash
# Edit .env
ENABLE_MALWARE_SCANNING=false
```

---

## Development Workflow

### Typical Development Cycle

1. **Make code changes** in `src/ingestion_parsing/`
2. **Dramatiq auto-reloads** (if using `--watch` flag)
3. **FastAPI auto-reloads** (if using `--reload` flag)
4. **Test via curl** or Swagger UI
5. **Check logs** in terminal windows
6. **Repeat**

### Testing New Parsers

To test a new document parser:

```bash
# Add parser in src/ingestion_parsing/parsers/my_parser.py
# Register in parser_factory.py

# Test directly (without full upload flow)
python -c "
from src.ingestion_parsing.parsers.my_parser import MyParser
parser = MyParser()
result = parser.parse('tests/fixtures/sample.ext')
print(result)
"

# Upload test file via API and check results
```

### Monitoring Job Queue

Check Redis job queue status:

```bash
# View pending jobs
redis-cli -h localhost -p 6379 llen dramatiq:default

# View all queues
redis-cli -h localhost -p 6379 keys 'dramatiq:*'

# Monitor in real-time
redis-cli -h localhost -p 6379 MONITOR
```

### Database Inspection

Check document processing status:

```bash
psql postgresql://agenti_user:agenti_user@localhost:5436/agenticomni

-- View documents
SELECT document_id, filename, processing_status, created_at FROM documents;

-- View jobs
SELECT job_id, document_id, job_type, status, progress_percent FROM processing_jobs;

-- View chunks
SELECT chunk_id, document_id, chunk_type, LENGTH(content_text) as text_length FROM document_chunks;

\q
```

---

## Manual Parser Testing Script

For rapid parser iteration without full API upload:

```bash
# Create test script
cat > scripts/test_parsers.py << 'EOF'
#!/usr/bin/env python3
"""Test document parsers directly without API upload."""
import sys
from pathlib import Path
from src.ingestion_parsing.parsers.parser_factory import ParserFactory

def test_parser(file_path: str) -> None:
    """Test parsing a file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Testing parser for: {path.name}")
    print(f"File size: {path.stat().st_size} bytes")
    
    factory = ParserFactory()
    parser = factory.get_parser(str(path))
    
    print(f"Selected parser: {parser.__class__.__name__}")
    
    result = parser.parse(str(path))
    
    print(f"\nParsing Results:")
    print(f"  Text length: {len(result.text)} characters")
    print(f"  Chunks: {len(result.chunks)}")
    print(f"  Language: {result.language}")
    print(f"  Page count: {result.page_count}")
    print(f"\nFirst 200 characters:")
    print(result.text[:200])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/test_parsers.py <file_path>")
        sys.exit(1)
    test_parser(sys.argv[1])
EOF

# Make executable
chmod +x scripts/test_parsers.py

# Test
./scripts/test_parsers.py tests/fixtures/sample_documents/test.txt
```

---

## Step 10: Resumable Uploads for Large Files

For files larger than 50MB, use the resumable upload API that supports chunked uploads and can resume after network interruptions.

### 10.1 Initialize Resumable Upload Session

```bash
# Create a resumable upload session
curl -X POST http://localhost:8000/api/v1/documents/upload/resumable \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "large_video.mp4",
    "file_size": 500000000,
    "tenant_id": 1,
    "user_id": 1,
    "chunk_size": 10000000
  }'
```

**Expected Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "large_video.mp4",
  "file_size": 500000000,
  "chunk_size": 10000000,
  "total_chunks": 50,
  "uploaded_bytes": 0,
  "status": "pending",
  "upload_url": "/api/v1/documents/upload/resumable/550e8400-e29b-41d4-a716-446655440000",
  "expires_at": "2026-01-10T10:00:00Z",
  "created_at": "2026-01-09T10:00:00Z"
}
```

### 10.2 Upload Chunks

```bash
# Save session_id
SESSION_ID="550e8400-e29b-41d4-a716-446655440000"

# Split file into chunks (example using dd command)
FILE="large_video.mp4"
CHUNK_SIZE=10000000  # 10MB

# Upload first chunk (bytes 0-9999999)
curl -X PATCH "http://localhost:8000/api/v1/documents/upload/resumable/$SESSION_ID" \
  -H "Content-Range: bytes 0-9999999/500000000" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@chunk_0.bin"

# Expected Response:
# {
#   "session_id": "550e8400-e29b-41d4-a716-446655440000",
#   "uploaded_bytes": 10000000,
#   "total_bytes": 500000000,
#   "progress_percent": 2.0,
#   "status": "uploading"
# }

# Upload second chunk (bytes 10000000-19999999)
curl -X PATCH "http://localhost:8000/api/v1/documents/upload/resumable/$SESSION_ID" \
  -H "Content-Range: bytes 10000000-19999999/500000000" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@chunk_1.bin"
```

### 10.3 Check Upload Progress

```bash
# Check session progress
curl "http://localhost:8000/api/v1/documents/upload/resumable/$SESSION_ID"
```

**Expected Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "large_video.mp4",
  "file_size": 500000000,
  "chunk_size": 10000000,
  "total_chunks": 50,
  "uploaded_bytes": 20000000,
  "status": "uploading",
  "upload_url": "/api/v1/documents/upload/resumable/550e8400-e29b-41d4-a716-446655440000",
  "expires_at": "2026-01-10T10:00:00Z",
  "created_at": "2026-01-09T10:00:00Z"
}
```

### 10.4 Complete Upload

After the last chunk is uploaded, the system automatically:
1. Merges all chunks into a single file
2. Validates file integrity
3. Creates document record
4. Triggers parsing job

**Response after last chunk**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded_bytes": 500000000,
  "total_bytes": 500000000,
  "progress_percent": 100.0,
  "status": "complete",
  "document_id": 123,
  "job_id": 456
}
```

### 10.5 Cancel Upload (Optional)

```bash
# Cancel an upload session
curl -X DELETE "http://localhost:8000/api/v1/documents/upload/resumable/$SESSION_ID"
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Upload session cancelled and cleaned up"
}
```

### 10.6 Python Script for Resumable Upload

Create a helper script for uploading large files:

```python
# scripts/resumable_upload.py
import requests
import os
import math

def upload_file_resumable(file_path: str, tenant_id: int, user_id: int) -> dict:
    """Upload a large file using resumable upload API."""
    
    # Configuration
    API_BASE = "http://localhost:8000/api/v1"
    CHUNK_SIZE = 10_000_000  # 10MB chunks
    
    # Get file info
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    
    print(f"📁 Uploading: {filename} ({file_size:,} bytes)")
    
    # Step 1: Initialize session
    print("🔄 Initializing upload session...")
    response = requests.post(
        f"{API_BASE}/documents/upload/resumable",
        json={
            "filename": filename,
            "file_size": file_size,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "chunk_size": CHUNK_SIZE,
        },
    )
    response.raise_for_status()
    session = response.json()
    session_id = session["session_id"]
    total_chunks = session["total_chunks"]
    
    print(f"✅ Session created: {session_id}")
    print(f"📦 Total chunks: {total_chunks}")
    
    # Step 2: Upload chunks
    with open(file_path, "rb") as f:
        for chunk_num in range(total_chunks):
            start = chunk_num * CHUNK_SIZE
            end = min(start + CHUNK_SIZE, file_size) - 1
            
            # Read chunk
            f.seek(start)
            chunk_data = f.read(CHUNK_SIZE)
            
            # Upload chunk
            print(f"⬆️  Uploading chunk {chunk_num + 1}/{total_chunks}...", end=" ")
            response = requests.patch(
                f"{API_BASE}/documents/upload/resumable/{session_id}",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Content-Type": "application/octet-stream",
                },
                data=chunk_data,
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"{result['progress_percent']:.1f}% complete")
    
    print("✅ Upload complete!")
    print(f"📄 Document ID: {result.get('document_id')}")
    print(f"⚙️  Job ID: {result.get('job_id')}")
    
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scripts/resumable_upload.py <file_path>")
        sys.exit(1)
    
    result = upload_file_resumable(
        file_path=sys.argv[1],
        tenant_id=1,
        user_id=1,
    )
```

**Usage**:
```bash
# Upload a large file
python scripts/resumable_upload.py /path/to/large_file.mp4
```

### 10.7 Resumable Upload Features

| Feature | Description |
|---------|-------------|
| **Max File Size** | 5GB per file |
| **Chunk Size** | Configurable: 1MB - 100MB (default: 5MB) |
| **Session Expiry** | 24 hours |
| **Resume Support** | Can resume from last uploaded chunk |
| **Integrity Check** | SHA-256 hash validation (optional) |
| **Auto-merge** | Automatic merging when complete |
| **Progress Tracking** | Byte-level progress (0-100%) |

### 10.8 Best Practices

**Chunk Size Selection**:
- **Fast Network**: 10-50MB chunks
- **Slow Network**: 1-5MB chunks
- **Mobile/Unstable**: 1-2MB chunks

**Error Handling**:
```python
import time

def upload_chunk_with_retry(session_id, chunk_data, start, end, total_size, max_retries=3):
    """Upload a chunk with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            response = requests.patch(
                f"{API_BASE}/documents/upload/resumable/{session_id}",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{total_size}",
                    "Content-Type": "application/octet-stream",
                },
                data=chunk_data,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"❌ Upload failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

---

## Next Steps

After completing this quickstart:

1. **Frontend Integration**: Build upload UI in Next.js frontend (see `frontend/` directory)
2. **Embedding Generation**: Implement vector embeddings for chunks (see `rag_orchestration/` module)
3. **RAG Queries**: Connect parsed documents to RAG query endpoints
4. **Production Deployment**: Configure S3 storage, ClamAV, monitoring

**See Also**:
- [API Contracts](./contracts/) - OpenAPI specifications
- [Data Model](./data-model.md) - Database schema
- [Research](./research.md) - Technology decisions
- [Implementation Plan](./plan.md) - Full technical plan

---

## Getting Help

**Common Issues**: See [Troubleshooting](#troubleshooting) section above

**Logs**:
- FastAPI: Terminal running `uvicorn`
- Dramatiq Worker: Terminal running `dramatiq`
- Database: `docker-compose logs postgres`
- Redis: `docker-compose logs redis`

**Questions**: Contact development team or create an issue

---

**Status**: ✅ Quickstart guide complete  
**Last Updated**: 2026-01-09  
**Tested On**: macOS 14+, Python 3.12
