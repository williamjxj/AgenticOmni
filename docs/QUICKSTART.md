# Quick Start Guide - Running the Application

**Last Updated**: 2026-01-11

This guide will help you start both the backend API server and the frontend.

---

## 🚀 Quick Start (2 Minutes)

### Terminal 1: Start Backend API

```bash
# Navigate to project root
cd /Users/william.jiang/my-apps/ai-edocuments

# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the FastAPI server
./scripts/run_dev.sh
```

**Expected Output**:
```
=======================================================================
AgenticOmni Development Server
=======================================================================

Starting FastAPI server...
  - Host: 0.0.0.0
  - Port: 8000
  - Environment: development
  - Log Level: INFO

📚 API Documentation: http://localhost:8000/api/v1/docs
🔍 ReDoc: http://localhost:8000/api/v1/redoc

Press Ctrl+C to stop the server
=======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Terminal 2: Start Frontend

```bash
# Open a NEW terminal window/tab

# Navigate to frontend directory
cd /Users/william.jiang/my-apps/ai-edocuments/frontend

# Install dependencies (first time only)
npm install

# Start Next.js development server
npm run dev
```

**Expected Output**:
```
   ▲ Next.js 16.1.1
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 2.1s
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 📋 Prerequisites

Before starting, ensure you have:

### Required Services

1. **PostgreSQL Database** (running)
   ```bash
   # Check if PostgreSQL is running
   pg_isready
   
   # If not running, start it (macOS with Homebrew)
   brew services start postgresql@14
   ```

2. **Redis** (running)
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return: PONG
   
   # If not running, start it
   brew services start redis
   ```

### Python Environment

```bash
# Check Python version (should be 3.12+)
python --version

# Activate virtual environment
cd /Users/william.jiang/my-apps/ai-edocuments
source venv/bin/activate

# Verify dependencies are installed
pip list | grep fastapi
pip list | grep sqlalchemy
```

### Node.js Environment

```bash
# Check Node.js version (should be 18+)
node --version

# Check npm
npm --version
```

---

## 🔧 Detailed Setup (First Time)

If this is your first time running the application, follow these steps:

### 1. Database Setup

```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Run database migrations
alembic upgrade head

# Verify pgvector extension
python scripts/verify_pgvector.py
```

### 2. Download ML Models (Optional - for OCR)

```bash
# Download embedding models (if using search)
python scripts/download_models.py
```

### 3. Environment Variables

The `.env` file already exists. Verify it has the necessary settings:

```bash
# Check key settings
cat .env | grep -E "DATABASE_URL|REDIS_URL|API_HOST|API_PORT"
```

**Key Variables**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agenticomni

# Redis
REDIS_URL=redis://localhost:6379/0

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (if needed)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Frontend Environment

```bash
cd frontend

# Create .env.local (if needed)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

---

## 🐳 Alternative: Using Docker Compose

If you prefer Docker, you can start all services at once:

```bash
cd /Users/william.jiang/my-apps/ai-edocuments

# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Services with Docker**:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 🧪 Verify Everything Works

### 1. Backend Health Check

```bash
# Using curl
curl http://localhost:8000/api/v1/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-01-11T...",
  "database": "connected",
  "redis": "connected"
}
```

### 2. Frontend Access

Open browser to http://localhost:3000

**You should see**:
- New customer-focused homepage
- "Upload Documents" button
- "Search Documents" button
- Clean, modern UI

### 3. API Documentation

Open browser to http://localhost:8000/api/v1/docs

**You should see**:
- Swagger UI with all API endpoints
- Try out endpoints interactively

---

## 📝 Common Commands

### Backend Server

```bash
# Start development server (with hot-reload)
./scripts/run_dev.sh

# Start production server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Run with specific log level
uvicorn src.api.main:app --log-level debug

# Run tests
pytest tests/

# Run specific test file
pytest tests/unit/test_ocr_service.py -v
```

### Frontend

```bash
cd frontend

# Development server (hot-reload)
npm run dev

# Production build
npm run build
npm run start

# Linting
npm run lint
```

### Database

```bash
# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# Check current version
alembic current

# View migration history
alembic history
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Reinstall dependencies
pip install -e .
```

**Problem**: Database connection error
```bash
# Solution: Check PostgreSQL is running
pg_isready
brew services start postgresql@14

# Verify database exists
psql -l | grep agenticomni

# Create database if missing
createdb agenticomni
```

**Problem**: Redis connection error
```bash
# Solution: Start Redis
brew services start redis

# Verify Redis is running
redis-cli ping
```

### Frontend Won't Start

**Problem**: `EADDRINUSE: address already in use`
```bash
# Solution: Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

**Problem**: `Module not found`
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Problem**: API calls failing (CORS error)
```bash
# Solution: Verify backend is running
curl http://localhost:8000/api/v1/health

# Check frontend .env.local
cat frontend/.env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Migrations

**Problem**: Migration fails
```bash
# Solution: Check current version
alembic current

# Rollback and retry
alembic downgrade -1
alembic upgrade head

# If stuck, reset migrations (⚠️ DESTROYS DATA)
alembic downgrade base
alembic upgrade head
```

---

## 📊 Port Usage

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| API Docs | 8000 | http://localhost:8000/api/v1/docs |

---

## 🎯 Typical Development Workflow

### Daily Startup

1. **Terminal 1**: Start backend
   ```bash
   cd /Users/william.jiang/my-apps/ai-edocuments
   source venv/bin/activate
   ./scripts/run_dev.sh
   ```

2. **Terminal 2**: Start frontend
   ```bash
   cd /Users/william.jiang/my-apps/ai-edocuments/frontend
   npm run dev
   ```

3. **Browser**: Open http://localhost:3000

### Making Changes

- **Backend changes**: Server auto-reloads (FastAPI's `--reload` flag)
- **Frontend changes**: Page auto-refreshes (Next.js hot-reload)
- **Database changes**: Run `alembic revision --autogenerate`, then `alembic upgrade head`

### Before Committing

```bash
# Format code
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Run tests
pytest tests/

# Frontend lint
cd frontend && npm run lint
```

---

## 🚀 Production Deployment

For production, see:
- `docs/PRODUCTION_DEPLOY.md` - Full deployment guide
- `docker-compose.yml` - Docker configuration
- `.env.example` - Environment variable template

**Quick production start**:
```bash
# Build and start with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or use uvicorn without reload
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📞 Need Help?

- **API Issues**: Check http://localhost:8000/api/v1/docs
- **Database Issues**: Check `docs/ENV_CONFIGURATION.md`
- **Markdown Workflow**: See `docs/MARKDOWN_WORKFLOW_GUIDE.md`
- **OCR Setup**: See `docs/OCR_MVP_COMPLETION.md`

---

## ✅ Quick Checklist

Before starting development:

- [ ] PostgreSQL running (`pg_isready`)
- [ ] Redis running (`redis-cli ping`)
- [ ] Python venv activated (`which python`)
- [ ] Dependencies installed (`pip list | grep fastapi`)
- [ ] Migrations applied (`alembic current`)
- [ ] .env file exists and configured
- [ ] Backend starts successfully (http://localhost:8000/api/v1/health)
- [ ] Frontend starts successfully (http://localhost:3000)

---

**Status**: Ready to develop! 🎉

Both services should now be running:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
