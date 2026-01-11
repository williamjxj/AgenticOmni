"""Database models for AgenticOmni.

This module exports all database models and the SQLAlchemy declarative base.
"""

# Import order matters for SQLAlchemy relationships!
# Base classes first
from src.storage_indexing.models.base import Base, TenantScopedMixin

# Then models without foreign key dependencies
from src.storage_indexing.models.permission import Permission
from src.storage_indexing.models.upload_session import UploadSession, UploadStatus

# Tenant and User before FolderBatch (FolderBatch references them)
from src.storage_indexing.models.tenant import Tenant
from src.storage_indexing.models.user import User

# FolderBatch before Document (Document references FolderBatch)
from src.storage_indexing.models.folder_batch import FolderBatch

# Document and its related models
from src.storage_indexing.models.document import Document, ProcessingStatus
from src.storage_indexing.models.markdown_metadata import MarkdownMetadata
from src.storage_indexing.models.image_reference import ImageReference
from src.storage_indexing.models.document_chunk import ChunkType, DocumentChunk

# Processing job last
from src.storage_indexing.models.processing_job import JobStatus, JobType, ProcessingJob

__all__ = [
    "Base",
    "ChunkType",
    "Document",
    "DocumentChunk",
    "FolderBatch",
    "ImageReference",
    "JobStatus",
    "JobType",
    "MarkdownMetadata",
    "Permission",
    "ProcessingJob",
    "ProcessingStatus",
    "Tenant",
    "TenantScopedMixin",
    "UploadSession",
    "UploadStatus",
    "User",
]
