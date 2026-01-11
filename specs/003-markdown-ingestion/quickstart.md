# Quickstart: Markdown File Ingestion Development

**Feature**: 003-markdown-ingestion  
**Date**: 2026-01-10  
**Target Audience**: Backend developers implementing markdown parsing

## Overview

This quickstart guide helps developers set up their environment, understand the architecture, and begin implementing the markdown file ingestion feature. Follow these steps to get started quickly.

## Prerequisites

- Python 3.12+ installed
- PostgreSQL 14+ with pgvector extension
- Redis 7+ (for Dramatiq task queue)
- Docker and Docker Compose (optional, for local services)
- Git access to the repository

## Quick Setup (5 minutes)

### 1. Clone and Install Dependencies

```bash
# Clone repository (if not already done)
cd /Users/william.jiang/my-apps/ai-edocuments

# Activate virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies (includes marko for markdown parsing)
pip install -r requirements.txt

# Add new markdown-specific dependency
pip install python-frontmatter==1.1.0

# Update requirements.txt
pip freeze > requirements.txt
```

### 2. Start Required Services

```bash
# Option A: Using Docker Compose (recommended)
docker-compose up -d postgres redis

# Option B: Manual setup
# Start PostgreSQL on port 5432
# Start Redis on port 6379
```

### 3. Run Database Migrations

```bash
# Apply migrations to add markdown support tables
alembic upgrade head

# Verify tables created
psql -d agenticomni -c "\dt" | grep -E 'markdown|folder_batch|image_reference'
```

### 4. Start Development Servers

```bash
# Terminal 1: Start FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Dramatiq worker
dramatiq src.ingestion_parsing.tasks.parsing_tasks:broker --processes 4 --threads 8

# Terminal 3: (Optional) Monitor Redis queues
redis-cli MONITOR
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status": "healthy", "version": "0.2.0"}
```

---

## Architecture Overview

### Component Diagram

```text
┌──────────────┐
│   FastAPI    │  Upload markdown file
│   Routes     │◄────────────────────┐
└──────┬───────┘                     │
       │                             │
       ▼                             │
┌──────────────────┐                 │
│  UploadService   │  Validate file  │
│  + validators    │                 │
└──────┬───────────┘                 │
       │                             │
       ▼                             │
┌──────────────────┐                 │
│  Document Model  │  Save metadata  │
│  + FolderBatch   │                 │
└──────┬───────────┘                 │
       │                             │
       ▼                             │
┌───────────────────┐                │
│ Dramatiq Queue    │  Async parsing │
│ (parse_markdown)  │                │
└──────┬────────────┘                │
       │                             │
       ▼                             │
┌───────────────────┐                │
│ MarkdownParser    │  Parse content │
│ + frontmatter     │                │
│ + mermaid         │                │
│ + images          │                │
└──────┬────────────┘                │
       │                             │
       ▼                             │
┌───────────────────┐                │
│ ChunkingService   │  RAG chunks    │
│ (512 tokens/50    │                │
│  overlap)         │                │
└──────┬────────────┘                │
       │                             │
       ▼                             │
┌───────────────────┐                │
│ pgvector          │  Embeddings    │
│ (1536-dim)        │                │
└───────────────────┘                │
                                     │
       RAG Query  ───────────────────┘
```

### Key Files and Their Purposes

| File | Purpose | Status |
|------|---------|--------|
| `src/ingestion_parsing/parsers/markdown_parser.py` | Main markdown parser implementing BaseParser | 🆕 To create |
| `src/ingestion_parsing/parsers/markdown/frontmatter.py` | YAML frontmatter extraction | 🆕 To create |
| `src/ingestion_parsing/parsers/markdown/mermaid.py` | Mermaid diagram detection | 🆕 To create |
| `src/ingestion_parsing/parsers/markdown/image_extractor.py` | Image reference extraction | 🆕 To create |
| `src/ingestion_parsing/services/folder_service.py` | Folder traversal and batch processing | 🆕 To create |
| `src/ingestion_parsing/tasks/folder_tasks.py` | Dramatiq tasks for folder batches | 🆕 To create |
| `src/storage_indexing/models/markdown_metadata.py` | MarkdownMetadata ORM model | 🆕 To create |
| `src/storage_indexing/models/folder_batch.py` | FolderBatch ORM model | 🆕 To create |
| `src/storage_indexing/models/image_reference.py` | ImageReference ORM model | 🆕 To create |
| `src/api/routes/documents.py` | Extended with folder upload endpoint | ✏️ To modify |
| `src/ingestion_parsing/parsers/parser_factory.py` | Add markdown MIME types | ✏️ To modify |

