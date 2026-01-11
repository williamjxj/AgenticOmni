"""Add OCR fields to documents table

Revision ID: 004_add_ocr_fields
Revises: 003_markdown_support
Create Date: 2026-01-11 10:00:00.000000

Feature: 004-ocr-embedding-pipeline
Task: T009
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_ocr_fields'
down_revision = '003_markdown_support'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add OCR processing fields to documents table."""
    
    # Add OCR status tracking
    op.add_column(
        'documents',
        sa.Column(
            'ocr_status',
            sa.String(20),
            nullable=False,
            server_default='not_started',
            comment='OCR processing status: not_started, in_progress, completed, failed'
        )
    )
    
    # Add OCR confidence score
    op.add_column(
        'documents',
        sa.Column(
            'ocr_confidence',
            sa.Float(),
            nullable=True,
            comment='Average OCR confidence score (0.0-1.0)'
        )
    )
    
    # Add embedding status tracking
    op.add_column(
        'documents',
        sa.Column(
            'embedding_status',
            sa.String(20),
            nullable=False,
            server_default='not_started',
            comment='Embedding generation status: not_started, in_progress, completed, failed'
        )
    )
    
    # Add language detection
    op.add_column(
        'documents',
        sa.Column(
            'language_detected',
            sa.String(10),
            nullable=True,
            comment='Detected language (ISO 639-1 code: en, zh, etc.)'
        )
    )
    
    # page_count already exists from migration ea5d2dac7580
    
    # Add scanned content flag
    op.add_column(
        'documents',
        sa.Column(
            'has_scanned_content',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='True if document contains image-based content requiring OCR'
        )
    )
    
    # Add OCR engine used
    op.add_column(
        'documents',
        sa.Column(
            'ocr_engine_used',
            sa.String(50),
            nullable=True,
            comment='OCR engine used: paddleocr, tesseract, none'
        )
    )
    
    # Add check constraints
    op.create_check_constraint(
        'chk_ocr_status',
        'documents',
        "ocr_status IN ('not_started', 'in_progress', 'completed', 'failed')"
    )
    
    op.create_check_constraint(
        'chk_embedding_status',
        'documents',
        "embedding_status IN ('not_started', 'in_progress', 'completed', 'failed')"
    )
    
    op.create_check_constraint(
        'chk_ocr_confidence',
        'documents',
        'ocr_confidence IS NULL OR (ocr_confidence >= 0 AND ocr_confidence <= 1)'
    )
    
    op.create_check_constraint(
        'chk_page_count',
        'documents',
        'page_count IS NULL OR page_count >= 1'
    )
    
    # Create indexes for efficient queries
    op.create_index(
        'idx_documents_ocr_status',
        'documents',
        ['tenant_id', 'ocr_status']
    )
    
    op.create_index(
        'idx_documents_embedding_status',
        'documents',
        ['tenant_id', 'embedding_status']
    )
    
    op.create_index(
        'idx_documents_language',
        'documents',
        ['language_detected']
    )
    
    op.create_index(
        'idx_documents_scanned_content',
        'documents',
        ['has_scanned_content'],
        postgresql_where=sa.text('has_scanned_content = true')
    )


def downgrade() -> None:
    """Remove OCR fields from documents table."""
    
    # Drop indexes
    op.drop_index('idx_documents_scanned_content', 'documents')
    op.drop_index('idx_documents_language', 'documents')
    op.drop_index('idx_documents_embedding_status', 'documents')
    op.drop_index('idx_documents_ocr_status', 'documents')
    
    # Drop check constraints
    op.drop_constraint('chk_page_count', 'documents', type_='check')
    op.drop_constraint('chk_ocr_confidence', 'documents', type_='check')
    op.drop_constraint('chk_embedding_status', 'documents', type_='check')
    op.drop_constraint('chk_ocr_status', 'documents', type_='check')
    
    # Drop columns
    op.drop_column('documents', 'ocr_engine_used')
    op.drop_column('documents', 'has_scanned_content')
    op.drop_column('documents', 'page_count')
    op.drop_column('documents', 'language_detected')
    op.drop_column('documents', 'embedding_status')
    op.drop_column('documents', 'ocr_confidence')
    op.drop_column('documents', 'ocr_status')
