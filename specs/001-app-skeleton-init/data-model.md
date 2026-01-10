# Data Model Specification

**Feature**: AgenticOmni Application Skeleton  
**Date**: January 9, 2026  
**Phase**: 1 - Design

## Overview

This document defines the complete database schema for the AgenticOmni platform, including all entities, relationships, constraints, and indexes. The schema supports multi-tenant document processing with vector embeddings for RAG retrieval.

**Database**: PostgreSQL 14+  
**Extensions**: pgvector (for 1536-dimension vector storage)  
**Migration Tool**: Alembic  
**Isolation Strategy**: Row-level multi-tenancy with tenant_id in shared schema

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     Tenant      │
│  (tenant_id PK) │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────────────────┐
    │                                       │
    │                                       │
┌───▼────────┐                    ┌────────▼──────────┐
│    User    │                    │     Document      │
│(user_id PK)│                    │  (document_id PK) │
│tenant_id FK│                    │  tenant_id FK     │
└──┬─────────┘                    └─────────┬─────────┘
   │                                        │
   │                                        │ 1:N
   │ N:M                                    │
   │                              ┌─────────▼──────────┐
   │                              │  DocumentChunk     │
   │                              │ (chunk_id PK)      │
   │                              │ document_id FK     │
   │                              │ embedding_vector   │
   │                              │     [1536d]        │
   │                              └────────────────────┘
   │
   │ 1:N
   │
┌──▼────────────┐            ┌──────────────────┐
│  Permission   │            │  ProcessingJob   │
│(permission_id │            │   (job_id PK)    │
│     PK)       │            │  document_id FK  │
│  user_id FK   │            │  tenant_id FK    │
└───────────────┘            │  status [enum]   │
                             └──────────────────┘
```

---

## Entities

### 1. Tenant

**Purpose**: Root entity representing an organization or client. Provides multi-tenancy isolation boundary.

**Table Name**: `tenants`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tenant_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique tenant identifier |
| name | VARCHAR(255) | NOT NULL | Organization display name |
| domain | VARCHAR(255) | UNIQUE, NOT NULL | Subdomain or unique identifier (e.g., "acme-corp") |
| settings | JSONB | DEFAULT '{}' | Tenant-specific configuration (JSON blob) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active', CHECK (status IN ('active', 'suspended', 'trial')) | Tenant account status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Tenant creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY: `tenant_id`
- UNIQUE INDEX: `idx_tenant_domain` ON `domain`
- INDEX: `idx_tenant_status` ON `status` (for filtering active tenants)

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

class Tenant(Base):
    __tablename__ = "tenants"
    
    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    settings = Column(JSONB, default={}, nullable=False)
    status = Column(
        String(20),
        CheckConstraint("status IN ('active', 'suspended', 'trial')"),
        nullable=False,
        default='active',
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="tenant", cascade="all, delete-orphan")
```

**Sample Data**:
```json
{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Acme Corporation",
  "domain": "acme-corp",
  "settings": {
    "max_documents": 10000,
    "allowed_file_types": ["pdf", "docx", "pptx"],
    "retention_days": 365
  },
  "status": "active",
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:00:00Z"
}
```

---

### 2. User

**Purpose**: Represents an individual user within a tenant. Stores authentication details and role assignments.

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| tenant_id | UUID | NOT NULL, FOREIGN KEY → tenants(tenant_id) ON DELETE CASCADE | Owning tenant |
| email | VARCHAR(255) | NOT NULL | User email address (unique within tenant) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt/Argon2 hashed password |
| role | VARCHAR(50) | NOT NULL, DEFAULT 'viewer', CHECK (role IN ('admin', 'editor', 'viewer')) | User role for RBAC |
| full_name | VARCHAR(255) | NULL | User's full display name |
| last_login | TIMESTAMP | NULL | Last successful login timestamp |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Account active status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | User creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY: `user_id`
- UNIQUE INDEX: `idx_user_tenant_email` ON `(tenant_id, email)` (email unique per tenant)
- INDEX: `idx_user_tenant` ON `tenant_id` (for tenant queries)

**Constraints**:
- FOREIGN KEY: `tenant_id` → `tenants(tenant_id)` ON DELETE CASCADE

**SQLAlchemy Model**:
```python
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(50),
        CheckConstraint("role IN ('admin', 'editor', 'viewer')"),
        nullable=False,
        default='viewer'
    )
    full_name = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    permissions = relationship("Permission", back_populates="user", cascade="all, delete-orphan")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_tenant_email'),
    )
```

