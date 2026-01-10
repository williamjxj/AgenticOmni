# Research & Technology Decisions

**Feature**: AgenticOmni Application Skeleton  
**Date**: January 9, 2026  
**Phase**: 0 - Research & Investigation

## Overview

This document consolidates research findings and technology decisions for initializing the AgenticOmni application skeleton. All decisions are based on the documented architecture in `docs/1-notebooklm-setup.md` and `docs/chatgpt-2.md`, prioritizing open-source, cost-effective solutions suitable for POC-to-production evolution.

---

## 1. Python Dependency Management

### Decision: pyproject.toml + pip

**Rationale**:
- **PEP 518/621 Standard**: `pyproject.toml` is the modern Python packaging standard, replacing `setup.py` and `requirements.txt`
- **Tool Consolidation**: Single file for dependencies, tool configurations (ruff, mypy, pytest), and project metadata
- **Workspace Rules Alignment**: Aligns with `.cursor/rules/python-best-practices.mdc` which emphasizes uv and pyproject.toml
- **Simplicity**: For initial skeleton, pip + pyproject.toml provides sufficient dependency resolution without Poetry overhead

**Alternatives Considered**:
- **Poetry**: Excellent dependency management and virtual environment handling, but adds complexity and another tool to learn for contributors
- **requirements.txt**: Legacy approach, lacks standardization for tool configs
- **uv**: Extremely fast Python package installer (mentioned in workspace rules), will consider for optimization phase

**Implementation Notes**:
- Use `pip install -e .` for editable installs during development
- Separate optional dependencies with `[dev]`, `[test]` extras
- Pin major versions for stability, allow minor/patch updates

---

## 2. Database Migration Tool: Alembic

### Decision: Alembic with auto-generation from SQLAlchemy models

**Rationale** (from clarification session):
- **Industry Standard**: De facto standard for SQLAlchemy-based projects
- **Auto-Generation**: Detects model changes and generates migration scripts automatically
- **Rollback Support**: Supports up/down migrations for schema rollbacks
- **Branch Management**: Handles parallel development with migration branching
- **FastAPI Integration**: Seamless integration with FastAPI + SQLAlchemy stack
- **Battle-Tested**: Used in production by thousands of companies

**Alternatives Considered**:
- **Raw SQL migrations**: Full control but high maintenance burden, error-prone
- **SQLAlchemy-Migrate**: Older tool, less actively maintained
- **Django-style migrations**: Non-standard for Python/SQLAlchemy ecosystem

**Implementation Notes**:
- Configure Alembic in `alembic.ini` with connection string from environment variables
- Place migrations in `src/storage_indexing/migrations/versions/`
- Use descriptive migration names: `001_initial_schema.py`, `002_add_user_roles.py`
- Always review auto-generated migrations before applying
- Create custom migration for pgvector extension setup

**Key Configuration**:
```python
# alembic/env.py snippet
from src.storage_indexing.models import Base
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            compare_server_default=True  # Detect default value changes
        )
        with context.begin_transaction():
            context.run_migrations()
```

---

## 3. PostgreSQL + pgvector Configuration

### Decision: PostgreSQL 14+ with pgvector extension, 1536-dimension vectors

**Rationale** (from architecture docs + clarifications):
- **Hybrid Retrieval**: Supports both vector search (pgvector) and full-text search (built-in tsvector) in single database
- **Cost-Effective**: No separate vector database subscription required for POC
- **Production-Ready**: Scales to millions of vectors with proper indexing (HNSW or IVFFlat)
- **ACID Guarantees**: Full transactional support for document metadata + vectors together
- **pgvector Maturity**: Stable extension with active development, supports cosine/L2/inner product distance

**Vector Dimensionality: 1536** (from clarification):
- Standard for OpenAI `text-embedding-3-small` and `text-embedding-ada-002`
- Excellent balance of performance, accuracy, and storage cost
- Widely compatible with multiple embedding providers (Cohere, open-source models)

**Alternatives Considered**:
- **Dedicated Vector DBs (Weaviate, Chroma, Pinecone)**: Higher operational complexity, additional service to manage
- **Elasticsearch**: Good for search but overkill for vector-only needs, higher resource usage
- **768 dimensions**: Lower storage but reduced accuracy; 3072 dimensions: higher accuracy but expensive

