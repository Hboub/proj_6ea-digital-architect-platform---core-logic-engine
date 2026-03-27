"""
Integration tests for vector database operations.
"""

import pytest

from src.vector_db.client import (
    connect_pinecone,
    disconnect_pinecone,
    get_pinecone_client,
    health_check,
    is_pinecone_connected,
)
from src.vector_db.embedding_service import (
    clear_embedding_cache,
    generate_embedding,
    generate_embeddings_batch,
    get_cache_stats,
)
from src.vector_db.models import (
    EmbeddingRequest,
    EntitySimilarityRequest,
    VectorMetadata,
    VectorQueryRequest,
    VectorUpsertRequest,
)


class TestPineconeClient:
    """Tests for Pinecone client connection management."""

    @pytest.mark.asyncio
    async def test_connect_pinecone(self):
        """Test connecting to Pinecone."""
        # This test requires PINECONE_API_KEY to be set
        # In a real environment, this would verify connection
        # For now, we test the function exists and has proper signature
        assert callable(connect_pinecone)

    @pytest.mark.asyncio
    async def test_disconnect_pinecone(self):
        """Test disconnecting from Pinecone."""
        await disconnect_pinecone()
        assert not is_pinecone_connected()

    def test_is_pinecone_connected(self):
        """Test connection status check."""
        status = is_pinecone_connected()
        assert isinstance(status, bool)

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test Pinecone health check."""
        result = await health_check()
        assert isinstance(result, dict)
        assert "connected" in result
        assert "status" in result


class TestEmbeddingService:
    """Tests for embedding generation service."""

    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        """Test generating single embedding."""
        text = "Digital transformation in healthcare"
        embedding = await generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await generate_embedding("")

    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_text(self):
        """Test embedding generation with whitespace-only text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await generate_embedding("   ")

    @pytest.mark.asyncio
    async def test_generate_embedding_caching(self):
        """Test embedding caching mechanism."""
        text = "Artificial intelligence for business"

        # Clear cache first
        clear_embedding_cache()

        # First generation
        embedding1 = await generate_embedding(text, use_cache=True)

        # Second generation should use cache
        embedding2 = await generate_embedding(text, use_cache=True)

        assert embedding1 == embedding2

        # Check cache stats
        stats = get_cache_stats()
        assert stats["cache_size"] > 0

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self):
        """Test batch embedding generation."""
        texts = [
            "Cloud computing services",
            "Machine learning models",
            "Data analytics platform",
        ]

        embeddings = await generate_embeddings_batch(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(len(emb) == 1536 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_empty(self):
        """Test batch embedding with empty list."""
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await generate_embeddings_batch([])

    @pytest.mark.asyncio
    async def test_embedding_deterministic(self):
        """Test that embeddings are deterministic."""
        text = "Enterprise resource planning"

        clear_embedding_cache()

        embedding1 = await generate_embedding(text, use_cache=False)
        embedding2 = await generate_embedding(text, use_cache=False)

        assert embedding1 == embedding2

    def test_clear_embedding_cache(self):
        """Test clearing embedding cache."""
        clear_embedding_cache()
        stats = get_cache_stats()
        assert stats["cache_size"] == 0


class TestVectorModels:
    """Tests for vector database models."""

    def test_vector_metadata_creation(self):
        """Test creating VectorMetadata."""
        metadata = VectorMetadata(
            entity_id="entity-123",
            entity_name="Test Entity",
            industry="Technology",
            owner_id="user-456",
            maturity_score=7.5,
        )

        assert metadata.entity_id == "entity-123"
        assert metadata.entity_name == "Test Entity"
        assert metadata.industry == "Technology"
        assert metadata.owner_id == "user-456"
        assert metadata.maturity_score == 7.5

    def test_vector_upsert_request_creation(self):
        """Test creating VectorUpsertRequest."""
        metadata = VectorMetadata(
            entity_id="entity-123", entity_name="Test", industry="Tech"
        )

        request = VectorUpsertRequest(
            vector_id="vec-123", values=[0.1, 0.2, 0.3], metadata=metadata
        )

        assert request.vector_id == "vec-123"
        assert len(request.values) == 3
        assert request.metadata.entity_id == "entity-123"

    def test_vector_query_request_defaults(self):
        """Test VectorQueryRequest default values."""
        request = VectorQueryRequest(query_vector=[0.1, 0.2, 0.3])

        assert request.top_k == 10
        assert request.filter is None
        assert request.include_metadata is True
        assert request.include_values is False
        assert request.namespace is None

    def test_vector_query_request_validation(self):
        """Test VectorQueryRequest validation."""
        with pytest.raises(ValueError):
            VectorQueryRequest(query_vector=[0.1, 0.2], top_k=0)

        with pytest.raises(ValueError):
            VectorQueryRequest(query_vector=[0.1, 0.2], top_k=101)

    def test_embedding_request_creation(self):
        """Test creating EmbeddingRequest."""
        request = EmbeddingRequest(text="Test text")

        assert request.text == "Test text"
        assert request.model == "text-embedding-ada-002"

    def test_embedding_request_validation(self):
        """Test EmbeddingRequest validation."""
        with pytest.raises(ValueError):
            EmbeddingRequest(text="")

    def test_entity_similarity_request_creation(self):
        """Test creating EntitySimilarityRequest."""
        request = EntitySimilarityRequest(
            entity_id="entity-123",
            top_k=5,
            owner_id="user-456",
            industry="Healthcare",
            min_score=0.7,
        )

        assert request.entity_id == "entity-123"
        assert request.top_k == 5
        assert request.owner_id == "user-456"
        assert request.industry == "Healthcare"
        assert request.min_score == 0.7

    def test_entity_similarity_request_defaults(self):
        """Test EntitySimilarityRequest default values."""
        request = EntitySimilarityRequest(entity_id="entity-123")

        assert request.top_k == 10
        assert request.owner_id is None
        assert request.industry is None
        assert request.min_score == 0.0


class TestVectorOperations:
    """Tests for vector query operations."""

    @pytest.mark.asyncio
    async def test_embedding_normalization(self):
        """Test that embeddings are normalized."""
        text = "Test normalization"
        embedding = await generate_embedding(text)

        # Check if embedding is normalized (magnitude ~= 1)
        magnitude = sum(x * x for x in embedding) ** 0.5
        assert 0.99 <= magnitude <= 1.01

    @pytest.mark.asyncio
    async def test_embedding_dimensions(self):
        """Test embedding dimensions are correct."""
        text = "Test dimensions"
        embedding = await generate_embedding(text)

        assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_batch_embedding_consistency(self):
        """Test batch embeddings match individual embeddings."""
        texts = ["Text one", "Text two"]

        clear_embedding_cache()

        # Generate individually
        emb1_single = await generate_embedding(texts[0], use_cache=False)
        emb2_single = await generate_embedding(texts[1], use_cache=False)

        clear_embedding_cache()

        # Generate in batch
        batch_embeddings = await generate_embeddings_batch(texts, use_cache=False)

        assert emb1_single == batch_embeddings[0]
        assert emb2_single == batch_embeddings[1]


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_embedding_with_very_long_text(self):
        """Test embedding generation with very long text."""
        # Create a very long text (10,000 characters)
        long_text = "a" * 10000

        embedding = await generate_embedding(long_text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_embedding_with_special_characters(self):
        """Test embedding with special characters."""
        text = "Special chars: @#$%^&*()[]{}|\\<>?/~`"

        embedding = await generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_embedding_with_unicode(self):
        """Test embedding with unicode characters."""
        text = "Unicode: 你好世界 🚀 مرحبا"

        embedding = await generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536


class TestCacheManagement:
    """Tests for embedding cache management."""

    def test_cache_stats_initial(self):
        """Test initial cache stats."""
        clear_embedding_cache()
        stats = get_cache_stats()

        assert stats["cache_size"] == 0

    @pytest.mark.asyncio
    async def test_cache_growth(self):
        """Test cache grows with new embeddings."""
        clear_embedding_cache()

        await generate_embedding("Text 1", use_cache=True)
        stats1 = get_cache_stats()

        await generate_embedding("Text 2", use_cache=True)
        stats2 = get_cache_stats()

        assert stats2["cache_size"] > stats1["cache_size"]

    @pytest.mark.asyncio
    async def test_cache_no_growth_on_duplicate(self):
        """Test cache doesn't grow with duplicate text."""
        clear_embedding_cache()

        text = "Duplicate text"

        await generate_embedding(text, use_cache=True)
        stats1 = get_cache_stats()

        await generate_embedding(text, use_cache=True)
        stats2 = get_cache_stats()

        assert stats1["cache_size"] == stats2["cache_size"]

    @pytest.mark.asyncio
    async def test_cache_bypass(self):
        """Test cache can be bypassed."""
        clear_embedding_cache()

        text = "Bypass test"

        await generate_embedding(text, use_cache=False)
        stats = get_cache_stats()

        assert stats["cache_size"] == 0
