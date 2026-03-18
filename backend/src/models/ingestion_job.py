from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class IngestionJob(Base):
    __tablename__ = 'ingestion_jobs'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    status = Column(String, default='pending')
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    document = relationship('Document')
