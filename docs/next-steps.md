# Next Steps: Upload Markdown → RAG → Search → Chat

**Date**: 2026-01-11  
**Status**: Database reset complete, ready for fresh start

This guide walks you through the complete workflow from uploading markdown files to searching and chatting with your documents.

---

## 🎯 What's Currently Working

✅ **Phase 1: Document Upload & Processing**
- Upload markdown files (.md, .markdown)
- Parse markdown content with structure preservation
- Extract metadata (headings, code blocks, links, tables)
- Create RAG-optimized chunks (512 tokens, 50 overlap)
- Store in PostgreSQL with pgvector

✅ **Phase 2: OCR Pipeline**
- OCR text extraction (PaddleOCR/Tesseract)
- Multi-language support (EN, ZH, JA, KO, etc.)
- Confidence scoring

✅ **Phase 3: Search Infrastructure**
- Search API endpoints (`/api/v1/search/semantic`)
- Embedding service (Ollama/OpenAI)
- Search frontend UI

⚠️ **What Needs Setup**
- Embedding generation (configured but not automated)
- Ollama embedding server (needs to be running)
- Chat interface (not yet implemented)

---

## 🚀 Quick Start Workflow

### Step 1: Start All Services

#### Terminal 1: Start Docker Services
```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Start PostgreSQL and Redis (already running after reset)
docker-compose ps

# If not running:
# docker-compose up -d postgres redis
```

#### Terminal 2: Start Ollama for Embeddings
```bash
# Install Ollama if not already installed
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# In another terminal, pull the embedding model
ollama pull nomic-embed-text:latest
```

#### Terminal 3: Start Backend API
```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
./scripts/run_dev.sh
```

**Expected output:**
```
🚀 FastAPI running on http://localhost:8000
📚 API Docs: http://localhost:8000/api/v1/docs
```

#### Terminal 4: Start Frontend
```bash
cd /Users/william.jiang/my-apps/ai-edocuments/frontend

# Install dependencies (first time only)
npm install

# Start Next.js dev server
npm run dev
```

**Expected output:**
```
▲ Next.js 16.1.1
- Local:        http://localhost:3000
✓ Ready in 2.1s
```

---

### Step 2: Upload Markdown Files

#### Option A: Using the Web UI (Recommended)

1. **Visit Upload Page**: http://localhost:3000/upload

2. **Upload Files**:
   - Drag and drop markdown files OR click to browse
   - Supports single files or multiple files
   - Accepts `.md` and `.markdown` files

3. **Monitor Progress**:
   - Watch real-time progress (0-100%)
   - See parsing status updates
   - Files automatically redirect to documents page when complete

#### Option B: Using API (cURL)

```bash
# Upload a single markdown file
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@path/to/your/document.md"

# Response includes document_id and job_id
```

#### Option C: Upload Test Documents

```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Upload sample markdown files
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@tests/fixtures/sample_documents/sample.md"

curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@tests/fixtures/sample_documents/with_frontmatter.md"
```

---

### Step 3: Verify Documents Were Processed

```bash
# Check database status
./scripts/check_db_status.sh

# Expected output:
# Documents: 2
# Chunks: 10-20 (depends on document size)
# Jobs: 2 (status: completed)
```

**Via API:**
```bash
# List all documents
curl "http://localhost:8000/api/v1/documents?tenant_id=1&page=1&limit=20"

# Get specific document details
curl "http://localhost:8000/api/v1/documents/1?tenant_id=1"
```

**Via Web UI:**
- Visit: http://localhost:3000/documents
- Should see your uploaded markdown files with "✓ Ready to Search" status

---

### Step 4: Generate Embeddings (MANUAL STEP - AUTOMATION COMING)

**Current State**: Chunks are created but embeddings are not automatically generated.

**Manual Embedding Generation Script:**

Create a helper script to generate embeddings for all chunks:

```bash
# Generate embeddings for all chunks
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate
python scripts/generate_embeddings.py

# Or filter by tenant ID
python scripts/generate_embeddings.py --tenant-id 1

# Check help for more options
python scripts/generate_embeddings.py --help
```

**Verify Embeddings:**
```bash
# Check if embeddings were created
docker-compose exec -T postgres psql -U agenti_user -d agenticomni -c \
  "SELECT COUNT(*) as chunks_with_embeddings FROM document_chunks WHERE embedding IS NOT NULL;"
```

---

### Step 5: Search Your Documents

#### Via Web UI (Recommended)

1. **Visit Search Page**: http://localhost:3000/search

2. **Enter Search Query**:
   - Type natural language query: "What is the main topic of this document?"
   - Or keyword search: "installation steps"
   - Supports English and Chinese

3. **View Results**:
   - Results ranked by relevance (similarity score)
   - Document snippets with highlighting
   - Click to view full document

#### Via API

```bash
# Semantic search
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "How to install the application?",
    "tenant_id": 1,
    "top_k": 5,
    "language": "en"
  }'
```

