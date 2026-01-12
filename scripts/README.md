# Scripts Directory

This directory contains utility scripts for development, testing, deployment, and maintenance of the AgenticOmni application.

**Last Updated**: 2026-01-12

---

## 📋 Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| **Development** |
| `run_dev.sh` | Start development server | `./scripts/run_dev.sh` |
| `start_all.sh` | Show startup instructions | `./scripts/start_all.sh` |
| `start_workers.sh` | Start Dramatiq workers | `./scripts/start_workers.sh` |
| `restart_backend.sh` | Restart backend server | `./scripts/restart_backend.sh` |
| **Database** |
| `check_db_status.sh` | Check database status | `./scripts/check_db_status.sh` |
| `reset_databases.sh` | Reset all databases | `./scripts/reset_databases.sh` |
| `setup_db.sh` | Setup database | `./scripts/setup_db.sh` |
| `init_db.sql` | Initial DB schema | Used by setup scripts |
| `inspect_db.py` | Inspect database contents | `python scripts/inspect_db.py` |
| `seed_database.py` | Seed test data | `python scripts/seed_database.py` |
| **Embeddings & ML** |
| `generate_embeddings.py` | Generate embeddings | `python scripts/generate_embeddings.py` |
| `download_models.py` | Download ML models | `python scripts/download_models.py` |
| `verify_ollama.sh` | Verify Ollama setup | `./scripts/verify_ollama.sh` |
| `verify_pgvector.py` | Verify pgvector | `python scripts/verify_pgvector.py` |
| **Testing** |
| `run_tests.sh` | Run test suite | `./scripts/run_tests.sh` |
| `test_parsers.py` | Test document parsers | `python scripts/test_parsers.py` |
| `test_upload.sh` | Test file upload | `./scripts/test_upload.sh` |
| `test_workflow.sh` | Test full workflow | `./scripts/test_workflow.sh` |
| **Setup & Validation** |
| `full_setup.sh` | Complete setup from scratch | `./scripts/full_setup.sh` |
| `setup_storage.sh` | Setup storage directories | `./scripts/setup_storage.sh` |
| `validate_env.sh` | Validate environment | `./scripts/validate_env.sh` |
| `validate_docs.py` | Validate documentation | `python scripts/validate_docs.py` |
| `validate_ocr_setup.py` | Validate OCR setup | `python scripts/validate_ocr_setup.py` |
| `validate_structure.py` | Validate project structure | `python scripts/validate_structure.py` |
| **Utilities** |
| `resumable_upload.py` | Upload large files | `python scripts/resumable_upload.py <file>` |

---

## 🚀 Development Scripts

### `run_dev.sh`
Start the FastAPI development server with auto-reload.

```bash
./scripts/run_dev.sh
```

**Features:**
- Auto-reload on code changes
- Runs on http://0.0.0.0:8000
- Shows API docs URL
- Environment: development mode

**Requirements:**
- Virtual environment activated
- `.env` file configured
- PostgreSQL and Redis running

---

### `start_all.sh`
Display instructions for starting all services (backend, frontend, Ollama).

```bash
./scripts/start_all.sh
```

**Output:**
- Terminal 1: Backend server commands
- Terminal 2: Frontend server commands
- Terminal 3: Ollama server commands
- Service URLs and health checks

---

### `start_workers.sh`
Start Dramatiq worker processes for background task processing.

```bash
./scripts/start_workers.sh
```

**Features:**
- Starts document parsing workers
- Starts embedding generation workers
- Connects to Redis broker
- Handles async job processing

**Environment Variables:**
- `DRAMATIQ_BROKER_URL`: Redis connection URL
- `MAX_CONCURRENT_JOBS`: Worker concurrency limit

---

### `restart_backend.sh`
Restart the backend API server (useful after code changes).

```bash
./scripts/restart_backend.sh
```

**Actions:**
- Kills existing uvicorn processes
- Waits for graceful shutdown
- Starts fresh server instance
- Displays startup logs

---

## 💾 Database Scripts

### `check_db_status.sh`
Check database connection and display table statistics.

```bash
./scripts/check_db_status.sh
```

**Output:**
- Connection status
- Table row counts
- Document statistics
- Embedding statistics
- pgvector extension status

