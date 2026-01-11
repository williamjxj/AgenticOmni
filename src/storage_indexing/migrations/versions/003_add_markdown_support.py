"""Add markdown ingestion support

Revision ID: 003_markdown_support
Revises: 70d30bc2e5ae
Create Date: 2026-01-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_markdown_support'
down_revision = '70d30bc2e5ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add tables for markdown ingestion: folder_batches, markdown_metadata, image_references."""
    
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
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.CheckConstraint('files_processed <= total_files_discovered', name='check_files_counts'),
        sa.CheckConstraint(
            "status IN ('discovering', 'processing', 'completed', 'partial_failure', 'failed')",
            name='check_folder_batch_status'
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
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            'heading_count >= 0 AND code_block_count >= 0 AND mermaid_diagram_count >= 0 AND table_count >= 0',
            name='check_counts_positive'
        )
    )
    op.create_index('idx_markdown_metadata_document_id', 'markdown_metadata', ['document_id'], unique=True)
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
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='CASCADE'),
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
    
    # Extend documents table with folder_batch_id
    op.add_column('documents', sa.Column('folder_batch_id', sa.BigInteger()))
    op.create_foreign_key('fk_documents_folder_batch', 'documents', 'folder_batches',
                         ['folder_batch_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_documents_folder_batch_id', 'documents', ['folder_batch_id'])


def downgrade() -> None:
    """Remove markdown ingestion tables."""
    op.drop_index('idx_documents_folder_batch_id', 'documents')
    op.drop_constraint('fk_documents_folder_batch', 'documents', type_='foreignkey')
    op.drop_column('documents', 'folder_batch_id')
    
    op.drop_table('image_references')
    op.drop_table('markdown_metadata')
    op.drop_table('folder_batches')
