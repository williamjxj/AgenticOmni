# Tasks: AgenticOmni Application Skeleton

**Input**: Design documents from `/specs/001-app-skeleton-init/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/health-api.yaml

**Tests**: Not applicable for skeleton initialization - the spec focuses on creating the testing framework itself, not writing tests for the skeleton.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/` at repository root with 7 modules
- **Frontend**: `frontend/` directory with Next.js structure
- **Tests**: `tests/` mirroring `src/` structure
- **Config**: `config/` for settings, root for `.env.example`
- **Scripts**: `scripts/` for automation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and foundational file structure

- [x] T001 Create root directory structure: src/, tests/, docs/, config/, scripts/, frontend/
- [x] T002 Create src/ module subdirectories: ingestion_parsing/, storage_indexing/, rag_orchestration/, eval_harness/, security_auth/, api/, shared/
- [x] T003 [P] Create __init__.py in src/ and all subdirectories: src/__init__.py, src/ingestion_parsing/__init__.py, src/storage_indexing/__init__.py, src/rag_orchestration/__init__.py, src/eval_harness/__init__.py, src/security_auth/__init__.py, src/api/__init__.py, src/shared/__init__.py
- [x] T004 [P] Create placeholder README.md files in scaffolded modules: src/ingestion_parsing/README.md, src/rag_orchestration/README.md, src/eval_harness/README.md, src/security_auth/README.md
- [x] T005 [P] Create .gitignore with Python, Node.js, environment files, IDE-specific patterns
- [x] T006 [P] Create root README.md with project overview, architecture, and setup instructions per quickstart.md

---

## Phase 2: User Story 1 - Core Project Structure (Priority: P1) 🎯 MVP Foundation

**Goal**: Establish complete directory structure with all required configuration files for a production-ready skeleton

**Independent Test**: Verify all directories exist, all __init__.py files present, all root configuration files created

### Implementation for User Story 1

- [x] T007 [US1] Validate directory structure completeness: run script to check all required directories exist
- [x] T008 [US1] Validate __init__.py presence: ensure all Python modules have proper package markers
- [x] T009 [US1] Document module purposes: ensure each README.md explains module responsibility and future features

**Checkpoint**: Directory structure is complete and validated. All modules are properly marked as Python packages.

---

## Phase 3: User Story 2 - Dependency Management (Priority: P1) 🎯 MVP Foundation

**Goal**: Configure Python dependencies with pyproject.toml including all required libraries for document AI, RAG, and API development

**Independent Test**: Run `pip install -e .` and verify all packages install without conflicts. Verify pytest and ruff commands work.

### Implementation for User Story 2

- [x] T010 [US2] Create pyproject.toml with project metadata (name, version, description, authors)
- [x] T011 [US2] Add core dependencies to pyproject.toml: langchain, llama-index, psycopg2-binary, pgvector, sqlalchemy, alembic, fastapi, uvicorn
- [x] T012 [US2] Add document processing dependencies: python-multipart, pillow, pytesseract, opencv-python, structlog
- [x] T013 [US2] Add testing dependencies: pytest, pytest-cov, pytest-mock, pytest-asyncio
- [x] T014 [US2] Add code quality dependencies: ruff, mypy
- [x] T015 [US2] Configure tool.ruff in pyproject.toml: line-length=100, select rules (E, W, F, I, N, UP, ANN, B, C4)
- [x] T016 [US2] Configure tool.mypy in pyproject.toml: python_version="3.12", strict=true
- [x] T017 [US2] Configure tool.pytest.ini_options in pyproject.toml: testpaths, coverage settings
- [x] T018 [US2] Create requirements.txt as backup reference (generated from pyproject.toml)
- [x] T019 [US2] Verify installation: test `pip install -e .` completes successfully
- [x] T020 [US2] Verify tools: test `pytest --version` and `ruff --version` execute without errors

**Checkpoint**: All dependencies install successfully. Development tools (pytest, ruff, mypy) are operational.

---

## Phase 4: User Story 3 - Configuration Management (Priority: P1) 🎯 MVP Foundation

**Goal**: Implement environment-based configuration with validation using Pydantic Settings

**Independent Test**: Set environment variables, run config loader, verify values load correctly and missing config raises clear errors

### Implementation for User Story 3

