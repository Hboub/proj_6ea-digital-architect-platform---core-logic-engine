"""
Pydantic models for database entities with validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EntityBase(BaseModel):
    """Base model for Entity with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    description: Optional[str] = Field(
        None, max_length=2000, description="Entity description"
    )
    vision: Optional[str] = Field(
        None, max_length=2000, description="Entity vision statement"
    )
    industry: str = Field(
        ..., min_length=1, max_length=100, description="Industry classification"
    )
    maturity_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Maturity score (0-10)"
    )
    owner_id: Optional[str] = Field(None, description="Owner user ID")


class EntityCreate(EntityBase):
    """Model for creating a new Entity."""

    pass


class EntityUpdate(BaseModel):
    """Model for updating an Entity."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Entity name"
    )
    description: Optional[str] = Field(None, max_length=2000)
    vision: Optional[str] = Field(None, max_length=2000)
    industry: Optional[str] = Field(None, min_length=1, max_length=100)
    maturity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    owner_id: Optional[str] = None


class Entity(EntityBase):
    """Complete Entity model with database fields."""

    id: str = Field(..., description="Unique entity identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class RoadmapBase(BaseModel):
    """Base model for Roadmap with common fields."""

    title: str = Field(..., min_length=1, max_length=255, description="Roadmap title")
    description: Optional[str] = Field(
        None, max_length=2000, description="Roadmap description"
    )
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    status: str = Field(
        default="draft",
        description="Roadmap status (draft, active, completed, cancelled)",
    )
    priority: str = Field(
        default="medium", description="Priority level (low, medium, high, critical)"
    )
    estimated_duration: Optional[int] = Field(
        None, ge=1, description="Estimated duration in days"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate roadmap status."""
        allowed_statuses = ["draft", "active", "completed", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate roadmap priority."""
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of {allowed_priorities}")
        return v


class RoadmapCreate(RoadmapBase):
    """Model for creating a new Roadmap."""

    pass


class RoadmapUpdate(BaseModel):
    """Model for updating a Roadmap."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=1)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate roadmap status."""
        if v is not None:
            allowed_statuses = ["draft", "active", "completed", "cancelled"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate roadmap priority."""
        if v is not None:
            allowed_priorities = ["low", "medium", "high", "critical"]
            if v not in allowed_priorities:
                raise ValueError(f"Priority must be one of {allowed_priorities}")
        return v


class Roadmap(RoadmapBase):
    """Complete Roadmap model with database fields."""

    id: str = Field(..., description="Unique roadmap identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class MilestoneBase(BaseModel):
    """Base model for Milestone with common fields."""

    roadmap_id: str = Field(..., description="Associated roadmap ID")
    title: str = Field(
        ..., min_length=1, max_length=255, description="Milestone title"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Milestone description"
    )
    status: str = Field(
        default="pending",
        description="Milestone status (pending, in_progress, completed, blocked)",
    )
    order: int = Field(..., ge=1, description="Order position in roadmap")
    due_date: Optional[datetime] = Field(None, description="Due date for milestone")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    deliverables: Optional[str] = Field(None, max_length=1000)
    success_criteria: Optional[str] = Field(None, max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate milestone status."""
        allowed_statuses = ["pending", "in_progress", "completed", "blocked"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class MilestoneCreate(MilestoneBase):
    """Model for creating a new Milestone."""

    pass


class MilestoneUpdate(BaseModel):
    """Model for updating a Milestone."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deliverables: Optional[str] = Field(None, max_length=1000)
    success_criteria: Optional[str] = Field(None, max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate milestone status."""
        if v is not None:
            allowed_statuses = ["pending", "in_progress", "completed", "blocked"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class Milestone(MilestoneBase):
    """Complete Milestone model with database fields."""

    id: str = Field(..., description="Unique milestone identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class EntityRelationshipBase(BaseModel):
    """Base model for EntityRelationship with common fields."""

    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(
        ..., min_length=1, max_length=100, description="Type of relationship"
    )
    strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Relationship strength (0.0-1.0)",
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Relationship description"
    )
    metadata: Optional[str] = Field(
        None, max_length=2000, description="Additional metadata (JSON)"
    )


class EntityRelationshipCreate(EntityRelationshipBase):
    """Model for creating a new EntityRelationship."""

    pass


class EntityRelationshipUpdate(BaseModel):
    """Model for updating an EntityRelationship."""

    relationship_type: Optional[str] = Field(None, min_length=1, max_length=100)
    strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[str] = Field(None, max_length=2000)


class EntityRelationship(EntityRelationshipBase):
    """Complete EntityRelationship model with database fields."""

    id: str = Field(..., description="Unique relationship identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
