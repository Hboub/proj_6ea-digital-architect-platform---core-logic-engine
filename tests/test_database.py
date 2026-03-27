"""
Database connection and model tests.

Tests database connection, Prisma client initialization, model validation,
basic CRUD operations, and owner-based filtering.
"""

import pytest
from prisma import Prisma
from pydantic import ValidationError

from src.database.client import connect_db, disconnect_db, get_db_client, is_connected
from src.database.models import (
    Entity,
    EntityCreate,
    EntityRelationship,
    EntityRelationshipCreate,
    EntityUpdate,
    Milestone,
    MilestoneCreate,
    MilestoneUpdate,
    Roadmap,
    RoadmapCreate,
    RoadmapUpdate,
)


class TestDatabaseConnection:
    """Test database connection functionality."""

    @pytest.mark.asyncio
    async def test_connect_disconnect(self) -> None:
        """Test database connection and disconnection."""
        await connect_db()
        assert await is_connected() is True

        await disconnect_db()
        assert await is_connected() is False

    @pytest.mark.asyncio
    async def test_get_client_before_connect(self) -> None:
        """Test getting client before connection raises error."""
        await disconnect_db()

        with pytest.raises(RuntimeError, match="not initialized"):
            get_db_client()

    @pytest.mark.asyncio
    async def test_get_client_after_connect(self) -> None:
        """Test getting client after connection succeeds."""
        await connect_db()
        client = get_db_client()
        assert isinstance(client, Prisma)

        await disconnect_db()

    @pytest.mark.asyncio
    async def test_multiple_connects(self) -> None:
        """Test multiple connect calls are handled gracefully."""
        await connect_db()
        await connect_db()

        assert await is_connected() is True

        await disconnect_db()


class TestEntityModel:
    """Test Entity Pydantic model validation."""

    def test_entity_create_valid(self) -> None:
        """Test creating valid Entity."""
        entity = EntityCreate(
            name="Test Company",
            description="A test company",
            vision="To be the best",
            industry="Technology",
            maturity_score=7.5,
            owner_id="owner-123",
        )

        assert entity.name == "Test Company"
        assert entity.industry == "Technology"
        assert entity.maturity_score == 7.5

    def test_entity_create_minimal(self) -> None:
        """Test creating Entity with minimal fields."""
        entity = EntityCreate(name="Minimal Corp", industry="Finance")

        assert entity.name == "Minimal Corp"
        assert entity.industry == "Finance"
        assert entity.maturity_score == 0.0
        assert entity.description is None

    def test_entity_name_validation(self) -> None:
        """Test Entity name validation."""
        with pytest.raises(ValidationError):
            EntityCreate(name="", industry="Technology")

    def test_entity_maturity_score_range(self) -> None:
        """Test Entity maturity score range validation."""
        with pytest.raises(ValidationError):
            EntityCreate(name="Test", industry="Tech", maturity_score=-1.0)

        with pytest.raises(ValidationError):
            EntityCreate(name="Test", industry="Tech", maturity_score=11.0)

        entity = EntityCreate(name="Test", industry="Tech", maturity_score=5.0)
        assert entity.maturity_score == 5.0

    def test_entity_update_partial(self) -> None:
        """Test Entity partial update."""
        update = EntityUpdate(name="Updated Name", maturity_score=8.0)

        assert update.name == "Updated Name"
        assert update.maturity_score == 8.0
        assert update.industry is None


class TestRoadmapModel:
    """Test Roadmap Pydantic model validation."""

    def test_roadmap_create_valid(self) -> None:
        """Test creating valid Roadmap."""
        roadmap = RoadmapCreate(
            title="Digital Transformation",
            description="Transform to digital",
            source_entity_id="entity-1",
            target_entity_id="entity-2",
            status="active",
            priority="high",
            estimated_duration=180,
        )

        assert roadmap.title == "Digital Transformation"
        assert roadmap.status == "active"
        assert roadmap.priority == "high"

    def test_roadmap_status_validation(self) -> None:
        """Test Roadmap status validation."""
        with pytest.raises(ValidationError, match="Status must be one of"):
            RoadmapCreate(
                title="Test",
                source_entity_id="1",
                target_entity_id="2",
                status="invalid",
            )

        roadmap = RoadmapCreate(
            title="Test", source_entity_id="1", target_entity_id="2", status="draft"
        )
        assert roadmap.status == "draft"

    def test_roadmap_priority_validation(self) -> None:
        """Test Roadmap priority validation."""
        with pytest.raises(ValidationError, match="Priority must be one of"):
            RoadmapCreate(
                title="Test",
                source_entity_id="1",
                target_entity_id="2",
                priority="invalid",
            )

        roadmap = RoadmapCreate(
            title="Test", source_entity_id="1", target_entity_id="2", priority="medium"
        )
        assert roadmap.priority == "medium"

    def test_roadmap_default_values(self) -> None:
        """Test Roadmap default values."""
        roadmap = RoadmapCreate(
            title="Test", source_entity_id="1", target_entity_id="2"
        )

        assert roadmap.status == "draft"
        assert roadmap.priority == "medium"


