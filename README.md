# AgenticOmni: AI-Powered Document Intelligence Platform

**Status**: 🚧 Application Skeleton - Foundation Phase  
**Version**: 0.1.0  
**License**: Proprietary

## 📄 Overview

AgenticOmni is an enterprise-grade AI document intelligence platform built on an ETL-to-RAG pipeline architecture. The system transforms complex multi-format documents (PDFs, DOCX, PPTX, images, audio, video) into searchable, intelligent knowledge bases powered by retrieval-augmented generation.

### Key Capabilities

- **Multi-Format Ingestion**: Process diverse document types with OCR, NLP, and multimedia extraction
- **Hybrid Retrieval**: Combine vector search (pgvector) with keyword search for optimal accuracy
- **Enterprise Security**: Row-level multi-tenancy with RBAC and document-level permissions
- **Production-Ready**: Async FastAPI backend, PostgreSQL + pgvector, Docker development environment
- **Modern Frontend**: Next.js 16 with React 19, TypeScript, Tailwind CSS 4, and shadcn/ui components

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

### 📖 Core Documentation (Version Controlled)

All documentation follows [Semantic Versioning](https://semver.org/) with change tracking in [CHANGELOG.md](./docs/CHANGELOG.md).

- **[Documentation Index](./docs/README.md)** - Complete documentation catalog with versioning standards
- **[Implementation Summary](./docs/implementation-summary.md)** v1.0.0 - Complete implementation overview with diagrams
- **[Versioning Guide](./docs/VERSIONING_GUIDE.md)** v1.0.0 - Quick reference for documentation versioning
- **[CHANGELOG](./docs/CHANGELOG.md)** - Documentation change history

### 🎯 Feature Specifications

- **[Quickstart Guide](./specs/001-app-skeleton-init/quickstart.md)** - Detailed setup instructions
- **[Implementation Plan](./specs/001-app-skeleton-init/plan.md)** - Technical architecture and decisions
- **[Data Model](./specs/001-app-skeleton-init/data-model.md)** - Database schema and entities
- **[API Contracts](./specs/001-app-skeleton-init/contracts/)** - OpenAPI specifications
- **[Tasks](./specs/001-app-skeleton-init/tasks.md)** - Implementation task breakdown (121 tasks)

### 🏛️ Architecture Documents

- **[Technical Blueprint](./docs/Project_Gemini_Technical_Blueprint.pdf)** - Complete system design
- **[NotebookLM Setup](./docs/1-notebooklm-setup.md)** - Architecture overview and module design
- **[ChatGPT Setup](./docs/2-chatgpt-setup.md)** - ETL workflow diagrams
- **[Requirements](./docs/requirements-1.md)** - Business and technical requirements

### 📝 Document Validation

```bash
# Validate all documentation follows standards
python scripts/validate_docs.py

# Create new documentation from template
cp docs/templates/DOCUMENT_TEMPLATE.md docs/my-new-doc.md
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
