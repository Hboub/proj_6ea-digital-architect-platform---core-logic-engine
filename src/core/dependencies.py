"""
Dependency injection utilities for FastAPI.
"""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

logger = logging.getLogger(__name__)


async def get_request_id(request: Request) -> str:
    """Extract request ID from request state."""
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        logger.warning("Request ID not found in request state")
        return "unknown"
    return request_id


async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    """Verify API key from request headers."""
    if not x_api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(status_code=401, detail="Missing API key")

    # TODO: Implement actual API key verification
    # For now, just validate that the key is not empty
    if not x_api_key.strip():
        logger.warning("Invalid API key provided")
        raise HTTPException(status_code=401, detail="Invalid API key")

    return x_api_key


RequestIdDep = Annotated[str, Depends(get_request_id)]
ApiKeyDep = Annotated[str, Depends(verify_api_key)]