---

## Development Workflow

### Step 1: Implement MarkdownParser

**File**: `src/ingestion_parsing/parsers/markdown_parser.py`

```python
"""Markdown document parser using marko and python-frontmatter."""

from pathlib import Path
from typing import Any

import marko
from marko.ext.gfm import GFM
import frontmatter
import structlog

from src.ingestion_parsing.parsers.base import BaseParser
from src.ingestion_parsing.models.parsing_result import ParsingResult

logger = structlog.get_logger(__name__)


class MarkdownParser(BaseParser):
    """Parser for markdown documents (.md, .markdown)."""
    
    def __init__(self) -> None:
        """Initialize markdown parser with GFM extensions."""
        self.markdown_parser = marko.Markdown(extensions=[GFM])
        logger.info("MarkdownParser initialized with GFM support")
    
    def parse(self, file_path: str) -> ParsingResult:
        """Parse markdown document and extract all content and metadata.
        
        Args:
            file_path: Path to .md file
            
        Returns:
            ParsingResult with text, metadata, and structural elements
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        # Read file content
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f"File must be UTF-8 encoded: {e}")
        
        # Extract frontmatter
        post = frontmatter.loads(content)
        frontmatter_data = post.metadata
        markdown_content = post.content
        
        # Parse markdown AST
        ast = self.markdown_parser.parse(markdown_content)
        
        # Extract text content
        text = self.extract_text(file_path)
        
        # Extract metadata
        metadata = self.extract_metadata(file_path)
        metadata['frontmatter'] = frontmatter_data
        
        return ParsingResult(
            text_content=text,
            metadata=metadata,
            page_count=1,  # Markdown is single "page"
            language='en',  # TODO: Add language detection
        )
    
    def extract_text(self, file_path: str) -> str:
        """Extract plain text from markdown.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Plain text content
        """
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        
        # Remove frontmatter
        post = frontmatter.loads(content)
        markdown_content = post.content
        
        # Parse to AST and extract text
        ast = self.markdown_parser.parse(markdown_content)
        
        # TODO: Walk AST and extract text from all nodes
        # For now, return raw markdown (will be improved)
        return markdown_content
    
    def extract_metadata(self, file_path: str) -> dict[str, Any]:
        """Extract markdown-specific metadata.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Dictionary with metadata (heading_count, code_block_count, etc.)
        """
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        
        post = frontmatter.loads(content)
        ast = self.markdown_parser.parse(post.content)
        
        # Count structural elements
        heading_count = 0
        code_block_count = 0
        mermaid_diagram_count = 0
        table_count = 0
        
        # TODO: Walk AST and count elements
        # This is a placeholder - full implementation in subtask
        
        return {
            'heading_count': heading_count,
            'code_block_count': code_block_count,
            'mermaid_diagram_count': mermaid_diagram_count,
            'table_count': table_count,
            'has_yaml_frontmatter': bool(post.metadata),
        }
    
    def supports_format(self, mime_type: str) -> bool:
        """Check if this parser supports the MIME type.
        
        Args:
            mime_type: MIME type to check
            
        Returns:
            True if markdown MIME type
        """
        return mime_type in ('text/markdown', 'text/x-markdown', 'text/plain')
```

### Step 2: Register Markdown Parser

**File**: `src/ingestion_parsing/parsers/parser_factory.py` (modify)

```python
from src.ingestion_parsing.parsers.markdown_parser import MarkdownParser

class ParserFactory:
    _parsers: dict[str, type[BaseParser]] = {
        "application/pdf": PDFParser,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DOCXParser,
        "text/plain": TXTParser,
        "text/markdown": MarkdownParser,      # Add this
        "text/x-markdown": MarkdownParser,    # Add this
    }
```

### Step 3: Create Database Models

**File**: `src/storage_indexing/models/markdown_metadata.py`

