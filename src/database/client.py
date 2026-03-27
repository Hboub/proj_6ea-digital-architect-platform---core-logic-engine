"""
Prisma database client setup with connection management and async support.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from prisma import Prisma

logger = logging.getLogger(__name__)

# Global Prisma client instance
_prisma_client: Optional[Prisma] = None


def get_db_client() -> Prisma:
    """
    Get the global Prisma client instance.

    Returns:
        Prisma: The Prisma client instance

    Raises:
        RuntimeError: If database client is not initialized
    """
    if _prisma_client is None:
        raise RuntimeError(
            "Database client not initialized. Call connect_db() first."
        )
    return _prisma_client


async def connect_db() -> None:
    """
    Initialize and connect to the database.

    This function should be called during application startup.

    Raises:
        Exception: If connection fails
    """
    global _prisma_client

    if _prisma_client is not None:
        logger.warning("Database client already initialized")
        return

    try:
        logger.info("Initializing Prisma database client")
        _prisma_client = Prisma()

        logger.info("Connecting to database")
        await _prisma_client.connect()

        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        _prisma_client = None
        raise


async def disconnect_db() -> None:
    """
    Disconnect from the database and cleanup resources.

    This function should be called during application shutdown.
    """
    global _prisma_client

    if _prisma_client is None:
        logger.warning("Database client not initialized, nothing to disconnect")
        return

    try:
        logger.info("Disconnecting from database")
        await _prisma_client.disconnect()
        logger.info("Database disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}", exc_info=True)
    finally:
        _prisma_client = None


async def is_connected() -> bool:
    """
    Check if the database is connected.

    Returns:
        bool: True if connected, False otherwise
    """
    if _prisma_client is None:
        return False

    try:
        await _prisma_client.execute_raw("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


@asynccontextmanager
async def get_db() -> AsyncIterator[Prisma]:
    """
    Context manager for getting the database client.

    This provides the Prisma client for dependency injection in FastAPI routes.

    Yields:
        Prisma: The Prisma client instance

    Raises:
        RuntimeError: If database client is not initialized

    Example:
        async with get_db() as db:
            entities = await db.entity.find_many()
    """
    client = get_db_client()
    try:
        yield client
    except Exception as e:
        logger.error(f"Error during database operation: {e}", exc_info=True)
        raise


async def health_check() -> dict[str, str]:
    """
    Perform a database health check.

    Returns:
        dict[str, str]: Health check status

    Example:
        {
            "status": "healthy",
            "database": "connected"
        }
    """
    try:
        connected = await is_connected()
        if connected:
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "unhealthy", "database": "error", "error": str(e)}
