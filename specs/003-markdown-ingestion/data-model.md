# Data Model: Markdown File Ingestion

**Feature**: 003-markdown-ingestion  
**Date**: 2026-01-10  
**Status**: Design Complete

## Overview

This document defines the data model for markdown file ingestion, including new entities for markdown-specific metadata, folder batch processing, and image references. The design extends existing models (Document, Chunk, ParsingJob) without breaking changes.

## Entity Relationship Diagram

```text
┌─────────────┐
│   Tenant    │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────────┐          ┌──────────────────┐
│  FolderBatch    │          │    Document      │
│─────────────────│◄─────────│──────────────────│
│ id              │  1:N     │ id               │
│ tenant_id       │          │ tenant_id        │
│ folder_path     │          │ filename         │
│ total_files     │          │ mime_type        │
│ files_processed │          │ folder_batch_id  │◄────┐
│ files_failed    │          │ file_path        │     │
│ status          │          │ status           │     │
│ created_at      │          └────────┬─────────┘     │
└─────────────────┘                   │               │
                                      │ 1:1           │
                                      ▼               │
                          ┌────────────────────┐      │
                          │ MarkdownMetadata   │      │
                          │────────────────────│      │
                          │ document_id        │      │
                          │ frontmatter        │      │
                          │ heading_count      │      │
                          │ code_block_count   │      │
                          │ mermaid_count      │      │
                          │ table_count        │      │
                          │ link_urls          │      │
                          └────────────────────┘      │
                                                      │
                ┌──────────────────────────────────────┘
                │ 1:N
                ▼
    ┌─────────────────────┐
    │  ImageReference     │
    │─────────────────────│
    │ id                  │
    │ document_id         │
    │ image_url           │
    │ alt_text            │
    │ is_local_path       │
    │ is_base64           │
    │ resolved_path       │
    │ ocr_pending         │
    └─────────────────────┘

                Document
                   │ 1:N
                   ▼
            ┌────────────┐
            │   Chunk    │  (existing, reused)
            │────────────│
            │ id         │
            │ document_id│
            │ content    │
            │ tokens     │
            │ embedding  │
            └────────────┘
```

## Entity Definitions

### 1. FolderBatch (New Entity)

**Purpose**: Track batch upload of folders containing multiple markdown files

**Table Name**: `folder_batches`

