"""
Vector similarity search and query service.
"""

import logging
from typing import Any, Optional

from src.vector_db.client import get_index
from src.vector_db.embedding_service import generate_embedding
from src.vector_db.models import (
    EntitySimilarityRequest,
    EntitySimilarityResponse,
    EntitySimilarityResult,
    VectorMatch,
    VectorQueryRequest,
    VectorQueryResponse,
)

logger = logging.getLogger(__name__)


async def query_vectors(
    request: VectorQueryRequest, index_name: Optional[str] = None
) -> VectorQueryResponse:
    """
    Query vectors from Pinecone index with metadata filtering.

    Args:
        request: Query request with vector and filters
        index_name: Optional index name override

    Returns:
        VectorQueryResponse: Query results with matches

    Raises:
        Exception: If query fails
    """
    try:
        logger.info(
            "Querying vectors",
            extra={
                "top_k": request.top_k,
                "has_filter": request.filter is not None,
                "namespace": request.namespace,
            },
        )

        index = get_index(index_name)

        # Execute query
        query_params = {
            "vector": request.query_vector,
            "top_k": request.top_k,
            "include_metadata": request.include_metadata,
            "include_values": request.include_values,
        }

        if request.filter:
            query_params["filter"] = request.filter

        if request.namespace:
            query_params["namespace"] = request.namespace

        response = index.query(**query_params)

        # Convert to response model
        matches = []
        if hasattr(response, "matches"):
            for match in response.matches:
                vector_match = VectorMatch(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata if request.include_metadata else None,
                    values=match.values if request.include_values else None,
                )
                matches.append(vector_match)

        logger.info(
            "Vector query completed",
            extra={"matches_count": len(matches)},
        )

        return VectorQueryResponse(matches=matches, namespace=request.namespace)

    except Exception as e:
        logger.error("Vector query failed", extra={"error": str(e)})
        raise


async def query_by_text(
    text: str,
    top_k: int = 10,
    filter: Optional[dict[str, Any]] = None,
    owner_id: Optional[str] = None,
    index_name: Optional[str] = None,
) -> VectorQueryResponse:
    """
    Query vectors by text similarity.

    Args:
        text: Query text
        top_k: Number of results to return
        filter: Metadata filter criteria
        owner_id: Filter by owner ID for multi-tenant isolation
        index_name: Optional index name override

    Returns:
        VectorQueryResponse: Query results

    Raises:
        ValueError: If text is empty
        Exception: If query fails
    """
    if not text or not text.strip():
        raise ValueError("Query text cannot be empty")

    try:
        logger.info(
            "Querying by text",
            extra={"text_length": len(text), "top_k": top_k},
        )

        # Generate embedding for query text
        query_vector = await generate_embedding(text)

        # Add owner filter for multi-tenant isolation
        if owner_id:
            if filter is None:
                filter = {}
            filter["owner_id"] = owner_id

        # Create query request
        request = VectorQueryRequest(
            query_vector=query_vector,
            top_k=top_k,
            filter=filter,
            include_metadata=True,
            include_values=False,
        )

        return await query_vectors(request, index_name)

    except Exception as e:
        logger.error("Text query failed", extra={"error": str(e)})
        raise


async def find_similar_entities(
    request: EntitySimilarityRequest, index_name: Optional[str] = None
) -> EntitySimilarityResponse:
    """
    Find similar entities based on vector similarity.

    Args:
        request: Entity similarity request
        index_name: Optional index name override

    Returns:
        EntitySimilarityResponse: Similar entities results

    Raises:
        Exception: If query fails
    """
    try:
        logger.info(
            "Finding similar entities",
            extra={
                "entity_id": request.entity_id,
                "top_k": request.top_k,
            },
        )

        index = get_index(index_name)

        # Fetch the source entity vector
        fetch_response = index.fetch(ids=[request.entity_id])

        if not fetch_response.vectors or request.entity_id not in fetch_response.vectors:
            raise ValueError(f"Entity {request.entity_id} not found in vector database")

        source_vector = fetch_response.vectors[request.entity_id]

        # Build metadata filter
        filter_criteria: dict[str, Any] = {}

        if request.owner_id:
            filter_criteria["owner_id"] = request.owner_id

        if request.industry:
            filter_criteria["industry"] = request.industry

        # Query similar vectors
        query_params = {
            "vector": source_vector.values,
            "top_k": request.top_k + 1,  # +1 to exclude self
            "include_metadata": True,
            "include_values": False,
        }

        if filter_criteria:
            query_params["filter"] = filter_criteria

        response = index.query(**query_params)

        # Process results
        results = []
        for match in response.matches:
            # Skip the source entity itself
            if match.id == request.entity_id:
                continue

            # Apply minimum score filter
            if match.score < request.min_score:
                continue

            # Extract metadata
            metadata = match.metadata or {}

            result = EntitySimilarityResult(
                entity_id=match.id,
                entity_name=metadata.get("entity_name", "Unknown"),
                industry=metadata.get("industry", "Unknown"),
                similarity_score=match.score,
                maturity_score=metadata.get("maturity_score"),
            )
            results.append(result)

        # Limit to requested top_k
        results = results[: request.top_k]

        logger.info(
            "Similar entities found",
            extra={"count": len(results)},
        )

        return EntitySimilarityResponse(
            source_entity_id=request.entity_id,
            results=results,
            total_results=len(results),
        )

    except Exception as e:
        logger.error("Failed to find similar entities", extra={"error": str(e)})
        raise


async def query_by_metadata(
    filter: dict[str, Any],
    top_k: int = 100,
    index_name: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Query vectors by metadata filter only.

    Args:
        filter: Metadata filter criteria
        top_k: Maximum number of results
        index_name: Optional index name override

    Returns:
        list[dict]: List of matching vectors with metadata

    Raises:
        ValueError: If filter is empty
        Exception: If query fails
    """
    if not filter:
        raise ValueError("Filter criteria cannot be empty")

    try:
        logger.info(
            "Querying by metadata",
            extra={"filter": filter, "top_k": top_k},
        )

        index = get_index(index_name)

        # Use a zero vector for metadata-only filtering
        # This is a workaround since Pinecone requires a vector for queries
        dummy_vector = [0.0] * 1536  # Assuming 1536 dimensions

        response = index.query(
            vector=dummy_vector,
            top_k=top_k,
            filter=filter,
            include_metadata=True,
            include_values=False,
        )

        results = []
        for match in response.matches:
            results.append(
                {"id": match.id, "score": match.score, "metadata": match.metadata}
            )

        logger.info(
            "Metadata query completed",
            extra={"results_count": len(results)},
        )

        return results

    except Exception as e:
        logger.error("Metadata query failed", extra={"error": str(e)})
        raise
