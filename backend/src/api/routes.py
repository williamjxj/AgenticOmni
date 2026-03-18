from fastapi import APIRouter
from backend.src.auth.auth import auth_router

api_router = APIRouter()

# Mount authentication endpoints
api_router.include_router(auth_router)

# Placeholder for additional API routes (documents, ingestion, governance, etc.)
