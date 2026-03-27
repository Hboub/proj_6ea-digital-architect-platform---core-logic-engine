"""
Custom middleware for request handling and error management.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request context and correlation ID."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and add context."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(
                "Unhandled exception in request processing",
                extra={"request_id": request_id},
            )
            raise
        finally:
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "process_time": f"{process_time:.3f}s",
                    "status_code": response.status_code
                    if "response" in locals()
                    else None,
                },
            )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Handle errors and return appropriate responses."""
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                "Validation error",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "message": str(e),
                    "request_id": request_id,
                },
            )
        except Exception as e:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.exception(
                "Internal server error",
                extra={"request_id": request_id, "error": str(e)},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id,
                },
            )
