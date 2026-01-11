"""Add embedding fields to document_chunks

Revision ID: 006_add_embedding_fields  
Revises: 005_create_extracted_texts
Create Date: 2026-01-11 10:20:00.000000

Feature: 004-ocr-embedding-pipeline
Task: T011
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '006_add_embedding_fields'
down_revision = '005_create_extracted_texts'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add embedding-specific fields to document_chunks table."""
    
    # Add chunk sequence number (for ordering)
    op.add_column(
        'document_chunks',
        sa.Column(
            'chunk_sequence',
            sa.Integer(),
            nullable=False,
            server_default='0',
            comment='Sequence number within document (0-indexed)'
        )
    )
    
    # Add character offsets
    op.add_column(
        'document_chunks',
        sa.Column(
            'char_offset_start',
            sa.Integer(),
            nullable=True,
            comment='Character offset in original text'
        )
    )
    
    op.add_column(
        'document_chunks',
        sa.Column(
            'char_offset_end',
            sa.Integer(),
            nullable=True,
            comment='Character offset in original text (end)'
        )
    )
    
    # Add section heading context
    op.add_column(
        'document_chunks',
        sa.Column(
            'section_heading',
            sa.String(255),
            nullable=True,
            comment='Nearest section/heading for context'
        )
    )
    
    # Add embedding model tracking
    op.add_column(
        'document_chunks',
        sa.Column(
            'embedding_model',
            sa.String(100),
            nullable=True,
            comment='Model used: multilingual-e5-base, multilingual-e5-large'
        )
    )
    
    # Add embedding generation timestamp
    op.add_column(
        'document_chunks',
        sa.Column(
            'embedding_generated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            comment='When embedding was created'
        )
    )
    
    # Update existing embedding_vector column to support 768 dimensions (multilingual-e5-base)
    # Note: This requires dropping and recreating the column
    # In production, you'd want a more careful migration strategy
    
    # Add check constraints
    op.create_check_constraint(
        'chk_chunk_sequence',
        'document_chunks',
        'chunk_sequence >= 0'
    )
    
    op.create_check_constraint(
        'chk_char_offsets',
        'document_chunks',
        'char_offset_start IS NULL OR char_offset_end IS NULL OR char_offset_start < char_offset_end'
    )
    
    # Create indexes
    op.create_index(
        'idx_chunks_sequence',
        'document_chunks',
        ['document_id', 'chunk_sequence']
    )
    
    op.create_index(
        'idx_chunks_embedding_model',
        'document_chunks',
        ['embedding_model']
    )
    
    # Create HNSW index for embedding vector similarity search
    # This is a critical performance optimization for vector search
    op.execute(
        """
        CREATE INDEX idx_chunks_embedding_hnsw 
        ON document_chunks 
        USING hnsw (embedding_vector vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )
    
    # Add unique constraint on chunk sequence per document
    op.create_unique_constraint(
        'uq_chunk_sequence_per_doc',
        'document_chunks',
        ['document_id', 'chunk_sequence']
    )


def downgrade() -> None:
    """Remove embedding fields from document_chunks table."""
    
    # Drop constraints
    op.drop_constraint('uq_chunk_sequence_per_doc', 'document_chunks', type_='unique')
    op.drop_constraint('chk_char_offsets', 'document_chunks', type_='check')
    op.drop_constraint('chk_chunk_sequence', 'document_chunks', type_='check')
    
    # Drop indexes
    op.drop_index('idx_chunks_embedding_hnsw', 'document_chunks')
    op.drop_index('idx_chunks_embedding_model', 'document_chunks')
    op.drop_index('idx_chunks_sequence', 'document_chunks')
    
    # Drop columns
    op.drop_column('document_chunks', 'embedding_generated_at')
    op.drop_column('document_chunks', 'embedding_model')
    op.drop_column('document_chunks', 'section_heading')
    op.drop_column('document_chunks', 'char_offset_end')
    op.drop_column('document_chunks', 'char_offset_start')
    op.drop_column('document_chunks', 'chunk_sequence')
