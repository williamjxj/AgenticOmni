from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.models.base import Base
import datetime

class AuditTrail(Base):
    __tablename__ = 'audit_trail'
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('review_queue.id'))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(String)
    review = relationship('ReviewQueue')