**Schema**:
```sql
CREATE TABLE folder_batches (
    id BIGSERIAL PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    folder_path TEXT NOT NULL,
    original_folder_name VARCHAR(500) NOT NULL,
    total_files_discovered INTEGER DEFAULT 0,
    files_processed INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'discovering',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_folder_batch_tenant FOREIGN KEY (tenant_id) 
        REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT fk_folder_batch_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT check_files_counts CHECK (files_processed <= total_files_discovered),
    CONSTRAINT check_status CHECK (
        status IN ('discovering', 'processing', 'completed', 'partial_failure', 'failed')
    )
);

-- Indexes
CREATE INDEX idx_folder_batches_tenant_id ON folder_batches(tenant_id);
CREATE INDEX idx_folder_batches_user_id ON folder_batches(user_id);
CREATE INDEX idx_folder_batches_status ON folder_batches(status);
CREATE INDEX idx_folder_batches_created_at ON folder_batches(created_at DESC);
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique batch identifier |
| tenant_id | BIGINT | NOT NULL, FK | Multi-tenant isolation |
| user_id | BIGINT | NOT NULL, FK | User who initiated upload |
| folder_path | TEXT | NOT NULL | Absolute path to uploaded folder |
| original_folder_name | VARCHAR(500) | NOT NULL | Original folder name from upload |
| total_files_discovered | INTEGER | DEFAULT 0 | Count of .md files found in traversal |
| files_processed | INTEGER | DEFAULT 0 | Count of successfully parsed files |
| files_failed | INTEGER | DEFAULT 0 | Count of files that failed parsing |
| status | VARCHAR(50) | NOT NULL | Current batch status (enum) |
| error_message | TEXT | NULLABLE | Error details if batch failed |
| created_at | TIMESTAMP | NOT NULL | Batch creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last status update timestamp |
| completed_at | TIMESTAMP | NULLABLE | Batch completion timestamp |

**Status Values**:
- `discovering`: Folder traversal in progress
- `processing`: Files discovered, parsing in progress
- `completed`: All files processed successfully
- `partial_failure`: Some files failed, others succeeded
- `failed`: Batch failed (discovery error, quota exceeded, etc.)

**Computed Properties** (application layer):
- `progress_percentage`: `(files_processed / total_files_discovered) * 100`
- `is_complete`: `status IN ('completed', 'partial_failure', 'failed')`
- `has_failures`: `files_failed > 0`

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, BigInteger, String, Integer, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class FolderBatch(Base):
    __tablename__ = 'folder_batches'
    
    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    folder_path = Column(Text, nullable=False)
    original_folder_name = Column(String(500), nullable=False)
    total_files_discovered = Column(Integer, default=0)
    files_processed = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)
    status = Column(String(50), nullable=False, default='discovering')
    error_message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    documents = relationship('Document', back_populates='folder_batch', lazy='dynamic')
    tenant = relationship('Tenant', back_populates='folder_batches')
    user = relationship('User', back_populates='folder_batches')
    
    __table_args__ = (
        CheckConstraint('files_processed <= total_files_discovered', name='check_files_counts'),
        CheckConstraint(
            "status IN ('discovering', 'processing', 'completed', 'partial_failure', 'failed')",
            name='check_status'
        ),
    )
    
    @property
    def progress_percentage(self) -> float:
        if self.total_files_discovered == 0:
            return 0.0
        return (self.files_processed / self.total_files_discovered) * 100
    
    @property
    def is_complete(self) -> bool:
        return self.status in ('completed', 'partial_failure', 'failed')
```

---

### 2. MarkdownMetadata (New Entity)

**Purpose**: Store markdown-specific metadata (frontmatter, structural counts, links)

**Table Name**: `markdown_metadata`

**Schema**:
```sql
CREATE TABLE markdown_metadata (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL UNIQUE,
    frontmatter JSONB,
    heading_count INTEGER DEFAULT 0,
    code_block_count INTEGER DEFAULT 0,
    mermaid_diagram_count INTEGER DEFAULT 0,
    table_count INTEGER DEFAULT 0,
    link_count INTEGER DEFAULT 0,
    image_count INTEGER DEFAULT 0,
    link_urls TEXT[],
    has_yaml_frontmatter BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_markdown_metadata_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT check_counts_positive CHECK (
        heading_count >= 0 AND code_block_count >= 0 AND 
        mermaid_diagram_count >= 0 AND table_count >= 0
    )
);

-- Indexes
CREATE UNIQUE INDEX idx_markdown_metadata_document_id ON markdown_metadata(document_id);
CREATE INDEX idx_markdown_metadata_frontmatter ON markdown_metadata USING GIN(frontmatter);
CREATE INDEX idx_markdown_metadata_has_frontmatter ON markdown_metadata(has_yaml_frontmatter) 
    WHERE has_yaml_frontmatter = TRUE;
CREATE INDEX idx_markdown_metadata_mermaid ON markdown_metadata(mermaid_diagram_count) 
    WHERE mermaid_diagram_count > 0;
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique metadata identifier |
| document_id | BIGINT | NOT NULL, UNIQUE, FK | One-to-one with Document |
| frontmatter | JSONB | NULLABLE | Parsed YAML frontmatter as JSON |
| heading_count | INTEGER | DEFAULT 0 | Count of headings (H1-H6) |
| code_block_count | INTEGER | DEFAULT 0 | Count of code blocks (including Mermaid) |
| mermaid_diagram_count | INTEGER | DEFAULT 0 | Count of Mermaid diagrams specifically |
| table_count | INTEGER | DEFAULT 0 | Count of markdown tables |
| link_count | INTEGER | DEFAULT 0 | Count of hyperlinks |
| image_count | INTEGER | DEFAULT 0 | Count of image references |
| link_urls | TEXT[] | NULLABLE | Array of extracted URLs |
| has_yaml_frontmatter | BOOLEAN | DEFAULT FALSE | Quick check for frontmatter presence |
| created_at | TIMESTAMP | NOT NULL | Metadata creation timestamp |

**Frontmatter JSON Structure** (Example):
```json
{
  "title": "API Documentation",
  "author": "John Doe",
  "date": "2026-01-10",
  "tags": ["api", "documentation", "rest"],
  "category": "engineering",
  "published": true
}
```

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, BigInteger, Integer, Boolean, TIMESTAMP, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class MarkdownMetadata(Base):
    __tablename__ = 'markdown_metadata'
    
    id = Column(BigInteger, primary_key=True)
    document_id = Column(BigInteger, ForeignKey('documents.id', ondelete='CASCADE'), 
                         nullable=False, unique=True)
    frontmatter = Column(JSONB)
    heading_count = Column(Integer, default=0)
    code_block_count = Column(Integer, default=0)
    mermaid_diagram_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    link_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    link_urls = Column(ARRAY(Text))
    has_yaml_frontmatter = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    document = relationship('Document', back_populates='markdown_metadata', uselist=False)
    
    __table_args__ = (
        CheckConstraint(
            'heading_count >= 0 AND code_block_count >= 0 AND mermaid_diagram_count >= 0 AND table_count >= 0',
            name='check_counts_positive'
        ),
    )
```

