from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/agenticomni")

def get_engine():
	return create_engine(DATABASE_URL)

def get_session():
	engine = get_engine()
	SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	return SessionLocal()

def init_db():
	engine = get_engine()
	Base.metadata.create_all(bind=engine)