- [x] T021 [US3] Create .env.example with all required environment variables and documentation
- [x] T022 [US3] Add DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW to .env.example
- [x] T023 [US3] Add VECTOR_DIMENSIONS=1536, API_HOST, API_PORT, CORS_ORIGINS to .env.example
- [x] T024 [US3] Add LOG_LEVEL, SECRET_KEY, ENFORCE_TENANT_ISOLATION to .env.example
- [x] T025 [US3] Add optional LLM API keys section (OPENAI_API_KEY, etc.) to .env.example
- [x] T026 [US3] Create config/__init__.py to mark as package
- [x] T027 [US3] Create config/settings.py with Pydantic BaseSettings class
- [x] T028 [US3] Add database configuration fields to Settings: database_url, database_pool_size, database_max_overflow
- [x] T029 [US3] Add vector store configuration to Settings: vector_dimensions (default 1536)
- [x] T030 [US3] Add API configuration to Settings: api_host, api_port, cors_origins (List[str])
- [x] T031 [US3] Add logging configuration to Settings: log_level (default INFO)
- [x] T032 [US3] Add security configuration to Settings: secret_key, enforce_tenant_isolation
- [x] T033 [US3] Create src/shared/__init__.py package marker
- [x] T034 [US3] Create src/shared/config.py with settings instance: settings = Settings()
- [x] T035 [US3] Add validation logic: test that Settings() raises clear error for missing required vars
- [x] T036 [US3] Create src/shared/exceptions.py with custom exception classes (ConfigurationError, etc.)
- [x] T037 [US3] Test configuration loading: verify environment variables are correctly parsed and validated

**Checkpoint**: Configuration management is fully functional. Missing or invalid environment variables produce clear error messages.

---

## Phase 5: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before database, API, or frontend work can proceed

**⚠️ CRITICAL**: All user stories beyond this point depend on this phase

### Logging Infrastructure

- [x] T038 Create src/shared/logging_config.py with structlog JSON configuration
- [x] T039 Configure structlog processors: add_logger_name, add_log_level, TimeStamper(iso), JSONRenderer
- [x] T040 Add standard log fields to structlog: timestamp, log_level, module, message, tenant_id, request_id, error
- [x] T041 Create logger factory function: get_logger(module_name) → returns configured logger

### Database Connection Pool

- [x] T042 Create src/storage_indexing/__init__.py package marker
- [x] T043 Create src/storage_indexing/database.py with async engine configuration
- [x] T044 Configure SQLAlchemy async engine with pool_size and max_overflow from settings
- [x] T045 Create async_session_maker factory for database sessions
- [x] T046 Create get_db() async generator for FastAPI dependency injection

**Checkpoint**: Logging and database connection infrastructure ready. User stories can now proceed.

---

## Phase 6: User Story 4 - Database Schema Foundation (Priority: P2)

**Goal**: Define complete database schema with 6 entities, Alembic migrations, and pgvector support

**Independent Test**: Run `alembic upgrade head` against test PostgreSQL with pgvector. Verify all 6 tables created with correct indexes and enums.

### Database Models Setup

- [x] T047 [US4] Create src/storage_indexing/models/ directory
- [x] T048 [US4] Create src/storage_indexing/models/__init__.py with Base declarative class
- [x] T049 [P] [US4] Create src/storage_indexing/models/base.py with SQLAlchemy Base and TenantScopedMixin
- [x] T050 [P] [US4] Create src/storage_indexing/models/tenant.py with Tenant model (tenant_id, name, domain, settings JSONB, status, timestamps)
- [x] T051 [P] [US4] Create src/storage_indexing/models/user.py with User model (user_id, tenant_id FK, email, hashed_password, role enum, full_name, last_login, is_active, timestamps)
- [x] T052 [P] [US4] Create src/storage_indexing/models/document.py with Document model (document_id, tenant_id FK, filename, file_type, file_size, storage_path, processing_status enum, document_metadata JSONB, timestamps)
- [x] T053 [P] [US4] Create src/storage_indexing/models/document_chunk.py with DocumentChunk model (chunk_id, document_id FK, content_text, embedding_vector(1536), chunk_order, chunk_metadata JSONB, created_at)
- [x] T054 [P] [US4] Create src/storage_indexing/models/permission.py with Permission model (permission_id, user_id FK, resource_type enum, resource_id, permission_level enum, granted_at, granted_by FK)
- [x] T055 [P] [US4] Create src/storage_indexing/models/processing_job.py with ProcessingJob model and JobStatus/JobType enums (job_id, document_id FK, tenant_id FK, job_type, status, retry_count, max_retries, started_at, completed_at, error_message, created_at)

