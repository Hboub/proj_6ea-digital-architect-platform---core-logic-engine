"""
FastAPI application entry point with middleware and routing configuration.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.health import router as health_router
from src.core.middleware import ErrorHandlingMiddleware, RequestContextMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for startup and shutdown events."""
    logger.info("Starting Digital Architect Platform - Core Logic Engine")
    yield
    logger.info("Shutting down Digital Architect Platform - Core Logic Engine")


app = FastAPI(
    title="Digital Architect Platform - Core Logic Engine",
    description="FastAPI business intelligence platform - Core Logic Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Include routers
app.include_router(health_router, tags=["health"])
