"""
Pydantic models for vector operations and metadata schemas.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class VectorMetadata(BaseModel):
    """Metadata for vector embeddings."""

    entity_id: str = Field(..., description="Entity identifier")
    entity_name: str = Field(..., description="Entity name")
    industry: str = Field(..., description="Industry classification")
    owner_id: Optional[str] = Field(None, description="Owner user ID")
    entity_type: str = Field(default="entity", description="Type of entity")
    maturity_score: Optional[float] = Field(None, description="Maturity score")
    content_type: str = Field(
        default="description", description="Type of content embedded"
    )
    timestamp: Optional[str] = Field(None, description="Timestamp of embedding")

    model_config = {"extra": "allow"}


class VectorUpsertRequest(BaseModel):
    """Request model for upserting vectors to Pinecone."""

    vector_id: str = Field(..., description="Unique vector identifier")
    values: list[float] = Field(..., description="Vector embedding values")
    metadata: VectorMetadata = Field(..., description="Vector metadata")

    model_config = {"extra": "forbid"}


class VectorQueryRequest(BaseModel):
    """Request model for querying vectors from Pinecone."""

    query_vector: list[float] = Field(..., description="Query vector embedding")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    filter: Optional[dict[str, Any]] = Field(
        None, description="Metadata filter criteria"
    )
    include_metadata: bool = Field(
        default=True, description="Include metadata in results"
    )
    include_values: bool = Field(
        default=False, description="Include vector values in results"
    )
    namespace: Optional[str] = Field(None, description="Namespace to query")

    model_config = {"extra": "forbid"}


class VectorMatch(BaseModel):
    """Single vector match result."""

    id: str = Field(..., description="Vector identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Optional[dict[str, Any]] = Field(None, description="Vector metadata")
    values: Optional[list[float]] = Field(None, description="Vector values")

    model_config = {"extra": "allow"}


class VectorQueryResponse(BaseModel):
    """Response model for vector query results."""

    matches: list[VectorMatch] = Field(default_factory=list, description="Match results")
    namespace: Optional[str] = Field(None, description="Namespace queried")

    model_config = {"extra": "allow"}


class EmbeddingRequest(BaseModel):
    """Request model for generating embeddings."""

    text: str = Field(..., min_length=1, description="Text to embed")
    model: str = Field(
        default="text-embedding-ada-002", description="Embedding model to use"
    )

    model_config = {"extra": "forbid"}


class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""

    embedding: list[float] = Field(..., description="Generated embedding vector")
    model: str = Field(..., description="Model used for embedding")
    dimensions: int = Field(..., description="Dimensionality of embedding")

    model_config = {"extra": "allow"}


class EntitySimilarityRequest(BaseModel):
    """Request model for entity similarity search."""

    entity_id: str = Field(..., description="Source entity identifier")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    owner_id: Optional[str] = Field(None, description="Filter by owner")
    industry: Optional[str] = Field(None, description="Filter by industry")
    min_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum similarity score"
    )

    model_config = {"extra": "forbid"}


class EntitySimilarityResult(BaseModel):
    """Single entity similarity result."""

    entity_id: str = Field(..., description="Entity identifier")
    entity_name: str = Field(..., description="Entity name")
    industry: str = Field(..., description="Industry classification")
    similarity_score: float = Field(..., description="Similarity score")
    maturity_score: Optional[float] = Field(None, description="Maturity score")

    model_config = {"extra": "allow"}


class EntitySimilarityResponse(BaseModel):
    """Response model for entity similarity search."""

    source_entity_id: str = Field(..., description="Source entity identifier")
    results: list[EntitySimilarityResult] = Field(
        default_factory=list, description="Similar entities"
    )
    total_results: int = Field(..., description="Total number of results")

    model_config = {"extra": "allow"}
