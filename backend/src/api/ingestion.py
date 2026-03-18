from fastapi import APIRouter, Depends
from backend.src.models.ingestion_job import IngestionJob
from backend.src.models.db_config import get_session
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/api/ingestion/start")
def start_ingestion(document_id: int, session: Session = Depends(get_session)):
    job = IngestionJob(document_id=document_id, status="pending")
    session.add(job)
    session.commit()
    return {"job_id": job.id, "status": job.status}

@router.get("/api/ingestion/{job_id}")
def get_ingestion_status(job_id: int, session: Session = Depends(get_session)):
    job = session.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        return {"error": "Job not found"}
    return {"job_id": job.id, "status": job.status}