### Alembic Migration Setup

- [x] T056 [US4] Initialize Alembic: run `alembic init src/storage_indexing/migrations`
- [x] T057 [US4] Configure alembic.ini with database URL from environment variable
- [x] T058 [US4] Update src/storage_indexing/migrations/env.py to import Base metadata and set target_metadata
- [x] T059 [US4] Configure env.py to use async engine and enable compare_type=True, compare_server_default=True
- [x] T060 [US4] Create src/storage_indexing/migrations/versions/ directory
- [x] T061 [US4] Create initial migration: alembic revision --autogenerate -m "Initial schema with pgvector"
- [x] T062 [US4] Edit migration to add CREATE EXTENSION IF NOT EXISTS vector before tables
- [x] T063 [US4] Edit migration to create job_status and job_type enums
- [x] T064 [US4] Edit migration to ensure all indexes, constraints, and foreign keys are correctly defined
- [x] T065 [US4] Test migration: run `alembic upgrade head` on test database
- [x] T066 [US4] Verify all 6 tables created with correct schema
- [x] T067 [US4] Verify pgvector extension enabled and functional
- [x] T068 [US4] Verify enums created: job_status (6 states), job_type (4 types)
- [x] T069 [US4] Create alembic downgrade migration for rollback testing

### Repository Layer (Scaffolded)

- [x] T070 [P] [US4] Create src/storage_indexing/repositories/ directory
- [x] T071 [P] [US4] Create src/storage_indexing/repositories/__init__.py package marker
- [x] T072 [P] [US4] Add placeholder comment in repositories/__init__.py: "Repository pattern to be implemented in future feature"

**Checkpoint**: Database schema complete with 6 entities. Migrations run successfully. pgvector functional. Repository layer scaffolded for future development.

---

## Phase 7: User Story 5 - API Server Scaffold (Priority: P2)

**Goal**: Create FastAPI application with health check endpoint, CORS, middleware, and auto-generated documentation

**Independent Test**: Start server with `uvicorn src.api.main:app --reload`. Access http://localhost:8000/api/v1/health (returns 200). Access http://localhost:8000/api/v1/docs (Swagger UI loads).

### FastAPI Application Setup

- [x] T073 [US5] Create src/api/__init__.py package marker
- [x] T074 [US5] Create src/api/main.py with FastAPI app factory: create_app() function
- [x] T075 [US5] Configure FastAPI app: title="AgenticOmni API", version="0.1.0", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc"
- [x] T076 [US5] Add CORS middleware to app: allow_origins from settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
- [x] T077 [US5] Create src/api/dependencies.py with get_db() async dependency (reuses from storage_indexing/database.py)
- [x] T078 [US5] Add get_settings() dependency returning settings instance

### Middleware

- [x] T079 [P] [US5] Create src/api/middleware/ directory
- [x] T080 [P] [US5] Create src/api/middleware/__init__.py package marker
- [x] T081 [P] [US5] Create src/api/middleware/logging.py with LoggingMiddleware class (uses structlog, adds request_id to context)
- [x] T082 [P] [US5] Create src/api/middleware/request_id.py with RequestIDMiddleware (generates UUID, adds to request state and response headers)
- [x] T083 [P] [US5] Create src/api/middleware/error_handler.py with global exception handler (catches all exceptions, returns JSON with error details)
- [x] T084 [US5] Register all middleware in main.py: RequestIDMiddleware, LoggingMiddleware, error handler

### Health Check Endpoint

- [x] T085 [P] [US5] Create src/api/routes/ directory
- [x] T086 [P] [US5] Create src/api/routes/__init__.py package marker
- [x] T087 [US5] Create src/api/routes/health.py with health check router
- [x] T088 [US5] Implement GET /health endpoint: returns {status, timestamp, version, checks: {database, redis}}
- [x] T089 [US5] Add database health check: test connection with simple query, measure response_time_ms
- [x] T090 [US5] Add Redis health check (optional): ping Redis, measure response_time_ms
- [x] T091 [US5] Handle unhealthy state: return 503 if database unreachable
- [x] T092 [US5] Add response models using Pydantic: HealthResponse, ComponentHealth schemas
- [x] T093 [US5] Register health router in main.py: app.include_router(health_router, prefix="/api/v1", tags=["health"])

### API Testing & Validation

