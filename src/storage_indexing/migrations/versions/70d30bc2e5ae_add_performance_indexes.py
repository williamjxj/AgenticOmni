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
    # Note: ix_documents_content_hash already exists from previous migration
    # Only create new indexes here
    
    # Index on documents.uploaded_by for user-specific queries
    op.execute('CREATE INDEX IF NOT EXISTS ix_documents_uploaded_by ON documents (uploaded_by)')
    
    # Composite index on documents (tenant_id, created_at) for listing
    op.execute('CREATE INDEX IF NOT EXISTS ix_documents_tenant_created ON documents (tenant_id, created_at)')
    
    # Index on upload_sessions.expires_at for cleanup queries
    op.execute('CREATE INDEX IF NOT EXISTS ix_upload_sessions_expires_at ON upload_sessions (expires_at)')
    
    # Index on processing_jobs.status for querying pending jobs
    op.execute('CREATE INDEX IF NOT EXISTS ix_processing_jobs_status ON processing_jobs (status)')
    
    # Composite index on processing_jobs (document_id, created_at)
    op.execute('CREATE INDEX IF NOT EXISTS ix_processing_jobs_document_created ON processing_jobs (document_id, created_at)')


def downgrade() -> None:
    """Remove performance indexes."""
    # Note: Don't drop ix_documents_content_hash as it was created in previous migration
    op.execute('DROP INDEX IF EXISTS ix_processing_jobs_document_created')
    op.execute('DROP INDEX IF EXISTS ix_processing_jobs_status')
    op.execute('DROP INDEX IF EXISTS ix_upload_sessions_expires_at')
    op.execute('DROP INDEX IF EXISTS ix_documents_tenant_created')
    op.execute('DROP INDEX IF EXISTS ix_documents_uploaded_by')
