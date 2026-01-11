"""Create extracted_texts table

Revision ID: 005_create_extracted_texts
Revises: 004_add_ocr_fields
Create Date: 2026-01-11 10:10:00.000000

Feature: 004-ocr-embedding-pipeline
Task: T010
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_create_extracted_texts'
down_revision = '004_add_ocr_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create extracted_texts table for storing OCR and native text extraction."""
    
    op.create_table(
        'extracted_texts',
        sa.Column(
            'extracted_text_id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            comment='Unique identifier for extracted text'
        ),
        sa.Column(
            'document_id',
            sa.Integer(),
            nullable=False,
            comment='Foreign key to documents table'
        ),
        sa.Column(
            'page_number',
            sa.Integer(),
            nullable=False,
            comment='Page number (1-indexed)'
        ),
        sa.Column(
            'extraction_method',
            sa.String(20),
            nullable=False,
            comment='Method used: native, ocr_paddleocr, ocr_tesseract'
        ),
        sa.Column(
            'text_content',
            sa.Text(),
            nullable=False,
            comment='Extracted text content'
        ),
        sa.Column(
            'confidence_score',
            sa.Float(),
            nullable=True,
            comment='OCR confidence score (0.0-1.0), NULL for native extraction'
        ),
        sa.Column(
            'bounding_boxes',
            postgresql.JSONB(),
            nullable=True,
            comment='Bounding box coordinates for OCR text regions'
        ),
        sa.Column(
            'structural_metadata',
            postgresql.JSONB(),
            nullable=True,
            comment='Headings, paragraphs, tables, lists detected'
        ),
        sa.Column(
            'character_count',
            sa.Integer(),
            nullable=False,
            comment='Number of characters in text_content'
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
            comment='Extraction timestamp'
        ),
        
        # Constraints
        sa.PrimaryKeyConstraint('extracted_text_id'),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['documents.document_id'],
            ondelete='CASCADE'
        ),
        sa.CheckConstraint(
            'page_number >= 1',
            name='chk_page_number_positive'
        ),
        sa.CheckConstraint(
            "extraction_method IN ('native', 'ocr_paddleocr', 'ocr_tesseract')",
            name='chk_extraction_method'
        ),
        sa.CheckConstraint(
            "text_content != ''",
            name='chk_text_not_empty'
        ),
        sa.CheckConstraint(
            'confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)',
            name='chk_confidence_score'
        ),
        sa.CheckConstraint(
            'character_count > 0',
            name='chk_character_count'
        )
    )
    
    # Create indexes
    op.create_index(
        'idx_extracted_texts_document_id',
        'extracted_texts',
        ['document_id']
    )
    
    op.create_index(
        'idx_extracted_texts_page',
        'extracted_texts',
        ['document_id', 'page_number']
    )
    
    op.create_index(
        'idx_extracted_texts_method',
        'extracted_texts',
        ['extraction_method']
    )
    
    op.create_index(
        'idx_extracted_texts_confidence',
        'extracted_texts',
        ['confidence_score'],
        postgresql_where=sa.text('confidence_score IS NOT NULL')
    )
    
    # Full-text search index (optional, for keyword fallback)
    op.execute(
        """
        CREATE INDEX idx_extracted_texts_fts 
        ON extracted_texts 
        USING gin(to_tsvector('english', text_content))
        """
    )
    
    # JSONB indexes for metadata
    op.create_index(
        'idx_extracted_texts_bounding_boxes',
        'extracted_texts',
        ['bounding_boxes'],
        postgresql_using='gin'
    )
    
    op.create_index(
        'idx_extracted_texts_structural_metadata',
        'extracted_texts',
        ['structural_metadata'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """Drop extracted_texts table."""
    op.drop_table('extracted_texts')
