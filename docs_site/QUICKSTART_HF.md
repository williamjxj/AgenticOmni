# HuggingFace Datasets - Quick Start Guide

## ✅ Integration Complete

All components are installed and tested. You can now import HuggingFace datasets into AgenticOmni!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the API Server

```bash
cd /Users/william.jiang/my-apps/ai-edocuments
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Import SQuAD Dataset (500 samples)

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

**Expected Response:**
```json
{
  "message": "Dataset import started. Processing 500 records from rajpurkar/squad.",
  "job_id": "abc123-def456",
  "dataset_name": "rajpurkar/squad",
  "split": "train",
  "limit": 500
}
```

### Step 3: Check Progress

Monitor in logs or query the database:
```sql
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5;
```

---

## 📋 What Was Installed

| Component | File | Description |
|-----------|------|-------------|
| **Package** | `requirements.txt` | `datasets==2.18.0` + token in `.env` |
| **Loader** | `src/ingestion_parsing/services/hf_dataset_loader.py` | Loads datasets from HF Hub |
| **Task** | `src/ingestion_parsing/tasks/hf_dataset_tasks.py` | Background processing with Dramatiq |
| **API** | `src/api/routes/datasets.py` | 3 endpoints (import, validate, list) |
| **Settings** | `config/settings.py` | `huggingface_token` configuration |

---

## 🔧 API Endpoints

### 1. Import Dataset
```bash
POST /api/v1/datasets/import
```

### 2. Validate Dataset
```bash
GET /api/v1/datasets/validate/rajpurkar%2Fsquad
```

### 3. List Supported Datasets
```bash
GET /api/v1/datasets/supported
```

**View Docs:** http://localhost:8000/api/v1/docs

---

## 🧪 Test the Integration

```bash
# Run the test suite
python test_hf_integration.py
```

**Expected Output:**
```
✓ All integration tests passed!
```

---

## 📊 How It Works

```
1. API receives import request
         ↓
2. Dramatiq task triggered (background)
         ↓
3. Load dataset from HuggingFace Hub
         ↓
4. Create document records in PostgreSQL
         ↓
5. Chunk text (512 tokens, 50 overlap)
         ↓
6. Store chunks in `document_chunks` table
         ↓
7. Trigger embedding generation
         ↓
8. Generate embeddings via Ollama
         ↓
9. Store in pgvector
         ↓
10. Ready for semantic search!
```

---

## 💡 Tips

- **Start small:** Use `limit: 100-500` for testing
- **Tenant ID:** Use `1` for default tenant
- **Deduplication:** Content hash prevents duplicates
- **Background job:** Import runs async, won't block API
- **Monitor logs:** Check `logs/app.log` for progress

---

## 🔍 Verify Import

Check the database after import:

```sql
-- View imported documents
SELECT document_id, filename, storage_path, document_metadata 
FROM documents 
WHERE storage_path LIKE 'hf://%';

-- Count chunks
SELECT COUNT(*) as chunk_count
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.document_id
WHERE d.storage_path LIKE 'hf://%';

-- Check embeddings
SELECT COUNT(*) as embedded_count
FROM document_chunks
WHERE embedding IS NOT NULL;
```

---

## 🎯 Example: Full Import Workflow

```bash
# 1. Validate access first
curl "http://localhost:8000/api/v1/datasets/validate/rajpurkar%2Fsquad"

# 2. Import dataset
curl -X POST "http://localhost:8000/api/v1/datasets/import" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "rajpurkar/squad",
    "tenant_id": 1,
    "split": "train",
    "limit": 500
  }'

# Save the job_id from response

# 3. Wait ~2-5 minutes for processing

# 4. Search imported content
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "university architecture",
    "tenant_id": 1,
    "limit": 5
  }'
```

---

## 📦 Supported Datasets

| Dataset | ID | Records | Recommended Limit |
|---------|----|---------|--------------------|
| SQuAD | `rajpurkar/squad` | 18K train | 500 |
| PubMed QA | `pubmed_qa` | 200K | 1000 |
| Natural Questions | `google-research-datasets/natural_questions` | 300K | 500 |
| WikiText | `wikitext` | ~100M tokens | 1000 |

---

## 🔗 Documentation

- **Full Guide:** `docs/huggingface-integration.md`
- **API Docs:** http://localhost:8000/api/v1/docs
- **HuggingFace:** https://huggingface.co/datasets

---

## ✨ Ready to Go!

Your integration is complete and tested. Start the server and try importing SQuAD!

```bash
uvicorn src.api.main:app --reload
```