**Implementation Notes**:
```sql
-- Enable pgvector extension (in Alembic migration)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with vector column
CREATE TABLE document_chunks (
    chunk_id UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    content_text TEXT NOT NULL,
    embedding_vector vector(1536),  -- 1536 dimensions
    chunk_order INTEGER NOT NULL,
    chunk_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create HNSW index for fast similarity search (post-MVP optimization)
CREATE INDEX idx_chunk_embedding ON document_chunks 
USING hnsw (embedding_vector vector_cosine_ops);
```

**Indexing Strategy**:
- **Development**: No vector index initially (acceptable for small datasets)
- **MVP**: IVFFlat index (faster build time, good for < 1M vectors)
- **Production**: HNSW index (slower build, best query performance for > 1M vectors)

---

## 4. FastAPI Configuration & Best Practices

### Decision: FastAPI with async/await, dependency injection, automatic OpenAPI docs

**Rationale** (from workspace rules):
- **Modern Async**: Native async/await support for non-blocking I/O (database, LLM API calls)
- **Type Safety**: Pydantic integration provides request/response validation and auto-generated schemas
- **Developer Experience**: Automatic OpenAPI (Swagger) and ReDoc documentation at `/docs` and `/redoc`
- **Performance**: One of the fastest Python web frameworks (comparable to Node.js/Go)
- **Ecosystem**: Large ecosystem of plugins for auth, CORS, rate limiting, etc.

**Implementation Patterns**:

**1. Application Factory Pattern**:
```python
# src/api/main.py
def create_app() -> FastAPI:
    app = FastAPI(
        title="AgenticOmni API",
        version="0.1.0",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Custom middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Exception handlers
    app.add_exception_handler(CustomException, custom_exception_handler)
    
    # Register routers
    app.include_router(health_router, prefix="/api/v1")
    
    return app
```

**2. Dependency Injection for Database Sessions**:
```python
# src/api/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage in route
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # db session automatically managed
    pass
```

**3. Request ID for Tracing**:
```python
# src/api/middleware/logging.py
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

---

## 5. JSON Structured Logging

### Decision: Python `structlog` library with JSON formatter

**Rationale** (from clarification):
- **Machine-Parseable**: JSON logs easily ingested by ELK, Splunk, CloudWatch, Datadog
- **Rich Context**: Supports nested metadata (tenant_id, request_id, user_id) without string parsing
- **Performance**: structlog uses processor chains for efficient logging
- **Standards**: Follows industry best practices for cloud-native applications

**Alternatives Considered**:
- **Plain text logging**: Human-readable but difficult to parse programmatically
- **python-json-logger**: Simpler but less flexible than structlog
- **Hybrid approach**: Adds configuration complexity

**Standard Log Fields** (from FR-017):
```json
{
  "timestamp": "2026-01-09T10:30:45.123Z",
  "log_level": "INFO",
  "module": "src.api.routes.health",
  "message": "Health check endpoint accessed",
  "tenant_id": "uuid-tenant-123",
  "request_id": "uuid-request-456",
  "user_id": "uuid-user-789",
  "duration_ms": 45,
  "status_code": 200
}
```

**Implementation**:
```python
# src/shared/logging_config.py
import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger(__name__)
logger.info("document_uploaded", 
            tenant_id=tenant_id, 
            document_id=doc_id, 
            file_size=size)
```

---

## 6. Configuration Management

### Decision: Pydantic Settings with environment variable validation

**Rationale**:
- **Type Safety**: Pydantic provides runtime type checking and validation for config values
- **Auto-Parsing**: Automatically converts env vars to correct types (int, bool, list, etc.)
- **Clear Errors**: Validation errors clearly indicate missing or invalid configuration
- **IDE Support**: Type hints enable autocomplete and static analysis
- **FastAPI Integration**: Native support in FastAPI ecosystem

**Implementation**:
```python
# src/shared/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Vector Store
    vector_dimensions: int = 1536
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # LLM (optional for skeleton)
    openai_api_key: str | None = None
    
    # Logging
    log_level: str = "INFO"
    
    # Multi-tenancy
    enforce_tenant_isolation: bool = True