```python
"""MarkdownMetadata ORM model."""

from sqlalchemy import Column, BigInteger, Integer, Boolean, Text, TIMESTAMP, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.storage_indexing.database import Base


class MarkdownMetadata(Base):
    """Markdown-specific metadata for documents."""
    
    __tablename__ = 'markdown_metadata'
    
    id = Column(BigInteger, primary_key=True)
    document_id = Column(
        BigInteger,
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False,
        unique=True
    )
    frontmatter = Column(JSONB)
    heading_count = Column(Integer, default=0)
    code_block_count = Column(Integer, default=0)
    mermaid_diagram_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    link_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    link_urls = Column(ARRAY(Text))
    has_yaml_frontmatter = Column(Boolean, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    document = relationship(
        'Document',
        back_populates='markdown_metadata',
        uselist=False
    )
    
    __table_args__ = (
        CheckConstraint(
            'heading_count >= 0 AND code_block_count >= 0 AND mermaid_diagram_count >= 0 AND table_count >= 0',
            name='check_counts_positive'
        ),
    )
    
    def __repr__(self) -> str:
        return f"<MarkdownMetadata(document_id={self.document_id}, headings={self.heading_count})>"
```

### Step 4: Write Unit Tests

**File**: `tests/unit/test_markdown_parser.py`

```python
"""Unit tests for MarkdownParser."""

import pytest
from pathlib import Path

from src.ingestion_parsing.parsers.markdown_parser import MarkdownParser


@pytest.fixture
def markdown_parser():
    """Create MarkdownParser instance."""
    return MarkdownParser()


@pytest.fixture
def sample_markdown_file(tmp_path):
    """Create sample markdown file for testing."""
    content = """---
title: Test Document
author: John Doe
tags: [test, markdown]
---

# Main Heading

This is a paragraph with **bold** and *italic* text.

## Subheading

- List item 1
- List item 2

```python
def hello():
    print("Hello, world!")
```

![Test image](https://example.com/image.png)
"""
    file_path = tmp_path / "test.md"
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)


def test_parse_markdown_file(markdown_parser, sample_markdown_file):
    """Test parsing a valid markdown file."""
    result = markdown_parser.parse(sample_markdown_file)
    
    assert result is not None
    assert result.text_content
    assert 'frontmatter' in result.metadata
    assert result.metadata['frontmatter']['title'] == 'Test Document'


def test_extract_frontmatter(markdown_parser, sample_markdown_file):
    """Test YAML frontmatter extraction."""
    metadata = markdown_parser.extract_metadata(sample_markdown_file)
    
    # Frontmatter will be in ParsingResult metadata
    result = markdown_parser.parse(sample_markdown_file)
    frontmatter = result.metadata['frontmatter']
    
    assert frontmatter['title'] == 'Test Document'
    assert frontmatter['author'] == 'John Doe'
    assert 'test' in frontmatter['tags']


def test_parse_markdown_without_frontmatter(markdown_parser, tmp_path):
    """Test parsing markdown without frontmatter."""
    content = "# Just a heading\n\nAnd a paragraph."
    file_path = tmp_path / "no_frontmatter.md"
    file_path.write_text(content, encoding='utf-8')
    
    result = markdown_parser.parse(str(file_path))
    
    assert result.text_content
    assert result.metadata['frontmatter'] == {}


def test_parse_invalid_encoding(markdown_parser, tmp_path):
    """Test error handling for non-UTF-8 file."""
    file_path = tmp_path / "invalid.md"
    # Write file with Latin-1 encoding
    file_path.write_bytes("Café".encode('latin-1'))
    
    with pytest.raises(ValueError, match="UTF-8 encoded"):
        markdown_parser.parse(str(file_path))


def test_supports_markdown_mime_types(markdown_parser):
    """Test MIME type support detection."""
    assert markdown_parser.supports_format('text/markdown')
    assert markdown_parser.supports_format('text/x-markdown')
    assert markdown_parser.supports_format('text/plain')
    assert not markdown_parser.supports_format('application/pdf')
```

### Step 5: Run Tests

```bash
# Run markdown parser tests
pytest tests/unit/test_markdown_parser.py -v

# Run with coverage
pytest tests/unit/test_markdown_parser.py --cov=src.ingestion_parsing.parsers.markdown_parser --cov-report=term-missing

# Run all ingestion tests
pytest tests/unit/ tests/integration/ -k markdown
```

