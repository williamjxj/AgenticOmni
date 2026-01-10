"""API routes for metrics and monitoring."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse

import structlog

from src.shared.metrics import export_prometheus, get_metrics_report

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_class=JSONResponse)
async def get_metrics() -> JSONResponse:
    """Get metrics in JSON format.
    
    Returns comprehensive metrics including:
    - Upload statistics
    - Parsing performance
    - Storage usage
    - Error rates
    - System metrics
    
    Returns:
        JSON response with all metrics
    """
    metrics = get_metrics_report()
    return JSONResponse(content=metrics)


@router.get("/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics() -> PlainTextResponse:
    """Get metrics in Prometheus text format.
    
    Returns metrics in Prometheus exposition format for scraping.
    Compatible with Prometheus, Grafana, and other monitoring tools.
    
    Returns:
        Plain text response in Prometheus format
    """
    prometheus_output = export_prometheus()
    return PlainTextResponse(content=prometheus_output)
