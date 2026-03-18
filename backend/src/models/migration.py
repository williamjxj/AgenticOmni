from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class Migration(Base):
    __tablename__ = 'alembic_version'
    version_num = Column(String, primary_key=True)
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
