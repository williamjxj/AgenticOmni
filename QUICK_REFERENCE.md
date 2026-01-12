# 🚀 Quick Reference Card

**Fresh Database Reset Complete** - Ready for upload, RAG, and search!

## 📍 Essential URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3000 | Main app |
| **Upload Page** | http://localhost:3000/upload | Upload markdown |
| **Search Page** | http://localhost:3000/search | Search documents |
| **Documents** | http://localhost:3000/documents | View uploaded files |
| **API Docs** | http://localhost:8000/api/v1/docs | Swagger UI |
| **Health Check** | http://localhost:8000/api/v1/health | API status |

## ⚡ Quick Commands

```bash
# Check database status
./scripts/check_db_status.sh

# Reset databases (clean slate)
./scripts/reset_databases.sh

# Generate embeddings for search
source venv/bin/activate
python scripts/generate_embeddings.py

# Start services (shows instructions)
./scripts/start_all.sh
```

## 🎯 Complete Workflow (3 Steps)

### 1️⃣ Start Services

**Terminal 1 - Backend:**
```bash
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate
./scripts/run_dev.sh
```

**Terminal 2 - Frontend:**
```bash
cd /Users/william.jiang/my-apps/ai-edocuments/frontend
npm run dev
```

**Terminal 3 - Ollama (for embeddings):**
```bash
# Install if needed: brew install ollama
ollama serve

# In another terminal, pull model:
ollama pull nomic-embed-text:latest
```

### 2️⃣ Upload Markdown Files

**Via Web UI:**
- Visit: http://localhost:3000/upload
- Drag & drop `.md` or `.markdown` files
- Wait for processing to complete (auto-redirects)

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@your-document.md"
```

### 3️⃣ Generate Embeddings & Search

**Generate embeddings:**
```bash
# Make sure you're in the project root
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate
python scripts/generate_embeddings.py

# Or filter by tenant
python scripts/generate_embeddings.py --tenant-id 1
```

**Search:**
- Web UI: http://localhost:3000/search
- Enter query: "What is the main topic?"
- View ranked results

## 📊 Status Checks

```bash
# Docker services
docker-compose ps

# Database counts
./scripts/check_db_status.sh

# API health
curl http://localhost:8000/api/v1/health

# Ollama
curl http://localhost:11434/api/tags
```

## ✅ Pre-Flight Checklist

Before starting work:

- [ ] PostgreSQL running (port 5436)
- [ ] Redis running (port 6380)
- [ ] Ollama running (port 11434)
- [ ] nomic-embed-text model pulled
- [ ] Backend API running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Virtual environment activated

**All green?** Start uploading! 🚀

## 🆘 Common Issues

**Upload fails:**
- Check file extension is `.md` or `.markdown`
- Verify file size < 100MB
- Check backend logs for errors

**Search returns nothing:**
- Run embedding generation: `python scripts/generate_embeddings.py`
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check embeddings exist: `./scripts/check_db_status.sh`

**Frontend can't connect:**
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS settings in `.env`: `CORS_ORIGINS=http://localhost:3000`
- Restart backend after .env changes

## 📚 Full Documentation

- **Complete Guide**: [docs/NEXT_STEPS_GUIDE.md](docs/NEXT_STEPS_GUIDE.md)
- **Implementation Status**: [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)
- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Environment Config**: [docs/ENV_CONFIGURATION.md](docs/ENV_CONFIGURATION.md)

## 🎯 What Works Now

| Feature | Status | Notes |
|---------|--------|-------|
| Upload Markdown | ✅ Working | .md, .markdown files |
| Parse & Chunk | ✅ Automatic | 512 tokens, 50 overlap |
| Store in DB | ✅ Automatic | pgvector ready |
| Generate Embeddings | ⚠️ Manual | Run script after upload |
| Semantic Search | ✅ Working | After embeddings |
| Chat/RAG | ❌ Not Ready | Coming in next phase |

---

**Last Updated**: 2026-01-11  
**Database Status**: Fresh reset, 0 documents