class TestMilestoneModel:
    """Test Milestone Pydantic model validation."""

    def test_milestone_create_valid(self) -> None:
        """Test creating valid Milestone."""
        milestone = MilestoneCreate(
            roadmap_id="roadmap-1",
            title="Phase 1 Complete",
            description="Complete first phase",
            status="pending",
            order=1,
            deliverables="Technical spec",
            success_criteria="Approved by stakeholders",
        )

        assert milestone.title == "Phase 1 Complete"
        assert milestone.status == "pending"
        assert milestone.order == 1

    def test_milestone_status_validation(self) -> None:
        """Test Milestone status validation."""
        with pytest.raises(ValidationError, match="Status must be one of"):
            MilestoneCreate(
                roadmap_id="1", title="Test", status="invalid", order=1
            )

        milestone = MilestoneCreate(
            roadmap_id="1", title="Test", status="in_progress", order=1
        )
        assert milestone.status == "in_progress"

    def test_milestone_order_validation(self) -> None:
        """Test Milestone order validation."""
        with pytest.raises(ValidationError):
            MilestoneCreate(roadmap_id="1", title="Test", status="pending", order=0)

        milestone = MilestoneCreate(
            roadmap_id="1", title="Test", status="pending", order=1
        )
        assert milestone.order == 1


class TestEntityRelationshipModel:
    """Test EntityRelationship Pydantic model validation."""

    def test_relationship_create_valid(self) -> None:
        """Test creating valid EntityRelationship."""
        relationship = EntityRelationshipCreate(
            source_entity_id="entity-1",
            target_entity_id="entity-2",
            relationship_type="partnership",
            strength=0.8,
            description="Strategic partnership",
            metadata='{"type": "technology"}',
        )

        assert relationship.relationship_type == "partnership"
        assert relationship.strength == 0.8

    def test_relationship_strength_range(self) -> None:
        """Test EntityRelationship strength range validation."""
        with pytest.raises(ValidationError):
            EntityRelationshipCreate(
                source_entity_id="1",
                target_entity_id="2",
                relationship_type="partner",
                strength=-0.1,
            )

        with pytest.raises(ValidationError):
            EntityRelationshipCreate(
                source_entity_id="1",
                target_entity_id="2",
                relationship_type="partner",
                strength=1.5,
            )

        relationship = EntityRelationshipCreate(
            source_entity_id="1",
            target_entity_id="2",
            relationship_type="partner",
            strength=0.5,
        )
        assert relationship.strength == 0.5

    def test_relationship_default_strength(self) -> None:
        """Test EntityRelationship default strength."""
        relationship = EntityRelationshipCreate(
            source_entity_id="1", target_entity_id="2", relationship_type="client"
        )

        assert relationship.strength == 0.5


@pytest.mark.asyncio
class TestDatabaseCRUD:
    """Test basic CRUD operations against database."""

    async def test_entity_crud(self) -> None:
        """Test Entity CRUD operations."""
        await connect_db()
        db = get_db_client()

        try:
            entity = await db.entity.create(
                data={
                    "name": "Test Entity",
                    "description": "Test description",
                    "industry": "Technology",
                    "maturity_score": 5.0,
                    "owner_id": "test-owner",
                }
            )

            assert entity.id is not None
            assert entity.name == "Test Entity"
            assert entity.maturity_score == 5.0

            found = await db.entity.find_unique(where={"id": entity.id})
            assert found is not None
            assert found.name == "Test Entity"

            updated = await db.entity.update(
                where={"id": entity.id}, data={"maturity_score": 7.5}
            )
            assert updated.maturity_score == 7.5

            await db.entity.delete(where={"id": entity.id})

            deleted = await db.entity.find_unique(where={"id": entity.id})
            assert deleted is None

        finally:
            await disconnect_db()

    async def test_owner_based_filtering(self) -> None:
        """Test filtering entities by owner."""
        await connect_db()
        db = get_db_client()

        try:
            entity1 = await db.entity.create(
                data={
                    "name": "Owner 1 Entity",
                    "industry": "Tech",
                    "owner_id": "owner-1",
                }
            )

            entity2 = await db.entity.create(
                data={
                    "name": "Owner 2 Entity",
                    "industry": "Tech",
                    "owner_id": "owner-2",
                }
            )

            owner1_entities = await db.entity.find_many(
                where={"owner_id": "owner-1"}
            )
            assert len(owner1_entities) >= 1
            assert all(e.owner_id == "owner-1" for e in owner1_entities)

            owner2_entities = await db.entity.find_many(
                where={"owner_id": "owner-2"}
            )
            assert len(owner2_entities) >= 1
            assert all(e.owner_id == "owner-2" for e in owner2_entities)

            await db.entity.delete(where={"id": entity1.id})
            await db.entity.delete(where={"id": entity2.id})

        finally:
            await disconnect_db()

    async def test_roadmap_with_entities(self) -> None:
        """Test Roadmap creation with entity relationships."""
        await connect_db()
        db = get_db_client()

        try:
            entity = await db.entity.create(
                data={"name": "Test Entity", "industry": "Tech"}
            )

            roadmap = await db.roadmap.create(
                data={
                    "title": "Test Roadmap",
                    "source_entity_id": entity.id,
                    "target_entity_id": entity.id,
                    "status": "draft",
                    "priority": "medium",
                }
            )

            assert roadmap.id is not None
            assert roadmap.source_entity_id == entity.id

            fetched = await db.roadmap.find_unique(
                where={"id": roadmap.id}, include={"source_entity": True}
            )
            assert fetched is not None
            assert fetched.source_entity.name == "Test Entity"

            await db.roadmap.delete(where={"id": roadmap.id})
            await db.entity.delete(where={"id": entity.id})

        finally:
            await disconnect_db()