---

### `reset_databases.sh`
**⚠️ DESTRUCTIVE** - Reset all databases to clean state.

```bash
./scripts/reset_databases.sh
```

**Actions:**
- Drops all tables
- Recreates schema
- Resets sequences
- Clears Redis cache
- Re-applies migrations

**Use Cases:**
- Fresh development start
- After major schema changes
- Clearing test data

---

### `setup_db.sh`
Initialize database with schema and extensions.

```bash
./scripts/setup_db.sh
```

**Actions:**
- Creates database if needed
- Installs pgvector extension
- Runs Alembic migrations
- Verifies connection

---

### `inspect_db.py`
Interactive database inspection tool.

```bash
python scripts/inspect_db.py
```

**Features:**
- Query tables
- View schema
- Check constraints
- Inspect indexes
- Export data

---

### `seed_database.py`
Seed database with test data.

```bash
python scripts/seed_database.py
```

**Creates:**
- Test tenants
- Sample documents
- Dummy chunks
- Test users
- Processing jobs

**Options:**
```bash
python scripts/seed_database.py --tenants 3 --docs 10
```

---

## 🤖 Embeddings & ML Scripts

### `generate_embeddings.py`
Generate vector embeddings for document chunks using Ollama.

```bash
# Generate embeddings for all unembedded chunks
python scripts/generate_embeddings.py

# Filter by tenant
python scripts/generate_embeddings.py --tenant-id 1

# Regenerate all (force)
python scripts/generate_embeddings.py --force
```

**Requirements:**
- Ollama running on localhost:11434
- nomic-embed-text model pulled
- Document chunks in database

**Environment Variables:**
- `OLLAMA_BASE_URL`: Ollama API endpoint
- `EMBEDDING_MODEL`: Model name (default: nomic-embed-text:latest)
- `EMBEDDING_DIMENSION`: Vector dimensions (default: 768)

---

### `download_models.py`
Download and cache ML models (embedding, OCR, etc.).

```bash
python scripts/download_models.py
```

**Downloads:**
- Embedding models
- OCR models (PaddleOCR)
- Tokenizer models
- Language models

**Options:**
```bash
python scripts/download_models.py --model-type embedding
python scripts/download_models.py --cache-dir ./models
```

---

### `verify_ollama.sh`
Verify Ollama installation and model availability.

```bash
./scripts/verify_ollama.sh
```

**Checks:**
- Ollama service running
- API accessibility
- Installed models
- Model compatibility
- Embedding dimensions

---

### `verify_pgvector.py`
Verify pgvector extension is installed and configured.

```bash
python scripts/verify_pgvector.py
```

**Validates:**
- Extension installed
- Vector operations working
- Index performance
- Dimension compatibility

---

## 🧪 Testing Scripts

### `run_tests.sh`
Run the full test suite with coverage.

```bash
./scripts/run_tests.sh
```

**Features:**
- Runs all unit tests
- Runs integration tests
- Generates coverage report
- Displays summary

**Options:**
```bash
./scripts/run_tests.sh --unit          # Unit tests only
./scripts/run_tests.sh --integration   # Integration tests only
./scripts/run_tests.sh --verbose       # Verbose output
```

---

### `test_parsers.py`
Test document parser implementations.

```bash
python scripts/test_parsers.py
```

**Tests:**
- PDF parsing (Docling)
- DOCX parsing
- Markdown parsing
- TXT parsing
- Chunking strategies

**Output:**
- Parser performance metrics
- Parsing accuracy
- Error handling
- Edge cases

---

### `test_upload.sh`
Test file upload endpoints.

```bash
./scripts/test_upload.sh path/to/file.pdf
```

**Tests:**
- Single file upload
- Batch upload
- Validation
- Error handling
- Progress tracking

---

### `test_workflow.sh`
Test complete end-to-end workflow.

```bash
./scripts/test_workflow.sh
```

**Workflow:**
1. Upload document
2. Wait for parsing
3. Generate embeddings
4. Perform search
5. Verify results
6. Cleanup

---

## ⚙️ Setup & Validation Scripts

### `full_setup.sh`
Complete setup from scratch (new developers).

```bash
./scripts/full_setup.sh
```