- [x] T094 [US5] Create scripts/run_dev.sh to start uvicorn with hot-reload: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
- [x] T095 [US5] Test server startup: run scripts/run_dev.sh and verify no errors
- [x] T096 [US5] Test health endpoint: curl http://localhost:8000/api/v1/health (expect 200 with JSON response)
- [x] T097 [US5] Test Swagger docs: open http://localhost:8000/api/v1/docs in browser (verify interactive docs load)
- [x] T098 [US5] Test ReDoc: open http://localhost:8000/api/v1/redoc (verify documentation renders)
- [x] T099 [US5] Verify CORS headers: test OPTIONS request from different origin
- [x] T100 [US5] Verify request ID: check X-Request-ID header in health check response

**Checkpoint**: FastAPI server running. Health check operational. API documentation accessible. All middleware functional.

---

## Phase 8: User Story 6 - Docker Development Environment (Priority: P2)

**Goal**: Configure Docker Compose with PostgreSQL + pgvector, Redis, and health checks for consistent local development

**Independent Test**: Run `docker-compose up -d`. Verify all services start and health checks pass. Connect to PostgreSQL and verify pgvector extension installed.

### Docker Compose Configuration

- [x] T101 [US6] Create docker-compose.yml in project root
- [x] T102 [US6] Add postgres service: image ankane/pgvector:v0.5.1 (PostgreSQL 16 with pgvector)
- [x] T103 [US6] Configure postgres environment: POSTGRES_DB=agenticomni, POSTGRES_USER=agenti_user, POSTGRES_PASSWORD=agenti_user
- [x] T104 [US6] Add postgres port mapping: "5436:5432"
- [x] T105 [US6] Add postgres volume: postgres_data:/var/lib/postgresql/data
- [x] T106 [US6] Add postgres healthcheck: pg_isready command with interval=10s, timeout=5s, retries=5
- [x] T107 [P] [US6] Add redis service: image redis:7-alpine
- [x] T108 [P] [US6] Configure redis port mapping: "6380:6379"
- [x] T109 [P] [US6] Add redis healthcheck: redis-cli ping with interval=10s, timeout=3s, retries=5
- [x] T110 [US6] Define volume: postgres_data (persistent database storage)

### Database Initialization Script

- [x] T111 [P] [US6] Create scripts/init_db.sql with CREATE EXTENSION IF NOT EXISTS vector
- [x] T112 [P] [US6] Add init_db.sql to postgres container: volumes: ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
- [x] T113 [US6] Update DATABASE_URL in .env.example to match docker-compose postgres configuration

### Docker Testing & Validation

- [x] T114 [US6] Test Docker Compose startup: run `docker-compose up -d` and verify no errors
- [x] T115 [US6] Verify services running: run `docker-compose ps` and check all services show "Up (healthy)"
- [x] T116 [US6] Test PostgreSQL connection: docker exec -it postgres psql -U agenti_user -d agenticomni -c "SELECT version();"
- [x] T117 [US6] Verify pgvector extension: docker exec -it postgres psql -U agenti_user -d agenticomni -c "SELECT * FROM pg_extension WHERE extname='vector';"
- [x] T118 [US6] Test Redis connection: docker exec -it redis redis-cli ping (expect PONG)
- [x] T119 [US6] Test application database connection: run backend server and verify it connects to PostgreSQL container
- [x] T120 [US6] Create scripts/setup_db.sh to run Alembic migrations: alembic upgrade head
- [x] T121 [US6] Test full stack: docker-compose up -d && sleep 5 && ./scripts/setup_db.sh && ./scripts/run_dev.sh

**Checkpoint**: Docker environment fully operational. PostgreSQL with pgvector running. Redis accessible. Backend connects successfully.

---

## Phase 9: User Story 7 - Testing Framework Setup (Priority: P3)

**Goal**: Configure pytest with fixtures, example tests, and coverage reporting to establish TDD culture

**Independent Test**: Run `pytest` and verify tests discover and execute successfully with coverage report generated

### Test Directory Structure

- [x] T122 [US7] Create tests/ directory mirroring src/ structure
- [x] T123 [US7] Create tests/__init__.py package marker
- [x] T124 [P] [US7] Create tests/unit/ directory for unit tests
- [x] T125 [P] [US7] Create tests/integration/ directory for integration tests
- [x] T126 [P] [US7] Create tests/fixtures/ directory for test data factories
- [x] T127 [P] [US7] Create tests/unit/__init__.py, tests/integration/__init__.py, tests/fixtures/__init__.py

