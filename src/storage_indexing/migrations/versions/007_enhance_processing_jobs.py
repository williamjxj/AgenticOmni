"""Enhance processing_jobs table for OCR and embedding tasks

Revision ID: 007_enhance_processing_jobs
Revises: 006_add_embedding_fields
Create Date: 2026-01-11 10:30:00.000000

Feature: 004-ocr-embedding-pipeline
Task: T012
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_enhance_processing_jobs'
down_revision = '006_add_embedding_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Skip redundant enhancements."""
    pass


def downgrade() -> None:
    """Skip redundant enhancements."""
    pass