---

## Testing the Feature

### Manual API Testing

#### 1. Upload Single Markdown File

```bash
# Create test markdown file
cat > test.md << 'EOF'
---
title: API Documentation
author: Jane Smith
tags: [api, docs]
---

# API Overview

This document describes our REST API.

## Authentication

Use Bearer tokens for authentication.

```python
headers = {"Authorization": "Bearer your_token"}
```

![API Flow](https://example.com/api-flow.png)
EOF

# Upload to API
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.md" \
  -F "tenant_id=1" \
  -F "user_id=1" \
  -H "Authorization: Bearer your_token"

# Expected response:
# {
#   "document_id": 1001,
#   "filename": "doc_20260110_abc123.md",
#   "mime_type": "text/markdown",
#   "status": "pending",
#   "parsing_job_id": 5001
# }
```

#### 2. Check Document Status

```bash
# Poll for parsing completion
curl http://localhost:8000/api/v1/documents/1001 \
  -H "Authorization: Bearer your_token"

# Expected response (when completed):
# {
#   "document_id": 1001,
#   "status": "completed",
#   "chunks_count": 3,
#   ...
# }
```

#### 3. Query Markdown Metadata

```bash
# Get markdown-specific metadata
curl http://localhost:8000/api/v1/documents/1001/markdown-metadata \
  -H "Authorization: Bearer your_token"

# Expected response:
# {
#   "document_id": 1001,
#   "frontmatter": {
#     "title": "API Documentation",
#     "author": "Jane Smith",
#     "tags": ["api", "docs"]
#   },
#   "heading_count": 2,
#   "code_block_count": 1,
#   "image_count": 1,
#   ...
# }
```

#### 4. Upload Folder

```bash
# Create test folder structure
mkdir -p test-docs/api test-docs/guides
echo "# API Overview" > test-docs/api/overview.md
echo "# Authentication Guide" > test-docs/guides/auth.md
echo "# Getting Started" > test-docs/quickstart.md

# Upload folder (using multipart form with file paths)
# Note: Actual implementation may require client library for folder uploads

curl -X POST http://localhost:8000/api/v1/documents/upload-folder \
  -F "files=@test-docs/api/overview.md;filename=api/overview.md" \
  -F "files=@test-docs/guides/auth.md;filename=guides/auth.md" \
  -F "files=@test-docs/quickstart.md;filename=quickstart.md" \
  -F "tenant_id=1" \
  -F "user_id=1" \
  -F "folder_name=test-docs" \
  -H "Authorization: Bearer your_token"

# Expected response:
# {
#   "batch_id": 123,
#   "total_files_discovered": 3,
#   "status": "processing",
#   "status_url": "/api/v1/documents/folder-batches/123"
# }
```

#### 5. Check Folder Batch Progress

```bash
# Poll batch status
curl http://localhost:8000/api/v1/documents/folder-batches/123 \
  -H "Authorization: Bearer your_token"

# Expected response:
# {
#   "batch_id": 123,
#   "total_files_discovered": 3,
#   "files_processed": 3,
#   "files_failed": 0,
#   "status": "completed",
#   "progress_percentage": 100.0
# }
```

---

## Integration Testing

### Test Folder Upload Workflow

**File**: `tests/integration/test_markdown_folder_upload.py`

```python
"""Integration tests for folder upload."""

import pytest
from pathlib import Path

from src.api.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def test_folder(tmp_path):
    """Create test folder with multiple markdown files."""
    folder = tmp_path / "test-docs"
    folder.mkdir()
    
    (folder / "doc1.md").write_text("# Document 1\n\nContent here.")
    (folder / "doc2.md").write_text("# Document 2\n\nMore content.")
    
    subfolder = folder / "api"
    subfolder.mkdir()
    (subfolder / "api-doc.md").write_text("# API\n\nAPI documentation.")
    
    return folder


def test_upload_folder_creates_batch(test_folder, test_client):
    """Test uploading folder creates FolderBatch."""
    # Upload folder
    files = [
        ("files", ("doc1.md", open(test_folder / "doc1.md", "rb"), "text/markdown")),
        ("files", ("doc2.md", open(test_folder / "doc2.md", "rb"), "text/markdown")),
        ("files", ("api/api-doc.md", open(test_folder / "api" / "api-doc.md", "rb"), "text/markdown")),
    ]
    
    response = test_client.post(
        "/api/v1/documents/upload-folder",
        files=files,
        data={"tenant_id": 1, "user_id": 1, "folder_name": "test-docs"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["total_files_discovered"] == 3
    assert data["status"] in ["discovering", "processing"]
    assert "batch_id" in data
```