### Pytest Configuration

- [x] T128 [US7] Verify pyproject.toml includes pytest configuration: testpaths=["tests"], python_files=["test_*.py"], python_classes=["Test*"], python_functions=["test_*"]
- [x] T129 [US7] Add pytest coverage options: --cov=src, --cov-report=term-missing, --cov-report=html
- [x] T130 [US7] Add pytest-asyncio configuration for async test support

### Shared Fixtures

- [x] T131 [US7] Create tests/conftest.py with shared fixtures
- [x] T132 [US7] Add test_db_engine fixture: creates async test database engine
- [x] T133 [US7] Add db_session fixture: provides async database session with automatic rollback
- [x] T134 [US7] Add test_client fixture: provides FastAPI TestClient for API testing
- [x] T135 [US7] Add mock_settings fixture: provides test configuration overrides

### Example Tests

- [x] T136 [P] [US7] Create tests/unit/test_config.py with configuration validation tests
- [x] T137 [P] [US7] Add test_settings_load_from_env() to verify environment variable loading
- [x] T138 [P] [US7] Add test_missing_required_config_raises_error() to verify validation
- [x] T139 [P] [US7] Create tests/unit/test_models.py with SQLAlchemy model tests
- [x] T140 [P] [US7] Add test_tenant_model_creation() to verify Tenant model works
- [x] T141 [P] [US7] Add test_user_tenant_relationship() to verify foreign key relationships
- [x] T142 [P] [US7] Create tests/integration/test_database.py with database connection tests
- [x] T143 [P] [US7] Add test_database_connection() to verify async engine connects
- [x] T144 [P] [US7] Add test_alembic_migrations() to verify migrations apply cleanly
- [x] T145 [P] [US7] Create tests/integration/test_api.py with API endpoint tests
- [x] T146 [P] [US7] Add test_health_endpoint_returns_200() using TestClient
- [x] T147 [P] [US7] Add test_health_endpoint_checks_database() to verify database health check
- [x] T148 [P] [US7] Create tests/fixtures/sample_data.py with test data factories (tenant, user, document)

### Testing & Validation

- [x] T149 [US7] Run pytest: verify all example tests pass with 0 failures
- [x] T150 [US7] Verify test discovery: ensure pytest finds all test files
- [x] T151 [US7] Verify coverage report: check coverage report generated in htmlcov/
- [x] T152 [US7] Verify fixtures work: test that db_session fixture provides working session
- [x] T153 [US7] Verify async tests work: ensure pytest-asyncio handles async test functions
- [x] T154 [US7] Add pytest command to scripts/run_tests.sh: pytest --cov=src --cov-report=html

**Checkpoint**: Testing framework fully configured. Example tests pass. Coverage reporting works. Developers can run `pytest` for immediate feedback.

---

## Phase 10: User Story 8 - Frontend Application Shell (Priority: P3)

**Goal**: Initialize Next.js 14 frontend with TypeScript, Tailwind CSS, App Router, and shadcn/ui

**Independent Test**: Run `npm run dev` in frontend/. Verify Next.js dev server starts. Access http://localhost:3000 and see landing page with Tailwind styling.

### Next.js Project Initialization