---

### 3. Document

**Purpose**: Represents an uploaded or ingested document with metadata and processing status.

**Table Name**: `documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique document identifier |
| tenant_id | UUID | NOT NULL, FOREIGN KEY → tenants(tenant_id) ON DELETE CASCADE | Owning tenant |
| filename | VARCHAR(500) | NOT NULL | Original filename |
| file_type | VARCHAR(50) | NOT NULL | File extension/MIME type (e.g., "pdf", "docx") |
| file_size | BIGINT | NOT NULL | File size in bytes |
| storage_path | VARCHAR(1000) | NOT NULL | S3/GCS path or local file path |
| processing_status | VARCHAR(50) | NOT NULL, DEFAULT 'uploaded', CHECK (processing_status IN ('uploaded', 'processing', 'completed', 'failed')) | Document processing status |
| document_metadata | JSONB | DEFAULT '{}' | Custom metadata (author, tags, extracted info) |
| upload_date | TIMESTAMP | NOT NULL, DEFAULT NOW() | Upload timestamp |
| processed_at | TIMESTAMP | NULL | Processing completion timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY: `document_id`
- INDEX: `idx_document_tenant_upload` ON `(tenant_id, upload_date DESC)` (for tenant doc listing)
- INDEX: `idx_document_status` ON `processing_status` (for status filtering)
- INDEX: `idx_document_metadata` USING GIN ON `document_metadata` (for JSONB queries)

**Constraints**:
- FOREIGN KEY: `tenant_id` → `tenants(tenant_id)` ON DELETE CASCADE

**SQLAlchemy Model**:
```python
class Document(Base):
    __tablename__ = "documents"
    
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    processing_status = Column(
        String(50),
        CheckConstraint("processing_status IN ('uploaded', 'processing', 'completed', 'failed')"),
        nullable=False,
        default='uploaded',
        index=True
    )
    document_metadata = Column(JSONB, default={}, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="document")
    
    # Composite index
    __table_args__ = (
        Index('idx_document_tenant_upload', 'tenant_id', 'upload_date'),
    )
```

---

### 4. DocumentChunk

**Purpose**: Processed segment of a document with vector embedding for RAG retrieval.

**Table Name**: `document_chunks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| chunk_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique chunk identifier |
| document_id | UUID | NOT NULL, FOREIGN KEY → documents(document_id) ON DELETE CASCADE | Parent document |
| content_text | TEXT | NOT NULL | Extracted text content of chunk |
| embedding_vector | vector(1536) | NOT NULL | 1536-dimension vector embedding (pgvector) |
| chunk_order | INTEGER | NOT NULL | Chunk sequence number within document (0-indexed) |
| chunk_metadata | JSONB | DEFAULT '{}' | Chunk-specific metadata (page number, section, etc.) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Chunk creation timestamp |

**Indexes**:
- PRIMARY KEY: `chunk_id`
- INDEX: `idx_chunk_document_order` ON `(document_id, chunk_order)` (for ordered retrieval)
- INDEX: `idx_chunk_embedding` USING HNSW ON `embedding_vector vector_cosine_ops` (similarity search, add in Phase 2)

**Constraints**:
- FOREIGN KEY: `document_id` → `documents(document_id)` ON DELETE CASCADE
- CHECK: `chunk_order >= 0`

**SQLAlchemy Model**:
```python
from pgvector.sqlalchemy import Vector

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id', ondelete='CASCADE'), nullable=False, index=True)
    content_text = Column(Text, nullable=False)
    embedding_vector = Column(Vector(1536), nullable=False)  # pgvector type with 1536 dimensions
    chunk_order = Column(Integer, CheckConstraint("chunk_order >= 0"), nullable=False)
    chunk_metadata = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Composite index for ordered retrieval
    __table_args__ = (
        Index('idx_chunk_document_order', 'document_id', 'chunk_order'),
    )
```

**Vector Search Query Example**:
```python
# Cosine similarity search (L2 normalized vectors)
from sqlalchemy import select, func
from pgvector.sqlalchemy import cosine_distance

async def search_similar_chunks(
    session: AsyncSession,
    tenant_id: UUID,
    query_vector: list[float],
    limit: int = 10
) -> list[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .join(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(cosine_distance(DocumentChunk.embedding_vector, query_vector))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
```

---

### 5. Permission

**Purpose**: Defines access control rules for users to resources (documents or other entities).

