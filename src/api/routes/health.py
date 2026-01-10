"""Health check endpoint for monitoring and status verification."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.shared.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ServiceCheck(BaseModel):
    """Service health check result."""

    status: str = Field(
        ...,
        description="Service status (healthy, unhealthy, degraded)",
        examples=["healthy"],
    )
    response_time_ms: float | None = Field(
        None,
        description="Response time in milliseconds",
        examples=[5.2],
    )
    error: str | None = Field(
        None,
        description="Error message if service is unhealthy",
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(
        ...,
        description="Overall system status (healthy, unhealthy, degraded)",
        examples=["healthy"],
    )
    timestamp: datetime = Field(
        ...,
        description="Current server timestamp (ISO 8601, UTC)",
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["0.1.0"],
    )
    checks: dict[str, ServiceCheck] = Field(
        ...,
        description="Individual service health checks",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies (database, cache).",
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2026-01-09T10:00:00Z",
                        "version": "0.1.0",
                        "checks": {"database": {"status": "healthy", "response_time_ms": 5.2}},
                    }
                }
            },
        },
        503: {
            "description": "System is unhealthy",
        },
    },
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check application and dependency health.

    This endpoint verifies:
    - Database connectivity and responsiveness
    - Overall system status

    Args:
        db: Database session (injected)

    Returns:
        HealthResponse: Health status of all services
    """
    checks: dict[str, ServiceCheck] = {}
    overall_status = "healthy"

    # Check database health
    try:
        start_time = datetime.now(UTC)
        await db.execute(text("SELECT 1"))
        end_time = datetime.now(UTC)
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        checks["database"] = ServiceCheck(
            status="healthy",
            response_time_ms=response_time_ms,
        )
        logger.debug("database_health_check_passed", response_time_ms=response_time_ms)
    except Exception as e:
        checks["database"] = ServiceCheck(
            status="unhealthy",
            error=str(e),
        )
        overall_status = "unhealthy"
        logger.error("database_health_check_failed", error=str(e), error_type=type(e).__name__)

    # Log health check
    logger.info(
        "health_check_completed",
        overall_status=overall_status,
        database_status=checks.get("database", ServiceCheck(status="unknown")).status,
    )

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC),
        version="0.1.0",
        checks=checks,
    )