**Steps:**
1. Check prerequisites
2. Create .env file
3. Start Docker services
4. Create virtual environment
5. Install dependencies
6. Run migrations

---

### `setup_storage.sh`
Setup storage directories for uploads.

```bash
./scripts/setup_storage.sh
```

**Creates:**
- `./uploads/` - permanent storage
- `./tmp/uploads/` - temporary uploads
- Sets proper permissions
- Creates .gitkeep files

---

### `validate_env.sh`
Validate environment variables and configuration.

```bash
./scripts/validate_env.sh
```

**Validates:**
- Required variables set
- Database URL format
- Redis URL format
- API configuration
- CORS settings
- Storage paths

---

### `validate_docs.py`
Validate documentation completeness and quality.

```bash
python scripts/validate_docs.py
```

**Checks:**
- Markdown syntax
- Broken links
- Missing sections
- Outdated content
- Version consistency

---

### `validate_ocr_setup.py`
Validate OCR components are installed and working.

```bash
python scripts/validate_ocr_setup.py
```

**Validates:**
- PaddleOCR installed
- Tesseract available
- Models downloaded
- GPU availability
- Test OCR operations

---

### `validate_structure.py`
Validate project directory structure.

```bash
python scripts/validate_structure.py
```

**Checks:**
- Required directories exist
- Required files present
- Proper permissions
- Configuration files
- Module structure

---

## 🔧 Utility Scripts

### `resumable_upload.py`
Upload large files with resume capability.

```bash
python scripts/resumable_upload.py large-file.pdf
```

**Features:**
- Chunked uploads (10MB chunks)
- Resume on failure
- Progress tracking
- Retry logic
- Checksum validation

**Options:**
```bash
python scripts/resumable_upload.py \
  --file large-document.pdf \
  --tenant-id 1 \
  --user-id 1 \
  --chunk-size 5242880
```

---

## 📝 Common Workflows

### Fresh Development Start

```bash
# 1. Reset database
./scripts/reset_databases.sh

# 2. Seed test data
python scripts/seed_database.py

# 3. Generate embeddings
python scripts/generate_embeddings.py

# 4. Start services
./scripts/start_all.sh
```

### Deploy to Production

```bash
# 1. Validate environment
./scripts/validate_env.sh

# 2. Run tests
./scripts/run_tests.sh

# 3. Check database
./scripts/check_db_status.sh

# 4. Validate documentation
python scripts/validate_docs.py
```

### Troubleshooting

```bash
# Check all validators
./scripts/validate_env.sh
./scripts/validate_structure.py
./scripts/verify_ollama.sh
python scripts/verify_pgvector.py

# Test components
python scripts/test_parsers.py
./scripts/test_upload.sh
```

---

## 🔒 Security Notes

**Sensitive Scripts:**
- `reset_databases.sh` - Destructive operation
- `seed_database.py` - Inserts test data

**Production Usage:**
- Never run `reset_databases.sh` in production
- Review `seed_database.py` before production use
- Validate environment before deployment

---

## 🛠️ Development Guidelines

### Creating New Scripts

1. **Use proper shebang**:
   - Shell scripts: `#!/usr/bin/env bash`
   - Python scripts: `#!/usr/bin/env python3`

2. **Add documentation**:
   - Brief description at top
   - Usage examples
   - Environment variables
   - Exit codes

3. **Error handling**:
   - Use `set -e` in bash scripts
   - Check prerequisites
   - Provide helpful error messages

4. **Make executable**:
   ```bash
   chmod +x scripts/new-script.sh
   ```

5. **Update this README**:
   - Add to quick reference table
   - Add detailed section
   - Update workflows if applicable

### Script Naming Conventions

- `*.sh` - Bash scripts
- `*.py` - Python scripts
- `*.sql` - SQL scripts
- Use `_` separators (snake_case)
- Descriptive names (verb + noun)

---

## 📚 Additional Resources

- **Documentation**: `/docs/` directory
- **Main README**: `../README.md`
- **Quick Start**: `../docs/quickstart.md`
- **Environment Config**: `../docs/environment.md`

---

**Maintained by**: AgenticOmni Development Team  
**Project**: [AgenticOmni](https://github.com/williamjxj/AgenticOmni)
