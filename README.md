# AgenticOmni: AI-Powered Document Intelligence Platform

**Status**: ✅ MVP Complete - Document Upload & Processing Pipeline  
**Version**: 0.2.0  
**License**: Proprietary

## 📄 Overview

AgenticOmni is an enterprise-grade AI document intelligence platform built on an ETL-to-RAG pipeline architecture. The system transforms complex multi-format documents (PDF, DOCX, TXT) into searchable, intelligent knowledge bases powered by retrieval-augmented generation.

### 🎯 Current Features (v0.2.0)

#### Document Upload & Processing
- ✅ **Multi-Format Support**: PDF (Docling), DOCX (python-docx), TXT
- ✅ **Single & Batch Upload**: Upload 1-10 documents at once
- ✅ **Smart Validation**: File type detection (magic bytes), size limits, quota management
- ✅ **Async Processing**: Background parsing with Dramatiq task queue
- ✅ **Progress Tracking**: Real-time status updates (0-100% progress)
- ✅ **RAG-Optimized Chunking**: 512-token chunks with 50-token overlap
- ✅ **Storage Options**: Local filesystem or S3-compatible object storage
- ✅ **Security**: Malware scanning (ClamAV), content hashing for duplicates

#### API Endpoints
- `POST /api/v1/documents/upload` - Single document upload
- `POST /api/v1/documents/batch-upload` - Batch upload (up to 10 files)
- `GET /api/v1/documents/{id}` - Get document details
- `GET /api/v1/documents` - List documents with pagination
- `GET /api/v1/processing/jobs/{id}` - Get processing job status
- `POST /api/v1/processing/jobs/{id}/retry` - Retry failed job
- `POST /api/v1/processing/jobs/{id}/cancel` - Cancel processing job
- `GET /api/v1/health` - Health check

### Key Capabilities

- **Multi-Format Ingestion**: Process PDF, DOCX, and TXT documents with intelligent parsing
- **RAG-Ready Chunking**: Semantic text splitting optimized for vector search
- **Enterprise Security**: Multi-tenant isolation with per-tenant storage quotas
- **Production-Ready**: Async FastAPI backend, PostgreSQL + pgvector, Docker environment
- **Modern Frontend**: Next.js 14 with React, TypeScript, Tailwind CSS, and shadcn/ui components

## 🏗️ Architecture

### Backend Modules

```
src/
├── ingestion_parsing/      # Document upload, OCR, multimedia processing
├── storage_indexing/        # Database models, Alembic migrations, pgvector
├── rag_orchestration/       # LangChain/LlamaIndex RAG workflows
├── eval_harness/            # Metrics, accuracy tracking, regression tests
├── security_auth/           # Multi-tenant RBAC, permissions, audit logs
├── api/                     # FastAPI server, routes, middleware
└── shared/                  # Config, logging, common utilities
```

### Frontend

```
frontend/
├── app/                     # Next.js 16 App Router pages
├── components/              # React components + shadcn/ui
└── lib/                     # API client, utilities
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI + async/await | High-performance async API server |
| **Database** | PostgreSQL 14+ | ACID-compliant relational database |
| **Vector Store** | pgvector (1536d) | Semantic search with embeddings |
| **Caching** | Redis 7 | Session storage and query caching |
| **Migrations** | Alembic | Database schema version control |
| **ORM** | SQLAlchemy (async) | Type-safe database access |
| **RAG Framework** | LangChain, LlamaIndex | Flexible retrieval orchestration |
| **Logging** | structlog (JSON) | Structured, cloud-native logging |
| **Testing** | pytest + pytest-asyncio | Comprehensive test coverage |
| **Code Quality** | Ruff, mypy | Fast linting and type checking |
| **Frontend** | Next.js 14, TypeScript | Modern React with SSR/SSG |
| **Styling** | Tailwind CSS, shadcn/ui | Utility-first CSS + accessible components |
| **Containerization** | Docker Compose | Consistent development environment |

## 📡 API Usage

### Upload a Single Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F "tenant_id=1" \
  -F "user_id=1"
```

Response:
```json
{
  "document_id": 123,
  "filename": "doc_20240109_abc123.pdf",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "content_hash": "a1b2c3...",
  "job_id": 456,
  "status": "uploaded"
}
```

### Upload Multiple Documents (Batch)

```bash
curl -X POST "http://localhost:8000/api/v1/documents/batch-upload" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "files=@doc3.txt" \
  -F "tenant_id=1" \
  -F "user_id=1"
```

