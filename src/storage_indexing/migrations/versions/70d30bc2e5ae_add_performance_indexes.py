"""add_performance_indexes

Revision ID: 70d30bc2e5ae
Revises: ea5d2dac7580
Create Date: 2026-01-09 23:04:39.878733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70d30bc2e5ae'
down_revision: Union[str, Sequence[str], None] = 'ea5d2dac7580'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for document queries."""
    # Index on documents.content_hash for duplicate detection
    op.create_index(
        'ix_documents_content_hash',
        'documents',
        ['content_hash'],
        unique=False
    )
    
    # Index on documents.uploaded_by for user-specific queries
    op.create_index(
        'ix_documents_uploaded_by',
        'documents',
        ['uploaded_by'],
        unique=False
    )
    
    # Composite index on documents (tenant_id, created_at) for listing
    op.create_index(
        'ix_documents_tenant_created',
        'documents',
        ['tenant_id', 'created_at'],
        unique=False
    )
    
    # Index on upload_sessions.expires_at for cleanup queries
    op.create_index(
        'ix_upload_sessions_expires_at',
        'upload_sessions',
        ['expires_at'],
        unique=False
    )
    
    # Index on processing_jobs.status for querying pending jobs
    op.create_index(
        'ix_processing_jobs_status',
        'processing_jobs',
        ['status'],
        unique=False
    )
    
    # Composite index on processing_jobs (document_id, created_at)
    op.create_index(
        'ix_processing_jobs_document_created',
        'processing_jobs',
        ['document_id', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_processing_jobs_document_created', table_name='processing_jobs')
    op.drop_index('ix_processing_jobs_status', table_name='processing_jobs')
    op.drop_index('ix_upload_sessions_expires_at', table_name='upload_sessions')
    op.drop_index('ix_documents_tenant_created', table_name='documents')
    op.drop_index('ix_documents_uploaded_by', table_name='documents')
    op.drop_index('ix_documents_content_hash', table_name='documents')