**Table Name**: `permissions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| permission_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique permission identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → users(user_id) ON DELETE CASCADE | User granted permission |
| resource_type | VARCHAR(50) | NOT NULL, CHECK (resource_type IN ('document', 'folder', 'tenant')) | Type of resource |
| resource_id | UUID | NOT NULL | ID of the resource (e.g., document_id) |
| permission_level | VARCHAR(20) | NOT NULL, CHECK (permission_level IN ('read', 'write', 'admin')) | Access level |
| granted_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Permission grant timestamp |
| granted_by | UUID | NULL, FOREIGN KEY → users(user_id) | User who granted permission |

**Indexes**:
- PRIMARY KEY: `permission_id`
- UNIQUE INDEX: `idx_permission_user_resource` ON `(user_id, resource_type, resource_id)` (no duplicate permissions)
- INDEX: `idx_permission_resource` ON `(resource_type, resource_id)` (for resource permission lookup)

**Constraints**:
- FOREIGN KEY: `user_id` → `users(user_id)` ON DELETE CASCADE
- FOREIGN KEY: `granted_by` → `users(user_id)` ON DELETE SET NULL

**SQLAlchemy Model**:
```python
class Permission(Base):
    __tablename__ = "permissions"
    
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    resource_type = Column(
        String(50),
        CheckConstraint("resource_type IN ('document', 'folder', 'tenant')"),
        nullable=False
    )
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    permission_level = Column(
        String(20),
        CheckConstraint("permission_level IN ('read', 'write', 'admin')"),
        nullable=False
    )
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
    
    # Unique constraint: one permission per user-resource pair
    __table_args__ = (
        UniqueConstraint('user_id', 'resource_type', 'resource_id', name='uq_user_resource'),
        Index('idx_permission_resource', 'resource_type', 'resource_id'),
    )
```

---

### 6. ProcessingJob

**Purpose**: Tracks background tasks for document ingestion, OCR, embedding generation, or reprocessing.

**Table Name**: `processing_jobs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique job identifier |
| document_id | UUID | NULL, FOREIGN KEY → documents(document_id) ON DELETE SET NULL | Associated document (nullable for bulk jobs) |
| tenant_id | UUID | NOT NULL, FOREIGN KEY → tenants(tenant_id) ON DELETE CASCADE | Owning tenant |
| job_type | VARCHAR(50) | NOT NULL, CHECK (job_type IN ('ingest', 'ocr', 'embed', 'reprocess')) | Type of processing task |
| status | job_status_enum | NOT NULL, DEFAULT 'pending' | Current job status (enum) |
| retry_count | INTEGER | NOT NULL, DEFAULT 0 | Number of retry attempts |
| max_retries | INTEGER | NOT NULL, DEFAULT 3 | Maximum allowed retries |
| started_at | TIMESTAMP | NULL | Job start timestamp |
| completed_at | TIMESTAMP | NULL | Job completion timestamp |
| error_message | TEXT | NULL | Error details if failed |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Job creation timestamp |

**Enum Type**: `job_status_enum`
```sql
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled', 'retrying');
```

**Indexes**:
- PRIMARY KEY: `job_id`
- INDEX: `idx_job_tenant_status` ON `(tenant_id, status, created_at DESC)` (for tenant job monitoring)
- INDEX: `idx_job_document` ON `document_id` (for document processing history)

**Constraints**:
- FOREIGN KEY: `document_id` → `documents(document_id)` ON DELETE SET NULL
- FOREIGN KEY: `tenant_id` → `tenants(tenant_id)` ON DELETE CASCADE
- CHECK: `retry_count <= max_retries`

**State Transitions**:
```
pending → processing → completed
                    → failed (no retry)
                    → retrying → processing (retry)
                              → failed (max retries)
                              → cancelled
```

**SQLAlchemy Model**:
```python
from enum import Enum as PyEnum

class JobStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobType(str, PyEnum):
    INGEST = "ingest"
    OCR = "ocr"
    EMBED = "embed"
    REPROCESS = "reprocess"

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.document_id', ondelete='SET NULL'), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False, index=True)
    job_type = Column(
        Enum(JobType, name="job_type", create_type=True),
        nullable=False
    )
    status = Column(
        Enum(JobStatus, name="job_status", create_type=True),
        nullable=False,
        default=JobStatus.PENDING,
        index=True
    )
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="processing_jobs")
    tenant = relationship("Tenant", back_populates="processing_jobs")
    
    # Composite index for tenant job monitoring
    __table_args__ = (
        Index('idx_job_tenant_status', 'tenant_id', 'status', 'created_at'),
        CheckConstraint('retry_count <= max_retries', name='chk_retry_limit'),
    )
```