---

## Debugging Tips

### 1. Check Dramatiq Logs

```bash
# View Dramatiq worker logs
tail -f logs/dramatiq.log

# Check for parsing errors
grep "ERROR" logs/dramatiq.log | grep markdown
```

### 2. Inspect Database State

```bash
# Connect to PostgreSQL
psql -d agenticomni

# Check markdown metadata
SELECT d.id, d.filename, m.heading_count, m.has_yaml_frontmatter
FROM documents d
JOIN markdown_metadata m ON d.id = m.document_id
WHERE d.mime_type = 'text/markdown';

# Check folder batches
SELECT * FROM folder_batches ORDER BY created_at DESC LIMIT 5;

# Check image references
SELECT d.filename, i.image_url, i.alt_text, i.ocr_pending
FROM image_references i
JOIN documents d ON i.document_id = d.id;
```

### 3. Monitor Redis Queues

```bash
# Check queue lengths
redis-cli LLEN dramatiq:default

# View pending tasks
redis-cli LRANGE dramatiq:default 0 10
```

---

## Common Issues and Solutions

### Issue: "File must be UTF-8 encoded"

**Cause**: Markdown file uses non-UTF-8 encoding (Latin-1, UTF-16, etc.)

**Solution**:
```bash
# Convert file to UTF-8
iconv -f latin1 -t utf-8 input.md > output.md

# Or in Python:
# content = path.read_bytes().decode('latin-1').encode('utf-8')
```

### Issue: "No parser available for MIME type"

**Cause**: Parser not registered in ParserFactory

**Solution**: Add markdown MIME types to `parser_factory.py`:
```python
"text/markdown": MarkdownParser,
"text/x-markdown": MarkdownParser,
```

### Issue: "Folder batch stuck in 'processing' status"

**Cause**: Dramatiq worker not running or crashed

**Solution**:
```bash
# Restart Dramatiq worker
dramatiq src.ingestion_parsing.tasks.parsing_tasks:broker --processes 4

# Check for stuck tasks
redis-cli LRANGE dramatiq:default 0 -1
```

---

## Performance Optimization

### Profiling Markdown Parsing

```python
import cProfile
import pstats

# Profile parsing
cProfile.run('parser.parse("large_file.md")', 'profile_stats')

# Analyze results
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Benchmark Results

Expected performance targets:
- 10,000-line markdown: <30 seconds (including chunking)
- Folder with 100 files: <5 minutes
- Frontmatter extraction: <50ms per file

---

## Next Steps

1. **Implement Core Parser**: Start with `MarkdownParser` basic functionality
2. **Add Frontmatter**: Implement `frontmatter.py` utility
3. **Add Mermaid Detection**: Implement `mermaid.py` utility
4. **Add Image Extraction**: Implement `image_extractor.py`
5. **Implement Folder Service**: Create `folder_service.py` for batch processing
6. **Write Tests**: Comprehensive unit and integration tests
7. **API Integration**: Add folder upload endpoint
8. **Documentation**: Update API docs and user guides

**Recommended Implementation Order** (see `/speckit.tasks` for detailed breakdown):
1. MarkdownParser skeleton
2. Database migrations
3. Unit tests for parser
4. Frontmatter extraction
5. Folder traversal service
6. API endpoints
7. Integration tests
8. Performance optimization

---

## Resources

- **Marko Documentation**: https://marko-py.readthedocs.io/
- **Python Frontmatter**: https://python-frontmatter.readthedocs.io/
- **CommonMark Spec**: https://commonmark.org/
- **GitHub Flavored Markdown**: https://github.github.com/gfm/
- **Internal Docs**: `/docs/IMPLEMENTATION.md`

## Getting Help

- **Slack**: #markdown-ingestion-dev
- **Issues**: GitHub Issues with `feature/markdown-ingestion` label
- **Code Review**: Tag @backend-team for reviews

---

**Happy Coding!** 🚀

