from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.src.models.base import Base
import datetime

class ReviewQueue(Base):
    __tablename__ = 'review_queue'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    document = relationship('Document')
    reviewer = relationship('User')