---

## Database Initialization

### Alembic Migration: Initial Schema

**File**: `src/storage_indexing/migrations/versions/001_initial_schema.py`

```python
"""Initial schema with pgvector extension

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create enums
    op.execute("CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled', 'retrying')")
    op.execute("CREATE TYPE job_type AS ENUM ('ingest', 'ocr', 'embed', 'reprocess')")
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), unique=True, nullable=False),
        sa.Column('settings', postgresql.JSONB, server_default='{}', nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('active', 'suspended', 'trial')", name='chk_tenant_status')
    )
    op.create_index('idx_tenant_domain', 'tenants', ['domain'], unique=True)
    op.create_index('idx_tenant_status', 'tenants', ['status'])
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='viewer'),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('admin', 'editor', 'viewer')", name='chk_user_role'),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_tenant_email')
    )
    op.create_index('idx_user_tenant', 'users', ['tenant_id'])
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.BigInteger, nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('processing_status', sa.String(50), nullable=False, server_default='uploaded'),
        sa.Column('document_metadata', postgresql.JSONB, server_default='{}', nullable=False),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint("processing_status IN ('uploaded', 'processing', 'completed', 'failed')", name='chk_processing_status')
    )
    op.create_index('idx_document_tenant_upload', 'documents', ['tenant_id', sa.text('upload_date DESC')])
    op.create_index('idx_document_status', 'documents', ['processing_status'])
    op.create_index('idx_document_metadata', 'documents', ['document_metadata'], postgresql_using='gin')
    
    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.document_id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_text', sa.Text, nullable=False),
        sa.Column('embedding_vector', Vector(1536), nullable=False),
        sa.Column('chunk_order', sa.Integer, nullable=False),
        sa.Column('chunk_metadata', postgresql.JSONB, server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('chunk_order >= 0', name='chk_chunk_order')
    )
    op.create_index('idx_chunk_document_order', 'document_chunks', ['document_id', 'chunk_order'])
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_level', sa.String(20), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('granted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
        sa.CheckConstraint("resource_type IN ('document', 'folder', 'tenant')", name='chk_resource_type'),
        sa.CheckConstraint("permission_level IN ('read', 'write', 'admin')", name='chk_permission_level'),
        sa.UniqueConstraint('user_id', 'resource_type', 'resource_id', name='uq_user_resource')
    )
    op.create_index('idx_permission_resource', 'permissions', ['resource_type', 'resource_id'])
    
    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('job_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.document_id', ondelete='SET NULL'), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.tenant_id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_type', sa.Enum('ingest', 'ocr', 'embed', 'reprocess', name='job_type'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'cancelled', 'retrying', name='job_status'), nullable=False, server_default='pending'),
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer, nullable=False, server_default='3'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('retry_count <= max_retries', name='chk_retry_limit')
    )
    op.create_index('idx_job_tenant_status', 'processing_jobs', ['tenant_id', 'status', sa.text('created_at DESC')])
    op.create_index('idx_job_document', 'processing_jobs', ['document_id'])

def downgrade() -> None:
    op.drop_table('processing_jobs')
    op.drop_table('permissions')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('tenants')
    op.execute('DROP TYPE IF EXISTS job_status')
    op.execute('DROP TYPE IF EXISTS job_type')
    op.execute('DROP EXTENSION IF EXISTS vector')
```

---

## Data Model Summary

| Entity | Purpose | Key Relationships | Multi-Tenant |
|--------|---------|-------------------|--------------|
| **Tenant** | Organization root | 1:N Users, Documents, Jobs | Root entity |
| **User** | Individual user | N:1 Tenant, 1:N Permissions | ✅ tenant_id FK |
| **Document** | Uploaded file | N:1 Tenant, 1:N Chunks, 1:N Jobs | ✅ tenant_id FK |
| **DocumentChunk** | Text segment + vector | N:1 Document | Via Document |
| **Permission** | Access control rule | N:1 User, references resources | Via User |
| **ProcessingJob** | Background task | N:1 Tenant, N:1 Document (optional) | ✅ tenant_id FK |

**Total Tables**: 6  
**Total Enums**: 2 (job_status, job_type)  
**Extensions**: pgvector  
**Estimated Schema Size**: ~50KB (without data)

---

**Data Model Complete**: All entities defined with comprehensive schemas, constraints, indexes, and relationships. Ready for Alembic migration generation.
