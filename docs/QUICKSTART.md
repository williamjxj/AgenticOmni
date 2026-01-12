# Quick Start Guide

**Last Updated**: 2026-01-12  
**Status**: ✅ Ready for Development

This guide will help you get the AgenticOmni application up and running in minutes.

---

## 🚀 Quick Start (2 Minutes)

### Prerequisites Check

```bash
# Check required services
docker-compose ps                    # PostgreSQL, Redis should be running
ollama list                          # Ollama with nomic-embed-text:latest
python --version                     # Python 3.12+
node --version                       # Node.js 18+
```

### Start Services

**Terminal 1 - Backend API:**
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
ollama serve                         # Start Ollama server
ollama pull nomic-embed-text:latest  # Pull embedding model (first time)
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main application |
| **Upload Page** | http://localhost:3000/upload | Upload documents |
| **Search Page** | http://localhost:3000/search | Semantic search |
| **Documents** | http://localhost:3000/documents | View all documents |
| **API Docs** | http://localhost:8000/api/v1/docs | Swagger UI |
| **Health Check** | http://localhost:8000/api/v1/health | API status |

---

## ⚡ Quick Commands

```bash
# Database Management
./scripts/check_db_status.sh         # Check database status
./scripts/reset_databases.sh         # Reset to clean state

# Embedding Generation
source venv/bin/activate
python scripts/generate_embeddings.py

# Start All Services
./scripts/start_all.sh               # Show startup instructions
```

---

## 🎯 Complete Workflow

### 1. Upload Markdown Files

**Via Web UI:**
1. Visit http://localhost:3000/upload
2. Drag & drop `.md` or `.markdown` files
3. Wait for processing (auto-redirects when complete)

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@your-document.md" \
  -F "tenant_id=1" \
  -F "user_id=1"
```

### 2. Generate Embeddings

```bash
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate
python scripts/generate_embeddings.py

# Or filter by tenant
python scripts/generate_embeddings.py --tenant-id 1
```

### 3. Search Documents

**Web UI:**
- Visit http://localhost:3000/search
- Enter your query
- View ranked search results

**API:**
```bash
curl "http://localhost:8000/api/v1/search?tenant_id=1&query=database+migration&limit=5"
```

---

## 📋 First-Time Setup

### 1. Install Dependencies

```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Python dependencies
python -m venv venv
source venv/bin/activate
pip install -e .

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Start Docker Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services
docker-compose ps
```

### 3. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Verify pgvector extension
python scripts/verify_pgvector.py
```

### 4. Configure Environment

```bash
# Verify .env file exists
cat .env | grep -E "DATABASE_URL|REDIS_URL|CORS_ORIGINS"
```

### 5. Download ML Models

```bash
# Install Ollama (macOS)
brew install ollama

# Pull embedding model
ollama pull nomic-embed-text:latest
```

---

## ✅ Pre-Flight Checklist

- [ ] PostgreSQL running (port 5436)
- [ ] Redis running (port 6380)
- [ ] Ollama running (port 11434)
- [ ] nomic-embed-text model pulled
- [ ] Python venv activated
- [ ] Dependencies installed
- [ ] Migrations applied
- [ ] .env file configured
- [ ] Backend starts successfully
- [ ] Frontend starts successfully

---

## 📊 Status Checks

```bash
# Docker services
docker-compose ps

# Database status
./scripts/check_db_status.sh

# API health
curl http://localhost:8000/api/v1/health

# Ollama models
curl http://localhost:11434/api/tags
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Problem**: Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps
docker-compose logs postgres
```

### Frontend Won't Start

**Problem**: `EADDRINUSE`
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Upload Fails

- Check file extension is `.md` or `.markdown`
- Verify file size < 100MB
- Check backend logs

### Search Returns Nothing

- Run: `python scripts/generate_embeddings.py`
- Verify Ollama is running
- Check embeddings exist

---

## 🎯 What Works Now

| Feature | Status |
|---------|--------|
| Upload Markdown | ✅ Working |
| Parse & Chunk | ✅ Automatic |
| Generate Embeddings | ⚠️ Manual script |
| Semantic Search | ✅ Working |
| View Documents | ✅ Working |

---

## 📞 Need Help?

- **Setup Issues**: See [environment.md](./environment.md)
- **Implementation**: See [implementation.md](./implementation.md)
- **Production**: See [production.md](./production.md)

---

**Status**: Ready to develop! 🎉