# Global instance
settings = Settings()
```

**`.env.example` Template**:
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5436/agenticomni
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Vector Store Configuration
VECTOR_DIMENSIONS=1536

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# LLM API Keys (optional for skeleton)
OPENAI_API_KEY=sk-...

# Logging Configuration
LOG_LEVEL=INFO

# Security
ENFORCE_TENANT_ISOLATION=true
SECRET_KEY=your-secret-key-here-change-in-production
```

---

## 7. Docker Compose Development Environment

### Decision: Docker Compose with PostgreSQL 14 + pgvector, Redis, optional nginx

**Rationale**:
- **Consistency**: Identical environment across all developer machines and CI
- **Fast Onboarding**: New developers run `docker-compose up` and have full stack
- **Service Isolation**: Database, cache, and application in separate containers
- **Production Parity**: Development environment mirrors production architecture
- **Easy Teardown**: `docker-compose down -v` removes all data for clean slate

**Services Configuration**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:v0.5.1  # PostgreSQL 16 with pgvector
    environment:
      POSTGRES_DB: agenticomni
      POSTGRES_USER: agenti_user
      POSTGRES_PASSWORD: agenti_user
    ports:
      - "5436:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agenti_user -d agenticomni"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Optional: nginx reverse proxy (for future multi-service routing)
  # nginx:
  #   image: nginx:alpine
  #   ports:
  #     - "80:80"
  #   volumes:
  #     - ./nginx.conf:/etc/nginx/nginx.conf:ro
  #   depends_on:
  #     - api

volumes:
  postgres_data:
```

**Benefits**:
- **Health Checks**: Services wait for dependencies to be ready before starting
- **Persistent Volumes**: Database data persists across container restarts
- **Port Mapping**: Services accessible from host machine for debugging

---

## 8. Next.js Frontend Configuration

### Decision: Next.js 14 with App Router, TypeScript, Tailwind CSS, shadcn/ui

**Rationale** (from specification and user rules):
- **App Router**: Modern Next.js architecture with React Server Components
- **TypeScript**: Type safety for frontend code, catches errors at compile time
- **Tailwind CSS**: Utility-first CSS for rapid UI development without custom CSS
- **shadcn/ui**: High-quality, accessible component library built on Radix UI
- **Vercel Deployment**: Optimized for Vercel deployment (future production)

**Project Structure**:
```text
frontend/
├── app/                     # Next.js 14 App Router
│   ├── layout.tsx           # Root layout with providers, fonts
│   ├── page.tsx             # Home page
│   └── globals.css          # Tailwind directives
├── components/
│   ├── ui/                  # shadcn/ui components (button, card, etc.)
│   └── layout/              # Layout components (header, sidebar)
├── lib/
│   ├── api-client.ts        # Axios/Fetch wrapper for backend API
│   └── utils.ts             # Utility functions (cn, formatters)
├── public/                  # Static assets
└── __tests__/               # Jest + React Testing Library tests
```

**API Client Pattern**:
```typescript
// lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}
```

**Environment Variables**:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 9. Testing Strategy & Tools

### Decision: pytest (backend), Jest + React Testing Library (frontend)

**Backend Testing (pytest)**:
- **Fixtures**: Reusable test setup (database, API client, mock data)
- **Async Support**: pytest-asyncio for testing async functions
- **Coverage**: pytest-cov for code coverage reports
- **Mocking**: pytest-mock for mocking external dependencies

**Test Organization**:
```text
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (pure functions, models)
│   ├── test_config.py
│   └── test_models.py
├── integration/             # Integration tests (DB, API)
│   ├── test_database.py
│   └── test_api.py
└── fixtures/
    └── sample_data.py       # Test data factories
```

**Key Fixtures**:
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
async def test_db_engine():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_db_engine):
    async with AsyncSession(test_db_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
def test_client():
    from src.api.main import create_app
    app = create_app()
    return TestClient(app)
```

**Frontend Testing (Jest + RTL)**:
- **Component Tests**: Test UI components in isolation
- **Integration Tests**: Test component interactions and API calls
- **Snapshot Tests**: Detect unintended UI changes

---

## 10. Multi-Tenancy Row-Level Security Pattern

### Decision: Application-level tenant_id filtering with database constraints

**Rationale** (from clarification):
- **Simplicity**: Easier to manage than schema-per-tenant or database-per-tenant
- **Scalability**: Single schema scales well to thousands of tenants
- **Cost-Effective**: Shared infrastructure reduces operational overhead
- **Flexible**: Can later add PostgreSQL Row-Level Security (RLS) policies for additional safety

