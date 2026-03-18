from fastapi import APIRouter
from backend.src.review.review_queue import ReviewQueue
from backend.src.review.audit import AuditTrail

router = APIRouter()

@router.post("/api/review/queue")
def add_to_review_queue(document_id: int, reviewer_id: int):
    # Placeholder: Add document to review queue
    return {"status": "added"}

@router.post("/api/review/audit")
def add_audit_entry(review_id: int, action: str, details: str):
    # Placeholder: Add audit entry
    return {"status": "logged"}
