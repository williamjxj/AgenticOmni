from fastapi import APIRouter
from backend.src.governance.usage import router as usage_router
from backend.src.governance.cost import router as cost_router
from backend.src.governance.logs import router as logs_router

router = APIRouter()
router.include_router(usage_router)
router.include_router(cost_router)
router.include_router(logs_router)