**Implementation Pattern**:

**1. Database Constraints**:
```sql
-- All tenant-scoped tables include tenant_id with FK constraint
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    -- ... other fields
    created_at TIMESTAMP DEFAULT NOW()
);

-- Composite indexes for tenant-scoped queries
CREATE INDEX idx_documents_tenant ON documents(tenant_id, created_at DESC);
```

**2. SQLAlchemy Base Model Mixin**:
```python
# src/storage_indexing/models/base.py
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, UUID, ForeignKey

class TenantScopedMixin:
    """Mixin for tenant-scoped entities"""
    
    @declared_attr
    def tenant_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey('tenants.tenant_id', ondelete='CASCADE'),
            nullable=False,
            index=True
        )
```

**3. Repository Pattern with Automatic Tenant Filtering**:
```python
# Future implementation (out of scope for skeleton)
class DocumentRepository:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
    
    async def get_by_id(self, document_id: UUID) -> Document:
        result = await self.session.execute(
            select(Document)
            .where(Document.document_id == document_id)
            .where(Document.tenant_id == self.tenant_id)  # Enforced at app level
        )
        return result.scalar_one_or_none()
```

**4. FastAPI Dependency for Tenant Context**:
```python
# Future implementation
async def get_current_tenant(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    # Extract tenant from JWT, subdomain, or header
    tenant_id = extract_tenant_from_request(request)
    tenant = await get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
```

---

## 11. Code Quality Tools

### Decision: Ruff (linting + formatting), mypy (type checking), pytest (testing)

**Rationale** (from workspace rules):
- **Ruff**: Extremely fast Python linter and formatter, replaces black + isort + flake8
- **mypy**: Industry-standard static type checker for Python
- **Simple Toolchain**: Three tools cover all quality needs (lint, type, test)

**Tool Configuration in pyproject.toml**:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "ANN", # flake8-annotations
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--strict-markers",
]
```

---

## 12. ProcessingJob State Machine

### Decision: 6-state enum (pending, processing, completed, failed, cancelled, retrying)

**Rationale** (from clarification):
- **Comprehensive Coverage**: Handles all job lifecycle scenarios including retries
- **Retry Support**: Dedicated `retrying` state enables automatic retry logic
- **Terminal States**: Clear terminal states (completed, failed, cancelled) for reporting
- **Observable**: Each state provides clear operational visibility

**State Transitions**:
```
pending → processing → completed (success)
                    → failed (error, no retry)
                    → retrying → processing (retry attempt)
                              → failed (max retries exceeded)
                              → cancelled (manual cancellation)
```

**SQLAlchemy Enum Definition**:
```python
# src/storage_indexing/models/processing_job.py
from enum import Enum as PyEnum
from sqlalchemy import Enum

class JobStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(
        Enum(JobStatus, name="job_status", create_type=True),
        nullable=False,
        default=JobStatus.PENDING,
        index=True
    )
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    # ... other fields
```

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Dependency Mgmt** | pyproject.toml + pip | Modern Python standard, tool consolidation |
| **Database Migrations** | Alembic | Industry standard, auto-generation, SQLAlchemy integration |
| **Vector Store** | PostgreSQL + pgvector (1536d) | Hybrid search, cost-effective, OpenAI compatibility |
| **API Framework** | FastAPI + async/await | Performance, type safety, auto-docs |
| **Logging** | structlog (JSON) | Machine-parseable, cloud-native, rich context |
| **Configuration** | Pydantic Settings | Type-safe, validation, FastAPI integration |
| **Container Orchestration** | Docker Compose | Development consistency, fast onboarding |
| **Frontend** | Next.js 14 + TypeScript + Tailwind | Modern React, type safety, rapid development |
| **Backend Testing** | pytest + fixtures | Python standard, async support, good DX |
| **Frontend Testing** | Jest + RTL | React standard, component-focused |
| **Multi-Tenancy** | Row-level with tenant_id | Simple, scalable, cost-effective |
| **Code Quality** | Ruff + mypy | Fast, comprehensive, modern tooling |
| **Job States** | 6-state enum | Comprehensive, retry-capable, observable |

---

**Research Phase Complete**: All technology decisions documented with rationale. Ready for Phase 1 (Design).
