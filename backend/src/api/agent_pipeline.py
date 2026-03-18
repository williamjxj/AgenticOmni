from fastapi import APIRouter
from backend.src.agents.orchestrator import AgentPipelineOrchestrator
from backend.src.agents.ocr_agent import OcrAgent
from backend.src.agents.extraction_agent import ExtractionAgent
from backend.src.agents.rag_agent import RagAgent
from backend.src.agents.summary_agent import SummaryAgent

router = APIRouter()

@router.post("/api/agent-pipeline/run")
def run_pipeline(document: dict):
    agents = [OcrAgent(), ExtractionAgent(), RagAgent(), SummaryAgent()]
    orchestrator = AgentPipelineOrchestrator(agents)
    result = orchestrator.run(document)
    return {"result": result}