**Query Examples**:
```python
# Find documents with specific frontmatter tag
documents = session.query(Document).join(MarkdownMetadata).filter(
    MarkdownMetadata.frontmatter['tags'].astext.contains('api')
).all()

# Find documents with Mermaid diagrams
mermaid_docs = session.query(Document).join(MarkdownMetadata).filter(
    MarkdownMetadata.mermaid_diagram_count > 0
).all()

# Search frontmatter by author
author_docs = session.query(Document).join(MarkdownMetadata).filter(
    MarkdownMetadata.frontmatter['author'].astext == 'John Doe'
).all()
```

---

### 3. ImageReference (New Entity)

**Purpose**: Track image references in markdown for future OCR processing

**Table Name**: `image_references`

**Schema**:
```sql
CREATE TABLE image_references (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    image_url TEXT NOT NULL,
    alt_text TEXT,
    is_local_path BOOLEAN DEFAULT FALSE,
    is_base64 BOOLEAN DEFAULT FALSE,
    is_external_url BOOLEAN DEFAULT TRUE,
    resolved_path TEXT,
    file_size_bytes BIGINT,
    ocr_pending BOOLEAN DEFAULT FALSE,
    ocr_completed_at TIMESTAMP WITH TIME ZONE,
    position_in_document INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_image_reference_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT check_image_type CHECK (
        (is_local_path::int + is_base64::int + is_external_url::int) = 1
    )
);

-- Indexes
CREATE INDEX idx_image_references_document_id ON image_references(document_id);
CREATE INDEX idx_image_references_ocr_pending ON image_references(ocr_pending) 
    WHERE ocr_pending = TRUE;
CREATE INDEX idx_image_references_local_path ON image_references(is_local_path) 
    WHERE is_local_path = TRUE;
```

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Unique reference identifier |
| document_id | BIGINT | NOT NULL, FK | Parent markdown document |
| image_url | TEXT | NOT NULL | Image URL/path as in markdown |
| alt_text | TEXT | NULLABLE | Alt text from markdown (for RAG) |
| is_local_path | BOOLEAN | DEFAULT FALSE | True if local file path |
| is_base64 | BOOLEAN | DEFAULT FALSE | True if base64 embedded |
| is_external_url | BOOLEAN | DEFAULT TRUE | True if http/https URL |
| resolved_path | TEXT | NULLABLE | Absolute path if local image |
| file_size_bytes | BIGINT | NULLABLE | Image file size if available |
| ocr_pending | BOOLEAN | DEFAULT FALSE | Flag for future OCR processing |
| ocr_completed_at | TIMESTAMP | NULLABLE | OCR processing timestamp |
| position_in_document | INTEGER | NULLABLE | Image position (line number) |
| created_at | TIMESTAMP | NOT NULL | Reference creation timestamp |

