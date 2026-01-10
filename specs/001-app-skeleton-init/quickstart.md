# AgenticOmni Quickstart Guide

**Last Updated**: January 9, 2026  
**Target Audience**: New developers joining the AgenticOmni project  
**Expected Setup Time**: < 15 minutes

## Overview

This guide will help you set up your development environment for the AgenticOmni AI document intelligence platform. By the end of this guide, you'll have:

- ✅ All prerequisites installed (Python 3.12+, Node.js 18+, Docker)
- ✅ Local development database running (PostgreSQL + pgvector)
- ✅ Backend API server running with hot-reload
- ✅ Frontend development server running
- ✅ Ability to run tests and code quality checks

---

## Prerequisites

### Required Software

| Software | Minimum Version | Check Command | Installation |
|----------|----------------|---------------|--------------|
| **Python** | 3.12+ | `python --version` | [python.org](https://www.python.org/) or `brew install python@3.12` (macOS) |
| **Node.js** | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) or `brew install node` (macOS) |
| **npm** | 9+ | `npm --version` | Included with Node.js |
| **Docker** | 20+ | `docker --version` | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Docker Compose** | 2.0+ | `docker-compose --version` | Included with Docker Desktop |
| **Git** | 2.30+ | `git --version` | [git-scm.com](https://git-scm.com/) or `brew install git` (macOS) |

### Platform Support

- ✅ **macOS** 11+ (Big Sur or later)
- ✅ **Linux** (Ubuntu 20.04+, Fedora 35+, or equivalent)
- ✅ **Windows** with WSL2 (Ubuntu 20.04+ recommended)

**Note**: Native Windows (without WSL2) is not officially supported due to Docker networking differences.

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url> agenticomni
cd agenticomni

# Checkout the skeleton branch (if not on main)
git checkout 001-app-skeleton-init
```

---

## Step 2: Environment Configuration

### Create Environment File

Copy the example environment file and customize it:

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

### Required Environment Variables

Update `.env` with the following minimum configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://agenti_user:agenti_user@localhost:5436/agenticomni

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO

# Vector Configuration
VECTOR_DIMENSIONS=1536

# Security (generate a secure key for production)
SECRET_KEY=dev-secret-key-change-in-production
ENFORCE_TENANT_ISOLATION=true
```

**Security Note**: The default values are for development only. Change `SECRET_KEY` and database password before deploying to production.

---

## Step 3: Start Database Services

### Using Docker Compose (Recommended)

```bash
# Start PostgreSQL with pgvector and Redis
docker-compose up -d

# Verify services are healthy
docker-compose ps

# Expected output:
#   NAME                STATUS              PORTS
#   postgres            Up (healthy)        0.0.0.0:5436->5432/tcp
#   redis               Up (healthy)        0.0.0.0:6379->6379/tcp
```

### Verify Database Connection

```bash
# Test PostgreSQL connection
docker exec -it postgres psql -U agenti_user -d agenticomni -c "SELECT version();"

# Expected: PostgreSQL version info with pgvector extension

# Test pgvector extension
docker exec -it postgres psql -U agenti_user -d agenticomni -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT * FROM pg_extension WHERE extname='vector';"

# Expected: Extension listed
```

---

## Step 4: Backend Setup

### Create Virtual Environment

```bash
# Create Python virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows (not recommended, use WSL2)

# Verify Python version
python --version  # Should show Python 3.12.x
```

### Install Dependencies

```bash
# Install Python dependencies
pip install --upgrade pip
pip install -e .

# Verify key packages
pip show fastapi sqlalchemy alembic langchain

# Expected: All packages installed successfully
```

### Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic upgrade head

# Expected output:
#   INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, Initial schema with pgvector extension

# Verify tables created
docker exec -it postgres psql -U agenti_user -d agenticomni -c "\dt"

# Expected: List of tables (tenants, users, documents, document_chunks, permissions, processing_jobs)
```

### Start Backend Server

```bash
# Start FastAPI development server with hot-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
#   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
#   INFO:     Started reloader process [12345] using StatReload
#   INFO:     Started server process [12346]
#   INFO:     Waiting for application startup.
#   INFO:     Application startup complete.
```

**Keep this terminal open**. The server will auto-reload when you edit Python files.

### Verify Backend

Open a new terminal and test the health endpoint:

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-09T10:30:45.123456Z",
#   "version": "0.1.0",
#   "checks": {
#     "database": {
#       "status": "healthy",
#       "response_time_ms": 5
#     },
#     "redis": {
#       "status": "healthy",
#       "response_time_ms": 2
#     }
#   }
# }
```

### View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## Step 5: Frontend Setup

Open a new terminal (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Expected: All packages installed successfully

# Start Next.js development server
npm run dev

# Expected output:
#   - Local:        http://localhost:3000
#   - Ready in 3.2s
```

### Verify Frontend

Open your browser and visit:
- **Home Page**: http://localhost:3000

You should see the AgenticOmni landing page with Tailwind CSS styling applied.

---

## Step 6: Run Tests

### Backend Tests

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run all tests with coverage
pytest

# Expected output:
#   ============================= test session starts ==============================
#   collected X items
#   
#   tests/unit/test_config.py ....                                          [ 25%]
#   tests/unit/test_models.py ....                                          [ 50%]
#   tests/integration/test_database.py ....                                 [ 75%]
#   tests/integration/test_api.py ....                                      [100%]
#   
#   ============================= X passed in 2.5s ================================
#   Coverage report: 85%
```

### Frontend Tests

```bash
# Navigate to frontend directory
cd frontend

# Run Jest tests
npm test

# Expected output:
#   PASS  __tests__/components/sample.test.tsx
#   ✓ renders correctly (50ms)
#   
#   Test Suites: 1 passed, 1 total
#   Tests:       1 passed, 1 total
```

---

## Step 7: Code Quality Checks

### Backend Linting & Type Checking

```bash
# Run Ruff linter
ruff check src/ tests/

# Expected: No errors

# Run Ruff formatter
ruff format src/ tests/

# Run mypy type checker
mypy src/

# Expected: Success: no issues found in X source files
```

### Frontend Linting

```bash
# Navigate to frontend directory
cd frontend

# Run ESLint
npm run lint

# Expected: ✔ No linting errors
```

---

## Development Workflow

### Daily Workflow

1. **Start Services**: `docker-compose up -d` (if stopped)
2. **Activate Backend**: `source venv/bin/activate && uvicorn src.api.main:app --reload`
3. **Start Frontend**: `cd frontend && npm run dev`
4. **Code Away**: Edit files, tests auto-run, servers auto-reload

### Making Database Changes

```bash
# 1. Edit SQLAlchemy models in src/storage_indexing/models/

# 2. Auto-generate migration
alembic revision --autogenerate -m "Add user roles table"

# 3. Review generated migration in src/storage_indexing/migrations/versions/

# 4. Apply migration
alembic upgrade head

# 5. Rollback if needed
alembic downgrade -1
```

### Creating a New API Endpoint

```python
# 1. Create router file: src/api/routes/documents.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    # Implementation here
    return {"documents": []}

# 2. Register router in src/api/main.py
from src.api.routes import documents

app.include_router(documents.router, prefix="/api/v1")

# 3. View docs: http://localhost:8000/api/v1/docs
```

### Adding a Frontend Component

```tsx
// 1. Create component: frontend/components/DocumentList.tsx
import React from 'react';

export function DocumentList() {
  return <div>Document List</div>;
}

// 2. Use in page: frontend/app/documents/page.tsx
import { DocumentList } from '@/components/DocumentList';

export default function DocumentsPage() {
  return <DocumentList />;
}

// 3. View at: http://localhost:3000/documents
```

---

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -e .
```

---

### Database Connection Errors

**Problem**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if PostgreSQL container is running
docker-compose ps

# If not running, start it
docker-compose up -d postgres

# Check logs for errors
docker-compose logs postgres
```

---

### pgvector Extension Missing

**Problem**: `ERROR: type "vector" does not exist`

**Solution**:
```bash
# Connect to database and enable extension
docker exec -it postgres psql -U agenti_user -d agenticomni

# In psql shell:
CREATE EXTENSION IF NOT EXISTS vector;
\q

# Rerun migrations
alembic upgrade head
```

---

### Port Already in Use

**Problem**: `Address already in use: 0.0.0.0:8000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux

# Kill the process
kill -9 <PID>

# Or change port in .env
API_PORT=8001
```

---

### Frontend Build Errors

**Problem**: `Module not found: Can't resolve '@/components/...'`

**Solution**:
```bash
# Clear Next.js cache
cd frontend
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

---

## Useful Commands Reference

### Docker

```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose down -v        # Stop and remove volumes (fresh start)
docker-compose logs -f        # View logs (follow mode)
docker-compose ps             # List running services
docker-compose restart postgres  # Restart specific service
```

### Alembic

```bash
alembic current               # Show current migration
alembic history               # Show migration history
alembic upgrade head          # Apply all migrations
alembic downgrade -1          # Rollback one migration
alembic revision --autogenerate -m "message"  # Create migration
```

### pytest

```bash
pytest                        # Run all tests
pytest tests/unit/            # Run only unit tests
pytest -v                     # Verbose output
pytest -k test_health         # Run specific test
pytest --cov=src --cov-report=html  # Generate HTML coverage report
```

### Ruff & mypy

```bash
ruff check .                  # Lint all Python files
ruff check --fix .            # Auto-fix linting issues
ruff format .                 # Format all Python files
mypy src/                     # Type check source code
```

---

## Next Steps

Now that your development environment is set up, you can:

1. **Explore the Codebase**: Read through `src/` modules to understand the architecture
2. **Review Data Model**: See [data-model.md](./data-model.md) for complete database schema
3. **Check API Contracts**: See [contracts/](./contracts/) for OpenAPI specifications
4. **Read Implementation Plan**: See [plan.md](./plan.md) for technical decisions and rationale
5. **Start Contributing**: Pick a task from [tasks.md](./tasks.md) (once generated)

---

## Getting Help

- **Documentation**: Check `/docs` folder for architecture and design docs
- **API Docs**: http://localhost:8000/api/v1/docs (when server running)
- **Slack/Discord**: Join #agenticomni-dev channel (team chat)
- **Issues**: File a GitHub issue for bugs or feature requests

---

## Development Environment Summary

| Service | URL | Port | Status Check |
|---------|-----|------|--------------|
| **Backend API** | http://localhost:8000 | 8000 | `curl localhost:8000/api/v1/health` |
| **Frontend** | http://localhost:3000 | 3000 | Open in browser |
| **PostgreSQL** | localhost | 5436 | `docker-compose ps postgres` |
| **Redis** | localhost | 6379 | `docker-compose ps redis` |
| **API Docs (Swagger)** | http://localhost:8000/api/v1/docs | - | Open in browser |
| **API Docs (ReDoc)** | http://localhost:8000/api/v1/redoc | - | Open in browser |

---

**Setup Complete!** 🎉 You're ready to start developing on AgenticOmni.
