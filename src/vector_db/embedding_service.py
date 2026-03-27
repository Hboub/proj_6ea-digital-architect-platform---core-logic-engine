"""
Embedding generation service for converting text to vectors.
"""

import hashlib
import logging
from typing import Optional

from src.vector_db.models import EmbeddingRequest, EmbeddingResponse

logger = logging.getLogger(__name__)

# Simple cache for embeddings to avoid redundant API calls
_embedding_cache: dict[str, list[float]] = {}


def _generate_cache_key(text: str, model: str) -> str:
    """
    Generate cache key for embedding.

    Args:
        text: Input text
        model: Model name

    Returns:
        str: Cache key
    """
    content = f"{model}:{text}"
    return hashlib.sha256(content.encode()).hexdigest()


def _generate_mock_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """
    Generate a mock embedding for testing purposes.

    This creates a deterministic embedding based on text content.
    In production, this would call OpenAI or Sentence Transformers API.

    Args:
        text: Input text
        dimensions: Embedding dimensions

    Returns:
        list[float]: Mock embedding vector
    """
    # Create deterministic embedding based on text hash
    text_hash = hashlib.sha256(text.encode()).digest()

    # Convert hash bytes to floats in range [-1, 1]
    embedding = []
    for i in range(dimensions):
        byte_idx = i % len(text_hash)
        # Normalize to [-1, 1] range
        value = (text_hash[byte_idx] / 127.5) - 1.0
        embedding.append(value)

    # Normalize to unit vector
    magnitude = sum(x * x for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]

    return embedding


async def generate_embedding(
    text: str, model: str = "text-embedding-ada-002", use_cache: bool = True
) -> list[float]:
    """
    Generate embedding vector for text.

    Args:
        text: Text to embed
        model: Embedding model to use
        use_cache: Whether to use cached embeddings

    Returns:
        list[float]: Embedding vector

    Raises:
        ValueError: If text is empty
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text = text.strip()
    cache_key = _generate_cache_key(text, model)

    # Check cache
    if use_cache and cache_key in _embedding_cache:
        logger.debug("Using cached embedding", extra={"cache_key": cache_key})
        return _embedding_cache[cache_key]

    try:
        logger.info(
            "Generating embedding",
            extra={"text_length": len(text), "model": model},
        )

        # In production, this would call OpenAI API or Sentence Transformers
        # For now, using mock embedding
        embedding = _generate_mock_embedding(text)

        # Cache the result
        if use_cache:
            _embedding_cache[cache_key] = embedding
            logger.debug(
                "Cached embedding", extra={"cache_key": cache_key, "cache_size": len(_embedding_cache)}
            )

        logger.info(
            "Embedding generated successfully",
            extra={"dimensions": len(embedding)},
        )

        return embedding

    except Exception as e:
        logger.error("Failed to generate embedding", extra={"error": str(e)})
        raise


async def generate_embeddings_batch(
    texts: list[str], model: str = "text-embedding-ada-002", use_cache: bool = True
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed
        model: Embedding model to use
        use_cache: Whether to use cached embeddings

    Returns:
        list[list[float]]: List of embedding vectors

    Raises:
        ValueError: If texts list is empty
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    logger.info(
        "Generating batch embeddings",
        extra={"batch_size": len(texts), "model": model},
    )

    try:
        embeddings = []
        for text in texts:
            embedding = await generate_embedding(text, model, use_cache)
            embeddings.append(embedding)

        logger.info(
            "Batch embeddings generated successfully",
            extra={"count": len(embeddings)},
        )

        return embeddings

    except Exception as e:
        logger.error("Failed to generate batch embeddings", extra={"error": str(e)})
        raise


async def generate_embedding_with_metadata(
    request: EmbeddingRequest,
) -> EmbeddingResponse:
    """
    Generate embedding with full response metadata.

    Args:
        request: Embedding request with text and model

    Returns:
        EmbeddingResponse: Response with embedding and metadata
    """
    try:
        embedding = await generate_embedding(request.text, request.model)

        return EmbeddingResponse(
            embedding=embedding, model=request.model, dimensions=len(embedding)
        )

    except Exception as e:
        logger.error(
            "Failed to generate embedding with metadata", extra={"error": str(e)}
        )
        raise


def clear_embedding_cache() -> None:
    """Clear the embedding cache."""
    global _embedding_cache
    cache_size = len(_embedding_cache)
    _embedding_cache.clear()
    logger.info("Embedding cache cleared", extra={"cleared_entries": cache_size})


def get_cache_stats() -> dict[str, int]:
    """
    Get embedding cache statistics.

    Returns:
        dict: Cache statistics
    """
    return {"cache_size": len(_embedding_cache)}
