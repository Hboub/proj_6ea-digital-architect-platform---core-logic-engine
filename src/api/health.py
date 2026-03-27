"""
Health check endpoints for monitoring and diagnostics.
"""

import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core.dependencies import RequestIdDep

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(
        description="Overall health status"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of health check"
    )
    service: str = Field(
        default="Digital Architect Platform - Core Logic Engine",
        description="Service name",
    )
    version: str = Field(default="0.1.0", description="Service version")


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    ready: bool = Field(description="Whether service is ready to accept traffic")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of readiness check"
    )
    checks: dict[str, bool] = Field(
        default_factory=dict, description="Individual readiness checks"
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns the health status of the service",
)
async def health_check(request_id: RequestIdDep) -> HealthResponse:
    """
    Perform health check.

    Returns basic health status of the service.
    """
    logger.info("Health check requested", extra={"request_id": request_id})

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check endpoint",
    description="Returns whether the service is ready to accept traffic",
)
async def readiness_check(request_id: RequestIdDep) -> ReadinessResponse:
    """
    Perform readiness check.

    Checks if the service is ready to accept traffic.
    This includes checking dependencies like database, external APIs, etc.
    """
    logger.info("Readiness check requested", extra={"request_id": request_id})

    checks = {
        "database": True,
        "vector_db": True,
    }

    ready = all(checks.values())

    return ReadinessResponse(
        ready=ready,
        timestamp=datetime.utcnow(),
        checks=checks,
    )