**Constraint**: Exactly one of `is_local_path`, `is_base64`, `is_external_url` must be TRUE

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, BigInteger, Text, Boolean, Integer, TIMESTAMP, CheckConstraint

class ImageReference(Base):
    __tablename__ = 'image_references'
    
    id = Column(BigInteger, primary_key=True)
    document_id = Column(BigInteger, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(Text, nullable=False)
    alt_text = Column(Text)
    is_local_path = Column(Boolean, default=False)
    is_base64 = Column(Boolean, default=False)
    is_external_url = Column(Boolean, default=True)
    resolved_path = Column(Text)
    file_size_bytes = Column(BigInteger)
    ocr_pending = Column(Boolean, default=False)
    ocr_completed_at = Column(TIMESTAMP(timezone=True))
    position_in_document = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    document = relationship('Document', back_populates='image_references')
    
    __table_args__ = (
        CheckConstraint(
            '(is_local_path::int + is_base64::int + is_external_url::int) = 1',
            name='check_image_type'
        ),
    )
    
    @property
    def image_type(self) -> str:
        if self.is_local_path:
            return 'local'
        elif self.is_base64:
            return 'base64'
        else:
            return 'external'
```

---

### 4. Document (Extended Entity)

**Modifications**: Add foreign key to FolderBatch for folder upload tracking

**New Field**:
```sql
ALTER TABLE documents 
ADD COLUMN folder_batch_id BIGINT REFERENCES folder_batches(id) ON DELETE SET NULL;

CREATE INDEX idx_documents_folder_batch_id ON documents(folder_batch_id);
```

**SQLAlchemy Model Update**:
```python
class Document(Base):
    # ... existing fields ...
    
    folder_batch_id = Column(BigInteger, ForeignKey('folder_batches.id', ondelete='SET NULL'))
    
    # Relationships
    folder_batch = relationship('FolderBatch', back_populates='documents')
    markdown_metadata = relationship('MarkdownMetadata', back_populates='document', 
                                     uselist=False, cascade='all, delete-orphan')
    image_references = relationship('ImageReference', back_populates='document',
                                    cascade='all, delete-orphan')
```

**No other schema changes required** - existing fields handle markdown documents:
- `mime_type`: Set to 'text/markdown'
- `file_size`: Original markdown file size
- `storage_path`: Path to stored .md file
- `status`: Existing status enum works for markdown parsing

---

### 5. Chunk (Reused Entity)

**No modifications needed** - existing Chunk model supports markdown chunks:

```python
class Chunk(Base):
    __tablename__ = 'chunks'
    
    id = Column(BigInteger, primary_key=True)
    document_id = Column(BigInteger, ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)  # Markdown text chunk
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer)
    embedding = Column(Vector(1536))  # pgvector for RAG
    created_at = Column(TIMESTAMP(timezone=True))