Response:
```json
{
  "batch_id": "batch_abc123",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "filename": "doc1.pdf",
      "status": "success",
      "document_id": 123,
      "job_id": 456
    },
    ...
  ]
}
```

### Check Processing Status

```bash
curl "http://localhost:8000/api/v1/processing/jobs/456"
```

Response:
```json
{
  "job_id": 456,
  "document_id": 123,
  "status": "processing",
  "progress_percent": 75,
  "job_type": "parse_document",
  "created_at": "2024-01-09T10:00:00Z"
}
```

### Supported Formats

| Format | Extension | Parser | Features |
|--------|-----------|--------|----------|
| **PDF** | `.pdf` | Docling (IBM) | Tables, images, structure preservation |
| **Word** | `.docx` | python-docx | Paragraphs, tables, metadata |
| **Text** | `.txt` | Native | UTF-8, multi-encoding support |

### Configuration

Key environment variables for document upload:

```bash
# Storage
STORAGE_BACKEND=local  # or 's3'
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=50
MAX_BATCH_SIZE=10

# Allowed formats
ALLOWED_FILE_TYPES=pdf,docx,txt

# Processing
DRAMATIQ_BROKER_URL=redis://localhost:6379/1
MAX_CONCURRENT_PARSING_JOBS=5

# Chunking for RAG
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
MIN_CHUNK_SIZE_TOKENS=100

# Security (optional)
ENABLE_MALWARE_SCANNING=false
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
```

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.12+
- **Node.js**: 18+
- **Docker**: 20+ with Docker Compose
- **Git**: 2.30+

### Installation

```bash
# 1. Clone the repository
git clone <repository-url> agenticomni
cd agenticomni

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Configuration section below)

# 3. Start services (PostgreSQL + Redis)
docker-compose up -d

# 4. Set up Python environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# 5. Run database migrations
alembic upgrade head

# 6. Start backend API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 7. In a new terminal, start frontend (optional)
cd frontend
npm install
npm run dev
```

### Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-09T...",
#   "version": "0.1.0",
#   "checks": {
#     "database": {"status": "healthy", "response_time_ms": 5},
#     "redis": {"status": "healthy", "response_time_ms": 2}
#   }
# }

# View API documentation
# Open http://localhost:8000/api/v1/docs in your browser

# View frontend (if started)
# Open http://localhost:3000 in your browser
```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Database (PostgreSQL with pgvector)
DATABASE_URL=postgresql+asyncpg://agenti_user:your_password@localhost:5436/agenticomni
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Vector Store
VECTOR_DIMENSIONS=1536

# API Server
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
ENFORCE_TENANT_ISOLATION=true
```

### Optional Environment Variables

```bash
# LLM API Keys (for future RAG features)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

See `.env.example` for complete configuration options with documentation.

## 📚 Documentation

### 📖 Core Documentation

All documentation follows [Semantic Versioning](https://semver.org/) with change tracking in [CHANGELOG.md](./docs/CHANGELOG.md).

- **[Documentation Index](./docs/README.md)** - Complete documentation catalog and navigation
- **[Implementation](./docs/IMPLEMENTATION.md)** v0.2.0 - Complete implementation status and summary (387/387 tasks)
- **[CHANGELOG](./docs/CHANGELOG.md)** - Version history and release notes

### 🎯 Setup & Configuration Guides

- **[Quickstart Guide](./specs/002-doc-upload-parsing/quickstart.md)** - 10-step setup instructions
- **[Environment Configuration](./docs/ENV_CONFIGURATION.md)** - Complete environment variable reference
- **[Frontend Integration](./docs/FRONTEND_INTEGRATION.md)** - Next.js/React integration guide
- **[Malware Scanning](./docs/MALWARE_SCANNING.md)** - ClamAV setup and troubleshooting
- **[Production Deploy](./docs/PRODUCTION_DEPLOY.md)** - Production deployment checklist

### 🏗️ Feature Specifications

- **[Application Skeleton Spec](./specs/001-app-skeleton-init/spec.md)** - Foundation implementation
- **[Document Upload & Parsing Spec](./specs/002-doc-upload-parsing/spec.md)** - Document processing feature
- **[Data Models](./specs/002-doc-upload-parsing/data-model.md)** - Database schema and entities
- **[API Contracts](./specs/002-doc-upload-parsing/contracts/)** - OpenAPI specifications
- **[Implementation Plan](./specs/002-doc-upload-parsing/plan.md)** - Technical architecture
- **[Task Breakdown](./specs/002-doc-upload-parsing/tasks.md)** - 165 tasks (100% complete)

### 📝 Development Guidelines

- **[Contributing Guidelines](./docs/CONTRIBUTING.md)** - How to contribute
- **[Versioning](./docs/VERSIONING.md)** - Documentation versioning and version control guide
- **[Document Templates](./docs/templates/)** - ADR and technical doc templates

### 🏛️ Architecture References

- **[Technical Blueprint](./docs/Project_Gemini_Technical_Blueprint.pdf)** - Complete system design (PDF)
- **[Tech Stack Guide](./docs/chatgpt-tech-stack.pdf)** - Technology decisions (PDF)

### 📝 Creating New Documentation

```bash
# Validate all documentation follows standards
python scripts/validate_docs.py