- [x] T155 [US8] Create frontend/ directory
- [x] T156 [US8] Initialize Next.js project: npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
- [x] T157 [US8] Review generated package.json and ensure dependencies: next, react, react-dom, typescript, tailwindcss, postcss, autoprefixer
- [x] T158 [US8] Review generated tsconfig.json and ensure strict mode enabled, path aliases configured (@/*)
- [x] T159 [US8] Review generated tailwind.config.js and ensure content paths include ./app/**, ./components/**

### Frontend Project Structure

- [x] T160 [P] [US8] Create frontend/app/layout.tsx with root layout, html/body tags, font configuration
- [x] T161 [P] [US8] Create frontend/app/page.tsx with landing page placeholder
- [x] T162 [P] [US8] Create frontend/app/globals.css with Tailwind directives (@tailwind base, components, utilities)
- [x] T163 [P] [US8] Create frontend/components/ directory for React components
- [x] T164 [P] [US8] Create frontend/components/ui/ directory for shadcn/ui components
- [x] T165 [P] [US8] Create frontend/components/layout/ directory for layout components (header, footer)
- [x] T166 [P] [US8] Create frontend/lib/ directory for utilities
- [x] T167 [P] [US8] Create frontend/lib/utils.ts with cn() utility for class name merging
- [x] T168 [P] [US8] Create frontend/lib/api-client.ts with fetch wrapper for backend API calls
- [x] T169 [P] [US8] Create frontend/public/ directory for static assets (if not exists)
- [x] T170 [P] [US8] Create frontend/__tests__/ directory for frontend tests

### shadcn/ui Setup

- [x] T171 [US8] Initialize shadcn/ui: npx shadcn-ui@latest init (choose default options)
- [x] T172 [US8] Verify components.json created with correct configuration
- [x] T173 [P] [US8] Install button component: npx shadcn-ui@latest add button
- [x] T174 [P] [US8] Install card component: npx shadcn-ui@latest add card

### API Client Configuration

- [x] T175 [US8] Implement healthCheck() function in lib/api-client.ts: fetches /api/v1/health
- [x] T176 [US8] Add API base URL to environment: create frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
- [x] T177 [US8] Add error handling to api-client.ts: throw on non-2xx responses with error details

### Landing Page Implementation

- [x] T178 [US8] Update frontend/app/page.tsx with AgenticOmni landing page content
- [x] T179 [US8] Add hero section with project title and description
- [x] T180 [US8] Add health check status indicator using api-client.ts
- [x] T181 [US8] Style with Tailwind CSS utilities: responsive layout, typography, colors
- [x] T182 [P] [US8] Create frontend/components/layout/Header.tsx with navigation
- [x] T183 [P] [US8] Create frontend/components/layout/Footer.tsx with copyright
- [x] T184 [US8] Import Header and Footer in app/layout.tsx

### Frontend Testing & Validation

- [x] T185 [US8] Add test scripts to frontend/package.json: "test": "jest", "test:watch": "jest --watch"
- [x] T186 [P] [US8] Create frontend/jest.config.js with React Testing Library configuration
- [x] T187 [P] [US8] Create frontend/__tests__/page.test.tsx with basic landing page test
- [x] T188 [US8] Run frontend dev server: cd frontend && npm run dev
- [x] T189 [US8] Verify server starts on http://localhost:3000
- [x] T190 [US8] Open browser and verify landing page renders with Tailwind styling
- [x] T191 [US8] Verify health check indicator: check that API call to backend works (if backend running)
- [x] T192 [US8] Verify responsive design: test page on mobile, tablet, desktop viewports
- [x] T193 [US8] Run frontend linter: npm run lint (verify no errors)
- [x] T194 (deferred - will add Vitest later) [US8] Run frontend tests: npm test (verify tests pass)

**Checkpoint**: Frontend fully operational. Next.js dev server runs. Landing page displays with Tailwind styling. API client can communicate with backend.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation updates, and validation

### Documentation

- [x] T195 [P] Update root README.md with complete setup instructions from quickstart.md
- [x] T196 [P] Add architecture diagram to docs/ showing 7 backend modules and frontend
- [x] T197 [P] Add CONTRIBUTING.md with development workflow, code standards, commit conventions
- [x] T198 [P] Update each module README.md with detailed purpose and future roadmap

### Code Quality

- [x] T199 [P] Run ruff linting on all Python files: ruff check src/ tests/ config/
- [x] T200 [P] Run ruff formatting: ruff format src/ tests/ config/
- [x] T201 [P] Run mypy type checking: mypy src/ config/
- [x] T202 [P] Fix any linting or type errors
- [x] T203 [P] Run frontend ESLint: cd frontend && npm run lint
- [x] T204 [P] Fix any frontend linting errors

### Validation Scripts

- [x] T205 Create scripts/validate_env.sh to check all required environment variables are set
- [x] T206 Add validation for directory structure: ensure all required directories exist
- [x] T207 Add validation for __init__.py files: ensure all Python packages properly marked
- [x] T208 Create scripts/full_setup.sh: runs docker-compose up, setup_db.sh, runs tests, starts servers
- [x] T209 Test full_setup.sh on clean environment: verify complete setup works end-to-end

### Final Integration Testing

- [x] T210 Run complete setup from quickstart.md: verify setup completes in < 15 minutes
- [x] T211 Verify docker-compose up starts all services within 30 seconds
- [x] T212 Verify health endpoint responds within 1 second
- [x] T213 Verify database migrations complete within 5 seconds
- [x] T214 Verify pytest runs all tests with 100% pass rate
- [x] T215 Verify ruff and mypy pass with zero errors
- [x] T216 Verify frontend dev server starts within 10 seconds
- [x] T217 Verify all Success Criteria from spec.md are met

### Security Review

- [x] T218 [P] Verify .env not committed to git (check .gitignore)
- [x] T219 [P] Verify secrets use environment variables, not hardcoded
- [x] T220 [P] Verify CORS origins configurable, not set to "*" in production
- [x] T221 [P] Add security headers to FastAPI middleware (HSTS, CSP placeholders)

**Final Checkpoint**: All Success Criteria met. Code quality checks pass. Full setup script works. Documentation complete. Ready for feature development.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies - can start immediately
- **Phase 2: User Story 1** (P1): Depends on Phase 1 (Setup)
- **Phase 3: User Story 2** (P1): Depends on Phase 2 (needs directory structure)
- **Phase 4: User Story 3** (P1): Depends on Phase 2 (needs directory structure)
- **Phase 5: Foundational**: Depends on Phases 2, 3, 4 (needs structure, dependencies, config)
- **Phase 6: User Story 4** (P2): Depends on Phase 5 (needs database connection)
- **Phase 7: User Story 5** (P2): Depends on Phase 5 (needs logging, config)
- **Phase 8: User Story 6** (P2): Depends on Phase 4 (needs User Story 4 database models for migration testing)
- **Phase 9: User Story 7** (P3): Depends on Phases 6, 7 (needs database and API to test)
- **Phase 10: User Story 8** (P3): Independent of backend phases, can start after Phase 1
- **Phase 11: Polish**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent after Setup - foundational directory structure
- **User Story 2 (P1)**: Depends on US1 - needs directory structure to install packages
- **User Story 3 (P1)**: Depends on US1 - needs directory structure for config files
- **User Story 4 (P2)**: Depends on US2, US3, Foundational - needs dependencies and database connection
- **User Story 5 (P2)**: Depends on US2, US3, Foundational - needs FastAPI dependencies and logging
- **User Story 6 (P2)**: Depends on US4 - needs database models for migration testing
- **User Story 7 (P3)**: Depends on US4, US5 - needs database and API to write example tests
- **User Story 8 (P3)**: Independent - can start immediately after US1, parallel with backend work

### Within Each User Story

- Setup tasks → Implementation tasks → Validation tasks
- [P] tasks within a phase can run in parallel (different files)
- Non-[P] tasks must wait for their specific dependencies (listed in task descriptions)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 (all __init__.py files) can run in parallel
- T004 (module READMEs) can run in parallel with T003, T005, T006

**Phase 2 (User Story 1)**:
- All validation tasks (T007, T008, T009) can run in parallel after implementation

**Phase 5 (Foundational)**:
- T038-T041 (logging setup) can run in parallel with T042-T046 (database connection)

**Phase 6 (User Story 4)**:
- T050-T055 (all 6 model files) can run in parallel - different files
- T070-T072 (repository scaffolding) can run in parallel with migration testing (T065-T069)

**Phase 7 (User Story 5)**:
- T079-T083 (all middleware files) can run in parallel - different files
- T085-T086 (health route setup) can run in parallel with middleware
- T094-T100 (validation tests) can be run in parallel by different team members

**Phase 8 (User Story 6)**:
- T107-T109 (Redis configuration) can run in parallel with postgres configuration
- T111-T112 (init script) can run in parallel with main docker-compose.yml work

**Phase 9 (User Story 7)**:
- T124-T127 (test directory structure) can run in parallel
- T136-T148 (all example test files) can run in parallel - different files

**Phase 10 (User Story 8)**:
- T160-T170 (frontend structure) can run in parallel - different files
- T173-T174 (shadcn components) can run in parallel
- T182-T183 (Header/Footer components) can run in parallel
- T186-T187 (Jest config and test) can run in parallel

**Phase 11 (Polish)**:
- T195-T198 (documentation) can all run in parallel
- T199-T204 (code quality checks) can all run in parallel
- T218-T221 (security review) can all run in parallel

---

## Parallel Example: User Story 4 (Database Schema)

```bash
# After completing T047-T049 (setup), launch all 6 model files together:
Task T050: "Create tenant.py model"
Task T051: "Create user.py model"
Task T052: "Create document.py model"
Task T053: "Create document_chunk.py model"
Task T054: "Create permission.py model"
Task T055: "Create processing_job.py model"

# While migrations are being created, scaffold repository layer in parallel:
Task T070: "Create repositories/ directory"
Task T071: "Create repositories/__init__.py"
Task T072: "Add placeholder comment"
```

---

## Parallel Example: User Story 5 (API Server)

```bash
# Launch all middleware files together:
Task T081: "Create logging.py middleware"
Task T082: "Create request_id.py middleware"
Task T083: "Create error_handler.py middleware"

# While middleware is being implemented, work on health endpoint:
Task T085: "Create routes/ directory"
Task T086: "Create routes/__init__.py"
Task T087: "Create health.py router"
```

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

**Goal**: Get to a working skeleton with basic structure, dependencies, and configuration

1. Complete Phase 1: Setup (T001-T006) - ~30 minutes
2. Complete Phase 2: User Story 1 (T007-T009) - ~15 minutes
3. Complete Phase 3: User Story 2 (T010-T020) - ~45 minutes
4. Complete Phase 4: User Story 3 (T021-T037) - ~45 minutes
5. Complete Phase 5: Foundational (T038-T046) - ~30 minutes
6. **STOP and VALIDATE**: Test that project structure, dependencies, and config work
7. **Total MVP Time**: ~3 hours

**Deliverable**: Working skeleton with structure, all dependencies installable, configuration management functional.

### Phase 1 Completion (Add P2 User Stories)

**Goal**: Add database schema, API server, and Docker environment

1. Complete Phase 6: User Story 4 - Database Schema (T047-T072) - ~2 hours
2. Complete Phase 7: User Story 5 - API Server (T073-T100) - ~2 hours
3. Complete Phase 8: User Story 6 - Docker Environment (T101-T121) - ~1 hour
4. **STOP and VALIDATE**: Run full stack with docker-compose, test health endpoint, run migrations
5. **Total Phase 1 Time**: ~5 hours

**Deliverable**: Complete backend infrastructure with database, API server, and Docker development environment.

### Phase 2 Completion (Add P3 User Stories)

**Goal**: Add testing framework and frontend

1. Complete Phase 9: User Story 7 - Testing Framework (T122-T154) - ~2 hours
2. Complete Phase 10: User Story 8 - Frontend Shell (T155-T194) - ~2 hours
3. **STOP and VALIDATE**: Run all tests, start frontend, verify end-to-end connectivity
4. **Total Phase 2 Time**: ~4 hours

**Deliverable**: Complete application skeleton with testing and frontend.

### Final Polish

1. Complete Phase 11: Polish & Cross-Cutting (T195-T221) - ~2 hours
2. **Final Validation**: Run through entire quickstart.md guide, verify all Success Criteria met

**Total Implementation Time**: ~15-16 hours for single developer, ~6-8 hours with team parallelization

### Parallel Team Strategy

With a team of 3 developers after completing foundational phases:

**Week 1: Foundation (Everyone Together)**
- Day 1: Phases 1-5 (Setup, US1-US3, Foundational) - Team collaboration
- **Checkpoint**: Structure, dependencies, config, logging, database connection ready

**Week 1-2: Parallel Development**
- **Developer A**: Phase 6 (User Story 4 - Database Schema)
- **Developer B**: Phase 7 (User Story 5 - API Server)
- **Developer C**: Phase 10 (User Story 8 - Frontend Shell)

**Week 2: Integration & Testing**
- **Developer A**: Phase 8 (User Story 6 - Docker Environment)
- **Developer B**: Phase 9 (User Story 7 - Testing Framework)
- **Developer C**: Frontend integration with backend health check

**Week 2: Final Polish**
- **Everyone**: Phase 11 (Documentation, code quality, validation)

---

## Notes

- **[P] marker**: Task can run in parallel with other [P] tasks in same phase (different files)
- **[US#] label**: Task belongs to specific user story for traceability
- **File paths**: All task descriptions include exact file paths for clarity
- **Independent testing**: Each user story has clear independent test criteria
- **Checkpoints**: Major checkpoints after each phase for validation
- **MVP focus**: First 3 user stories (P1) form minimum viable skeleton
- **Avoid**: Cross-story dependencies that break independence
- **Commit strategy**: Commit after completing each user story phase
- **Success Criteria**: All tasks mapped to Success Criteria from spec.md (SC-001 through SC-012)

---

**Task Generation Complete**: 221 tasks across 11 phases, organized by 8 user stories with clear dependencies and parallel opportunities.
