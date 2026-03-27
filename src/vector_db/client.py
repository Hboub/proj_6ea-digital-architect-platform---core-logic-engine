"""
Pinecone client setup with async operations and connection management.
"""

import logging
from typing import Optional

from pinecone import Pinecone, ServerlessSpec

from src.core.config import settings

logger = logging.getLogger(__name__)

# Global Pinecone client instance
_client: Optional[Pinecone] = None
_connected: bool = False


def get_pinecone_client() -> Pinecone:
    """
    Get or create the Pinecone client instance.

    Returns:
        Pinecone: Configured Pinecone client

    Raises:
        ValueError: If Pinecone API key is not configured
    """
    global _client

    if _client is None:
        if not settings.pinecone_api_key:
            raise ValueError(
                "Pinecone API key not configured. Set PINECONE_API_KEY environment variable."
            )

        logger.info("Initializing Pinecone client")
        _client = Pinecone(api_key=settings.pinecone_api_key)
        logger.info("Pinecone client initialized successfully")

    return _client


async def connect_pinecone() -> None:
    """
    Connect to Pinecone and verify connection.

    This function initializes the Pinecone client and verifies
    connectivity by listing available indexes.

    Raises:
        Exception: If connection fails
    """
    global _connected

    if _connected:
        logger.debug("Pinecone already connected")
        return

    try:
        logger.info("Connecting to Pinecone")
        client = get_pinecone_client()

        # Verify connection by listing indexes
        indexes = client.list_indexes()
        logger.info(
            "Connected to Pinecone successfully",
            extra={"available_indexes": len(indexes.indexes)},
        )

        _connected = True

    except Exception as e:
        logger.error("Failed to connect to Pinecone", extra={"error": str(e)})
        raise


async def disconnect_pinecone() -> None:
    """
    Disconnect from Pinecone.

    Cleans up the global client instance.
    """
    global _client, _connected

    if _client is not None:
        logger.info("Disconnecting from Pinecone")
        _client = None
        _connected = False
        logger.info("Disconnected from Pinecone successfully")


def is_pinecone_connected() -> bool:
    """
    Check if Pinecone is connected.

    Returns:
        bool: True if connected, False otherwise
    """
    return _connected


def get_index(index_name: Optional[str] = None):
    """
    Get a Pinecone index instance.

    Args:
        index_name: Name of the index. If None, uses default from settings.

    Returns:
        Index: Pinecone index instance

    Raises:
        ValueError: If index name is not provided and not in settings
        Exception: If index does not exist
    """
    client = get_pinecone_client()

    if index_name is None:
        index_name = settings.pinecone_index_name

    if not index_name:
        raise ValueError(
            "Index name not provided and PINECONE_INDEX_NAME not configured"
        )

    try:
        logger.debug("Getting Pinecone index", extra={"index_name": index_name})
        index = client.Index(index_name)
        return index
    except Exception as e:
        logger.error(
            "Failed to get Pinecone index",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


async def health_check() -> dict:
    """
    Perform health check on Pinecone connection.

    Returns:
        dict: Health check results with status and details

    Example:
        {
            "connected": True,
            "indexes_count": 1,
            "status": "healthy"
        }
    """
    try:
        if not _connected:
            await connect_pinecone()

        client = get_pinecone_client()
        indexes = client.list_indexes()

        return {
            "connected": True,
            "indexes_count": len(indexes.indexes),
            "status": "healthy",
        }

    except Exception as e:
        logger.error("Pinecone health check failed", extra={"error": str(e)})
        return {"connected": False, "status": "unhealthy", "error": str(e)}