```

**Markdown-specific considerations**:
- Chunks include alt text from images (extracted to content)
- Code block content included in chunks (searchable)
- Mermaid diagram code included in chunks (node labels searchable)

---

## Migration Script

**File**: `src/storage_indexing/migrations/versions/003_add_markdown_support.py`

```python
"""Add markdown ingestion support

Revision ID: 003_markdown_support
Revises: 002_doc_upload_parsing
Create Date: 2026-01-10 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_markdown_support'
down_revision = '002_doc_upload_parsing'
branch_labels = None
depends_on = None


def upgrade():
    # Create folder_batches table
    op.create_table(
        'folder_batches',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('folder_path', sa.Text(), nullable=False),
        sa.Column('original_folder_name', sa.String(500), nullable=False),
        sa.Column('total_files_discovered', sa.Integer(), server_default='0'),
        sa.Column('files_processed', sa.Integer(), server_default='0'),
        sa.Column('files_failed', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='discovering'),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('files_processed <= total_files_discovered', name='check_files_counts'),
        sa.CheckConstraint(
            "status IN ('discovering', 'processing', 'completed', 'partial_failure', 'failed')",
            name='check_status'
        )
    )
    op.create_index('idx_folder_batches_tenant_id', 'folder_batches', ['tenant_id'])
    op.create_index('idx_folder_batches_user_id', 'folder_batches', ['user_id'])
    op.create_index('idx_folder_batches_status', 'folder_batches', ['status'])
    op.create_index('idx_folder_batches_created_at', 'folder_batches', [sa.text('created_at DESC')])
    
    # Create markdown_metadata table
    op.create_table(
        'markdown_metadata',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('frontmatter', postgresql.JSONB()),
        sa.Column('heading_count', sa.Integer(), server_default='0'),
        sa.Column('code_block_count', sa.Integer(), server_default='0'),
        sa.Column('mermaid_diagram_count', sa.Integer(), server_default='0'),
        sa.Column('table_count', sa.Integer(), server_default='0'),
        sa.Column('link_count', sa.Integer(), server_default='0'),
        sa.Column('image_count', sa.Integer(), server_default='0'),
        sa.Column('link_urls', postgresql.ARRAY(sa.Text())),
        sa.Column('has_yaml_frontmatter', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            'heading_count >= 0 AND code_block_count >= 0 AND mermaid_diagram_count >= 0 AND table_count >= 0',
            name='check_counts_positive'
        )
    )
    op.create_unique_index('idx_markdown_metadata_document_id', 'markdown_metadata', ['document_id'])
    op.create_index('idx_markdown_metadata_frontmatter', 'markdown_metadata', ['frontmatter'], 
                    postgresql_using='gin')
    op.create_index('idx_markdown_metadata_has_frontmatter', 'markdown_metadata', ['has_yaml_frontmatter'],
                    postgresql_where=sa.text('has_yaml_frontmatter = TRUE'))
    op.create_index('idx_markdown_metadata_mermaid', 'markdown_metadata', ['mermaid_diagram_count'],
                    postgresql_where=sa.text('mermaid_diagram_count > 0'))
    
    # Create image_references table
    op.create_table(
        'image_references',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('alt_text', sa.Text()),
        sa.Column('is_local_path', sa.Boolean(), server_default='false'),
        sa.Column('is_base64', sa.Boolean(), server_default='false'),
        sa.Column('is_external_url', sa.Boolean(), server_default='true'),
        sa.Column('resolved_path', sa.Text()),
        sa.Column('file_size_bytes', sa.BigInteger()),
        sa.Column('ocr_pending', sa.Boolean(), server_default='false'),
        sa.Column('ocr_completed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('position_in_document', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            '(is_local_path::int + is_base64::int + is_external_url::int) = 1',
            name='check_image_type'
        )
    )
    op.create_index('idx_image_references_document_id', 'image_references', ['document_id'])
    op.create_index('idx_image_references_ocr_pending', 'image_references', ['ocr_pending'],
                    postgresql_where=sa.text('ocr_pending = TRUE'))
    op.create_index('idx_image_references_local_path', 'image_references', ['is_local_path'],
                    postgresql_where=sa.text('is_local_path = TRUE'))
    
    # Extend documents table
    op.add_column('documents', sa.Column('folder_batch_id', sa.BigInteger()))
    op.create_foreign_key('fk_documents_folder_batch', 'documents', 'folder_batches',
                         ['folder_batch_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_documents_folder_batch_id', 'documents', ['folder_batch_id'])


def downgrade():
    op.drop_index('idx_documents_folder_batch_id', 'documents')
    op.drop_constraint('fk_documents_folder_batch', 'documents', type_='foreignkey')
    op.drop_column('documents', 'folder_batch_id')
    
    op.drop_table('image_references')
    op.drop_table('markdown_metadata')
    op.drop_table('folder_batches')
```

---

## Validation Rules

### FolderBatch Validation

```python
def validate_folder_batch(batch: FolderBatch) -> None:
    """Validate folder batch constraints."""
    if batch.files_processed > batch.total_files_discovered:
        raise ValueError("files_processed cannot exceed total_files_discovered")
    
    if batch.status == 'completed' and batch.files_failed > 0:
        raise ValueError("Status cannot be 'completed' if files_failed > 0. Use 'partial_failure'.")
    
    if batch.status == 'completed' and batch.files_processed != batch.total_files_discovered:
        raise ValueError("Status 'completed' requires all files processed")
```

### MarkdownMetadata Validation

```python
def validate_markdown_metadata(metadata: MarkdownMetadata) -> None:
    """Validate markdown metadata constraints."""
    if any(count < 0 for count in [
        metadata.heading_count, metadata.code_block_count,
        metadata.mermaid_diagram_count, metadata.table_count
    ]):
        raise ValueError("All counts must be non-negative")
    
    if metadata.frontmatter and not metadata.has_yaml_frontmatter:
        raise ValueError("has_yaml_frontmatter must be True if frontmatter is present")
```

---

## Query Patterns

### Common Queries

```python
# Get all documents in a folder batch
documents = session.query(Document).filter(
    Document.folder_batch_id == batch_id
).all()

# Get folder batch progress
batch = session.query(FolderBatch).filter(FolderBatch.id == batch_id).first()
progress = (batch.files_processed / batch.total_files_discovered) * 100

# Find markdown documents with specific frontmatter
docs = session.query(Document).join(MarkdownMetadata).filter(
    MarkdownMetadata.frontmatter['category'].astext == 'engineering',
    MarkdownMetadata.frontmatter['published'].astext.cast(Boolean) == True
).all()

# Get documents with pending OCR
docs_with_pending_ocr = session.query(Document).join(ImageReference).filter(
    ImageReference.ocr_pending == True
).distinct().all()

# Count Mermaid diagrams across tenant
mermaid_count = session.query(
    func.sum(MarkdownMetadata.mermaid_diagram_count)
).join(Document).filter(
    Document.tenant_id == tenant_id
).scalar()
```

---

## Performance Considerations

### Indexing Strategy
- **GIN index on frontmatter JSONB**: Fast queries on frontmatter fields
- **Partial indexes**: Only index relevant rows (ocr_pending = TRUE, mermaid_count > 0)
- **Composite indexes**: Consider adding for common query patterns (tenant_id + status)

### Query Optimization
- Use `lazy='dynamic'` for large relationships (folder_batch.documents)
- Eager load markdown_metadata when documents retrieved
- Use pagination for folder batch document lists

### Data Retention
- Archive completed folder_batches after 90 days
- Keep markdown_metadata indefinitely (small size)
- OCR-processed image references can be cleaned up after embedding

---

## Summary

**New Tables**: 3 (folder_batches, markdown_metadata, image_references)  
**Modified Tables**: 1 (documents - add folder_batch_id)  
**Reused Tables**: 2 (chunks, parsing_jobs - no changes)  
**Migration Complexity**: Low (additive only, no data migration)  
**Backward Compatibility**: ✅ Full (no breaking changes)

**Next Steps**:
1. ✅ Data model defined
2. ⏭️ Create API contracts (OpenAPI specs)
3. ⏭️ Create quickstart guide for developers

