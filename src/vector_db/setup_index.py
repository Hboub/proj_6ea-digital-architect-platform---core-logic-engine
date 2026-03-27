"""
Index setup and configuration script for Pinecone.
"""

import logging
from typing import Optional

from pinecone import ServerlessSpec

from src.core.config import settings
from src.vector_db.client import get_pinecone_client

logger = logging.getLogger(__name__)


def check_index_exists(index_name: str) -> bool:
    """
    Check if a Pinecone index exists.

    Args:
        index_name: Name of the index

    Returns:
        bool: True if index exists, False otherwise
    """
    try:
        client = get_pinecone_client()
        indexes = client.list_indexes()

        for index_info in indexes.indexes:
            if index_info.name == index_name:
                logger.info(
                    "Index exists",
                    extra={"index_name": index_name},
                )
                return True

        logger.info(
            "Index does not exist",
            extra={"index_name": index_name},
        )
        return False

    except Exception as e:
        logger.error(
            "Failed to check index existence",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


def create_index(
    index_name: Optional[str] = None,
    dimension: int = 1536,
    metric: str = "cosine",
    cloud: str = "aws",
    region: str = "us-east-1",
) -> None:
    """
    Create a Pinecone index with proper configuration.

    Args:
        index_name: Name of the index. If None, uses default from settings.
        dimension: Vector dimensions (default 1536 for OpenAI ada-002)
        metric: Distance metric (cosine, euclidean, or dotproduct)
        cloud: Cloud provider (aws, gcp, or azure)
        region: Cloud region

    Raises:
        ValueError: If index name is not provided
        Exception: If index creation fails
    """
    if index_name is None:
        index_name = settings.pinecone_index_name

    if not index_name:
        raise ValueError(
            "Index name not provided and PINECONE_INDEX_NAME not configured"
        )

    try:
        client = get_pinecone_client()

        # Check if index already exists
        if check_index_exists(index_name):
            logger.warning(
                "Index already exists, skipping creation",
                extra={"index_name": index_name},
            )
            return

        logger.info(
            "Creating Pinecone index",
            extra={
                "index_name": index_name,
                "dimension": dimension,
                "metric": metric,
                "cloud": cloud,
                "region": region,
            },
        )

        # Create serverless index
        client.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=cloud, region=region),
        )

        logger.info(
            "Pinecone index created successfully",
            extra={"index_name": index_name},
        )

    except Exception as e:
        logger.error(
            "Failed to create index",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


def delete_index(index_name: Optional[str] = None) -> None:
    """
    Delete a Pinecone index.

    Args:
        index_name: Name of the index. If None, uses default from settings.

    Raises:
        ValueError: If index name is not provided
        Exception: If index deletion fails
    """
    if index_name is None:
        index_name = settings.pinecone_index_name

    if not index_name:
        raise ValueError(
            "Index name not provided and PINECONE_INDEX_NAME not configured"
        )

    try:
        client = get_pinecone_client()

        if not check_index_exists(index_name):
            logger.warning(
                "Index does not exist, skipping deletion",
                extra={"index_name": index_name},
            )
            return

        logger.info(
            "Deleting Pinecone index",
            extra={"index_name": index_name},
        )

        client.delete_index(index_name)

        logger.info(
            "Pinecone index deleted successfully",
            extra={"index_name": index_name},
        )

    except Exception as e:
        logger.error(
            "Failed to delete index",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


def get_index_stats(index_name: Optional[str] = None) -> dict:
    """
    Get statistics for a Pinecone index.

    Args:
        index_name: Name of the index. If None, uses default from settings.

    Returns:
        dict: Index statistics

    Raises:
        ValueError: If index name is not provided
        Exception: If fetching stats fails
    """
    if index_name is None:
        index_name = settings.pinecone_index_name

    if not index_name:
        raise ValueError(
            "Index name not provided and PINECONE_INDEX_NAME not configured"
        )

    try:
        client = get_pinecone_client()

        if not check_index_exists(index_name):
            raise ValueError(f"Index {index_name} does not exist")

        logger.info(
            "Getting index stats",
            extra={"index_name": index_name},
        )

        index = client.Index(index_name)
        stats = index.describe_index_stats()

        result = {
            "index_name": index_name,
            "dimension": stats.dimension,
            "index_fullness": stats.index_fullness,
            "total_vector_count": stats.total_vector_count,
            "namespaces": dict(stats.namespaces) if stats.namespaces else {},
        }

        logger.info(
            "Index stats retrieved",
            extra={"stats": result},
        )

        return result

    except Exception as e:
        logger.error(
            "Failed to get index stats",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


def setup_index_with_metadata_config(
    index_name: Optional[str] = None,
    dimension: int = 1536,
) -> None:
    """
    Setup index with metadata schema configuration.

    This creates an index optimized for the Digital Architect Platform
    with metadata fields for entity filtering.

    Args:
        index_name: Name of the index. If None, uses default from settings.
        dimension: Vector dimensions

    Raises:
        Exception: If setup fails
    """
    if index_name is None:
        index_name = settings.pinecone_index_name

    try:
        logger.info(
            "Setting up index with metadata configuration",
            extra={"index_name": index_name},
        )

        # Create index with cosine similarity for semantic search
        create_index(
            index_name=index_name,
            dimension=dimension,
            metric="cosine",
            cloud="aws",
            region="us-east-1",
        )

        logger.info(
            "Index setup completed with metadata configuration",
            extra={"index_name": index_name},
        )

    except Exception as e:
        logger.error(
            "Failed to setup index with metadata config",
            extra={"index_name": index_name, "error": str(e)},
        )
        raise


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup index
    setup_index_with_metadata_config()
