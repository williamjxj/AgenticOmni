from fastapi import APIRouter

router = APIRouter()

@router.get("/api/governance/usage")
def get_usage():
    # Placeholder: Return usage stats
    return {"usage": "1000 documents processed"}