**Response:**
```json
{
  "query_id": "uuid-here",
  "results": [
    {
      "chunk_id": 1,
      "document_id": 1,
      "content": "Installation steps...",
      "similarity_score": 0.89,
      "metadata": {...}
    }
  ],
  "total_results": 5,
  "search_duration_ms": 45
}
```

---

### Step 6: Chat Interface (COMING SOON)

**Status**: Not yet implemented. Planned for next phase.

**What's Needed**:
1. RAG orchestration service to combine search + LLM
2. Chat API endpoint (`/api/v1/chat`)
3. Chat UI component in frontend
4. DeepSeek LLM integration (already configured in .env)

**Temporary Workaround**:
Use the search API to get relevant chunks, then manually query DeepSeek/ChatGPT with the context.

---

## 🔧 Troubleshooting

### Problem: Upload fails with "Unknown MIME type"

**Solution:**
```bash
# Check if file is actually markdown
file your_document.md

# Should show: "text/plain" or "text/markdown"

# If it's a different type, rename with .md extension
mv document.txt document.md
```

### Problem: Embeddings not generated

**Check Ollama is running:**
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Should return list of models including nomic-embed-text
```

**Pull model if missing:**
```bash
ollama pull nomic-embed-text:latest
```

### Problem: Search returns no results

**Verify embeddings exist:**
```bash
./scripts/check_db_status.sh

# Check if chunks have embeddings
docker-compose exec -T postgres psql -U agenti_user -d agenticomni -c \
  "SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;"
```

**If 0, run embedding generation script from Step 4**

### Problem: Frontend can't connect to backend

**Check CORS settings:**
```bash
# In .env, verify:
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Restart backend after changing .env
```

---

## 📊 Monitor Your System

### Quick Status Check
```bash
./scripts/check_db_status.sh
```

### Check Processing Jobs
```bash
# Get all jobs
curl "http://localhost:8000/api/v1/processing/jobs?tenant_id=1&limit=20"

# Get specific job
curl "http://localhost:8000/api/v1/processing/jobs/1?tenant_id=1"
```

### View Logs
```bash
# Backend logs (in terminal running ./scripts/run_dev.sh)
# Look for structured JSON logs

# Frontend logs (in terminal running npm run dev)
# Look for Next.js compilation and request logs
```

---

## 🎯 Complete End-to-End Example

```bash
# 1. Upload a markdown document
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@README.md")

DOC_ID=$(echo $RESPONSE | jq -r '.document_id')
echo "Uploaded document ID: $DOC_ID"

# 2. Wait for processing to complete (5-10 seconds)
sleep 10

# 3. Verify document was chunked
curl "http://localhost:8000/api/v1/documents/$DOC_ID?tenant_id=1" | jq

# 4. Generate embeddings (manual step - see Step 4)
python scripts/generate_embeddings.py

# 5. Search the document
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is AgenticOmni?",
    "tenant_id": 1,
    "top_k": 3
  }' | jq

# 6. View results in browser
open http://localhost:3000/search
```

---

## 📝 Summary: What Works Now

| Feature | Status | How to Use |
|---------|--------|------------|
| **Upload Markdown** | ✅ Working | Web UI or API |
| **Parse & Chunk** | ✅ Automatic | Happens after upload |
| **Store in DB** | ✅ Automatic | pgvector ready |
| **Generate Embeddings** | ⚠️ Manual | Run script (Step 4) |
| **Semantic Search** | ✅ Working | Web UI or API (after embeddings) |
| **Chat/RAG** | ❌ Not Ready | Coming in next phase |

---

## 🚧 What's Next (Development Roadmap)

### Immediate Tasks
1. **Automate Embedding Generation**
   - Add Dramatiq task to generate embeddings after chunking
   - Hook into document_tasks.py pipeline
   - Add progress tracking

2. **Improve Search UI**
   - Add result highlighting
   - Show document metadata
   - Add filters (by date, language, etc.)

3. **Implement Chat Interface**
   - Create RAG orchestration service
   - Add chat API endpoint
   - Build chat UI component
   - Integrate DeepSeek LLM

### Medium-Term
- Batch folder upload for markdown
- Mermaid diagram support
- Image reference extraction
- Multi-modal search

---

## ✅ Checklist: Ready to Upload & Search

Before starting, ensure:

- [ ] PostgreSQL running on port 5436 (healthy)
- [ ] Redis running on port 6380 (healthy)
- [ ] Ollama running on port 11434
- [ ] nomic-embed-text model pulled in Ollama
- [ ] Backend API running on port 8000
- [ ] Frontend running on port 3000
- [ ] Database tables empty (verified with check_db_status.sh)

**All green? You're ready to go!** 🚀

Start with Step 1 above.

---

**Need Help?**
- Check logs in backend terminal
- Visit API docs: http://localhost:8000/api/v1/docs
- Run status check: `./scripts/check_db_status.sh`
- Review error messages in frontend console (F12)