# Create new documentation from template
cp docs/templates/DOCUMENT_TEMPLATE.md docs/my-new-doc.md
# or
cp docs/templates/ADR_TEMPLATE.md docs/adr-001-my-decision.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run tests in watch mode (requires pytest-watch)
ptw
```

### Test Organization

```
tests/
├── unit/             # Unit tests (models, utilities, pure functions)
├── integration/      # Integration tests (database, API, external services)
└── fixtures/         # Test data factories and fixtures
```

## 🔧 Development

### Code Quality

```bash
# Linting with Ruff
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/

# Type checking with mypy
mypy src/
```

### Database Migrations

```bash
# Create new migration (auto-generated from model changes)
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Services

```bash
# Start all services (PostgreSQL, Redis)
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart postgres
```

## 📁 Project Structure

```
agenticomni/
├── src/                      # Backend source code
│   ├── api/                  # FastAPI application
│   ├── storage_indexing/     # Database models and migrations
│   ├── ingestion_parsing/    # Document processing (scaffolded)
│   ├── rag_orchestration/    # RAG workflows (scaffolded)
│   ├── eval_harness/         # Evaluation metrics (scaffolded)
│   ├── security_auth/        # Security and auth (scaffolded)
│   └── shared/               # Common utilities
├── tests/                    # Test suite
├── frontend/                 # Next.js frontend application
├── config/                   # Configuration files
├── scripts/                  # Automation scripts
├── docs/                     # Architecture documentation
├── specs/                    # Feature specifications and plans
├── docker-compose.yml        # Docker services configuration
├── pyproject.toml            # Python dependencies and tool config
├── alembic.ini               # Alembic migration configuration
└── README.md                 # This file
```

## 🛠️ Development Scripts

```bash
# Database setup
./scripts/setup_db.sh         # Initialize database and run migrations

# Development server
./scripts/run_dev.sh           # Start backend with hot-reload

# Environment validation
./scripts/validate_env.sh      # Check all required env vars are set

# Full setup (from scratch)
./scripts/full_setup.sh        # Complete environment setup and validation
```

## 🚢 Deployment

**Note**: Production deployment configuration is planned for future releases.

## 🤝 Contributing

This is a private project. For internal contributors:

1. Follow the established code style (enforced by Ruff and mypy)
2. Write tests for new features (minimum 80% coverage)
3. Update documentation when adding new modules or changing APIs
4. Use feature branches and pull requests for all changes
5. Ensure all checks pass before requesting review

## 📊 Project Status

### Current Phase: Application Skeleton ✅

- [x] Project structure and module organization
- [x] Dependency management (pyproject.toml)
- [x] Configuration management (Pydantic Settings)
- [x] Database schema with 6 entities
- [x] Alembic migrations setup
- [x] FastAPI server with health check
- [x] Docker development environment
- [x] Testing framework (pytest)
- [x] Frontend shell (Next.js)

### Next Phase: Document Processing Pipeline

- [ ] Docling integration for PDF/DOCX parsing
- [ ] OCR engine integration (PaddleOCR or Tesseract)
- [ ] Document upload and storage endpoints
- [ ] Embedding generation pipeline
- [ ] Vector similarity search implementation

### Future Phases

- [ ] RAG query endpoints with LangChain
- [ ] LangGraph agentic workflows
- [ ] Evaluation harness and metrics dashboard
- [ ] Authentication and authorization (Auth0/Keycloak)
- [ ] Admin dashboard UI
- [ ] Multi-document relationship queries (GraphRAG)

## 📝 License

Proprietary - All Rights Reserved

## 👥 Contact

For questions or support, contact the development team.

---

**Built with** ❤️ **for enterprise document intelligence**
