"""Create search_queries and search_results tables

Revision ID: 008_create_search_tables
Revises: 007_enhance_processing_jobs
Create Date: 2026-01-11 10:40:00.000000

Feature: 004-ocr-embedding-pipeline
Task: T013
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_create_search_tables'
down_revision = '007_enhance_processing_jobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for search query logging and analytics."""
    
    # Create search_queries table
    op.create_table(
        'search_queries',
        sa.Column(
            'query_id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            comment='Unique identifier'
        ),
        sa.Column(
            'tenant_id',
            sa.Integer(),
            nullable=False,
            comment='Foreign key to tenants'
        ),
        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=True,
            comment='User who performed search'
        ),
        sa.Column(
            'query_text',
            sa.Text(),
            nullable=False,
            comment='Original search query text'
        ),
        sa.Column(
            'query_type',
            sa.String(20),
            nullable=False,
            comment='Type: semantic_search, similar_documents'
        ),
        sa.Column(
            'source_document_id',
            sa.Integer(),
            nullable=True,
            comment='For find similar queries'
        ),
        sa.Column(
            'filters_applied',
            postgresql.JSONB(),
            nullable=True,
            comment='Metadata filters used (date, folder, etc.)'
        ),
        sa.Column(
            'result_count',
            sa.Integer(),
            nullable=True,
            comment='Number of results returned'
        ),
        sa.Column(
            'search_duration_ms',
            sa.Integer(),
            nullable=True,
            comment='Query execution time in milliseconds'
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
            comment='When query was executed'
        ),
        
        # Constraints
        sa.PrimaryKeyConstraint('query_id'),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.tenant_id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.user_id'],
            ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['source_document_id'],
            ['documents.document_id'],
            ondelete='SET NULL'
        ),
        sa.CheckConstraint(
            "query_type IN ('semantic_search', 'similar_documents')",
            name='chk_query_type'
        ),
        sa.CheckConstraint(
            'result_count IS NULL OR result_count >= 0',
            name='chk_result_count'
        ),
        sa.CheckConstraint(
            'search_duration_ms IS NULL OR search_duration_ms >= 0',
            name='chk_search_duration'
        )
    )
    
    # Create search_results table
    op.create_table(
        'search_results',
        sa.Column(
            'result_id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            comment='Unique identifier'
        ),
        sa.Column(
            'query_id',
            sa.BigInteger(),
            nullable=False,
            comment='Associated search query'
        ),
        sa.Column(
            'chunk_id',
            sa.BigInteger(),
            nullable=False,
            comment='Matching chunk'
        ),
        sa.Column(
            'document_id',
            sa.Integer(),
            nullable=False,
            comment='Matching document'
        ),
        sa.Column(
            'similarity_score',
            sa.Float(),
            nullable=False,
            comment='Cosine similarity score'
        ),
        sa.Column(
            'rank_position',
            sa.Integer(),
            nullable=False,
            comment='Result position (1-based)'
        ),
        sa.Column(
            'result_snippet',
            sa.Text(),
            nullable=True,
            comment='Text snippet for preview'
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
            comment='When result was captured'
        ),
        
        # Constraints
        sa.PrimaryKeyConstraint('result_id'),
        sa.ForeignKeyConstraint(
            ['query_id'],
            ['search_queries.query_id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['chunk_id'],
            ['document_chunks.chunk_id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.document_id'],
            ondelete='CASCADE'
        ),
        sa.CheckConstraint(
            'similarity_score >= 0 AND similarity_score <= 1',
            name='chk_similarity_score'
        ),
        sa.CheckConstraint(
            'rank_position >= 1',
            name='chk_rank_position'
        )
    )
    
    # Create indexes for search_queries
    op.create_index(
        'idx_search_queries_tenant',
        'search_queries',
        ['tenant_id', sa.text('created_at DESC')]
    )
    
    op.create_index(
        'idx_search_queries_type',
        'search_queries',
        ['query_type']
    )
    
    op.create_index(
        'idx_search_queries_user',
        'search_queries',
        ['user_id'],
        postgresql_where=sa.text('user_id IS NOT NULL')
    )
    
    # Create indexes for search_results
    op.create_index(
        'idx_search_results_query',
        'search_results',
        ['query_id', 'rank_position']
    )
    
    op.create_index(
        'idx_search_results_chunk',
        'search_results',
        ['chunk_id']
    )
    
    op.create_index(
        'idx_search_results_document',
        'search_results',
        ['document_id']
    )


def downgrade() -> None:
    """Drop search tables."""
    op.drop_table('search_results')
    op.drop_table('search_queries')
