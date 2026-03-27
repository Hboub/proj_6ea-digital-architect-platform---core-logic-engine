"""
Database seed script for development and testing data.

Creates sample entities, roadmaps, and milestones with diverse industry types
and maturity levels for comprehensive testing.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from prisma import Prisma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_entities(db: Prisma) -> dict[str, str]:
    """
    Seed sample entities across various industries.

    Args:
        db: Prisma client instance

    Returns:
        dict[str, str]: Mapping of entity names to their IDs
    """
    logger.info("Seeding entities...")

    entities_data = [
        {
            "name": "TechCorp Solutions",
            "description": "Enterprise software development company specializing in cloud solutions",
            "vision": "To revolutionize enterprise software with AI-powered solutions",
            "industry": "Technology",
            "maturity_score": 7.5,
            "owner_id": "owner-tech-001",
        },
        {
            "name": "FinServe Banking",
            "description": "Digital banking platform for modern financial services",
            "vision": "Making banking accessible and transparent for everyone",
            "industry": "Finance",
            "maturity_score": 6.2,
            "owner_id": "owner-fin-001",
        },
        {
            "name": "HealthTech Innovators",
            "description": "Healthcare technology company focused on telemedicine",
            "vision": "Bringing quality healthcare to remote locations",
            "industry": "Healthcare",
            "maturity_score": 5.8,
            "owner_id": "owner-health-001",
        },
        {
            "name": "RetailNext",
            "description": "E-commerce platform for next-generation retail",
            "vision": "Creating seamless online shopping experiences",
            "industry": "Retail",
            "maturity_score": 6.9,
            "owner_id": "owner-retail-001",
        },
        {
            "name": "EduLearn Platform",
            "description": "Online education and learning management system",
            "vision": "Democratizing education through technology",
            "industry": "Education",
            "maturity_score": 4.5,
            "owner_id": "owner-edu-001",
        },
        {
            "name": "GreenEnergy Systems",
            "description": "Renewable energy solutions and smart grid technology",
            "vision": "Powering the world with sustainable energy",
            "industry": "Energy",
            "maturity_score": 5.2,
            "owner_id": "owner-energy-001",
        },
        {
            "name": "LogiTrans Global",
            "description": "Supply chain and logistics optimization platform",
            "vision": "Revolutionizing global supply chain management",
            "industry": "Logistics",
            "maturity_score": 6.7,
            "owner_id": "owner-logistics-001",
        },
        {
            "name": "MediaStream Pro",
            "description": "Content delivery and streaming platform",
            "vision": "Delivering premium content to audiences worldwide",
            "industry": "Media",
            "maturity_score": 7.1,
            "owner_id": "owner-media-001",
        },
    ]

    entity_ids = {}

    for entity_data in entities_data:
        entity = await db.entity.create(data=entity_data)
        entity_ids[entity_data["name"]] = entity.id
        logger.info(f"Created entity: {entity_data['name']}")

    logger.info(f"Created {len(entity_ids)} entities")
    return entity_ids


async def seed_roadmaps(db: Prisma, entity_ids: dict[str, str]) -> dict[str, str]:
    """
    Seed sample roadmaps connecting entities.

    Args:
        db: Prisma client instance
        entity_ids: Mapping of entity names to their IDs

    Returns:
        dict[str, str]: Mapping of roadmap titles to their IDs
    """
    logger.info("Seeding roadmaps...")

    roadmaps_data = [
        {
            "title": "Cloud Migration Initiative",
            "description": "Migrate legacy systems to cloud infrastructure",
            "source_entity_id": entity_ids["TechCorp Solutions"],
            "target_entity_id": entity_ids["TechCorp Solutions"],
            "status": "active",
            "priority": "high",
            "estimated_duration": 180,
        },
        {
            "title": "Digital Banking Transformation",
            "description": "Transform traditional banking to digital-first approach",
            "source_entity_id": entity_ids["FinServe Banking"],
            "target_entity_id": entity_ids["FinServe Banking"],
            "status": "active",
            "priority": "critical",
            "estimated_duration": 365,
        },
        {
            "title": "Telemedicine Platform Launch",
            "description": "Launch telemedicine capabilities for remote consultations",
            "source_entity_id": entity_ids["HealthTech Innovators"],
            "target_entity_id": entity_ids["HealthTech Innovators"],
            "status": "active",
            "priority": "high",
            "estimated_duration": 120,
        },
        {
            "title": "E-commerce Modernization",
            "description": "Modernize e-commerce platform with AI recommendations",
            "source_entity_id": entity_ids["RetailNext"],
            "target_entity_id": entity_ids["RetailNext"],
            "status": "draft",
            "priority": "medium",
            "estimated_duration": 90,
        },
        {
            "title": "Learning Platform Scale-up",
            "description": "Scale online learning platform to support 1M users",
            "source_entity_id": entity_ids["EduLearn Platform"],
            "target_entity_id": entity_ids["EduLearn Platform"],
            "status": "active",
            "priority": "high",
            "estimated_duration": 150,
        },
    ]

    roadmap_ids = {}

    for roadmap_data in roadmaps_data:
        roadmap = await db.roadmap.create(data=roadmap_data)
        roadmap_ids[roadmap_data["title"]] = roadmap.id
        logger.info(f"Created roadmap: {roadmap_data['title']}")

    logger.info(f"Created {len(roadmap_ids)} roadmaps")
    return roadmap_ids


async def seed_milestones(db: Prisma, roadmap_ids: dict[str, str]) -> int:
    """
    Seed sample milestones for roadmaps.

    Args:
        db: Prisma client instance
        roadmap_ids: Mapping of roadmap titles to their IDs

    Returns:
        int: Number of milestones created
    """
    logger.info("Seeding milestones...")

    now = datetime.now()
    milestones_data = [
        # Cloud Migration Initiative milestones
        {
            "roadmap_id": roadmap_ids["Cloud Migration Initiative"],
            "title": "Infrastructure Assessment",
            "description": "Assess current infrastructure and cloud readiness",
            "status": "completed",
            "order": 1,
            "due_date": now - timedelta(days=30),
            "completed_at": now - timedelta(days=35),
            "deliverables": "Infrastructure assessment report",
            "success_criteria": "Complete audit of all systems",
        },
        {
            "roadmap_id": roadmap_ids["Cloud Migration Initiative"],
            "title": "Cloud Architecture Design",
            "description": "Design cloud architecture and migration strategy",
            "status": "in_progress",
            "order": 2,
            "due_date": now + timedelta(days=15),
            "deliverables": "Architecture diagrams and migration plan",
            "success_criteria": "Approved architecture design",
        },
        {
            "roadmap_id": roadmap_ids["Cloud Migration Initiative"],
            "title": "Pilot Migration",
            "description": "Migrate non-critical systems as pilot",
            "status": "pending",
            "order": 3,
            "due_date": now + timedelta(days=60),
            "deliverables": "Migrated pilot systems",
            "success_criteria": "Zero downtime migration",
        },
        # Digital Banking Transformation milestones
        {
            "roadmap_id": roadmap_ids["Digital Banking Transformation"],
            "title": "Mobile App Development",
            "description": "Develop mobile banking application",
            "status": "in_progress",
            "order": 1,
            "due_date": now + timedelta(days=90),
            "deliverables": "iOS and Android apps",
            "success_criteria": "App store approval",
        },
        {
            "roadmap_id": roadmap_ids["Digital Banking Transformation"],
            "title": "API Integration",
            "description": "Integrate with core banking APIs",
            "status": "pending",
            "order": 2,
            "due_date": now + timedelta(days=120),
            "deliverables": "API integration layer",
            "success_criteria": "100% API coverage",
        },
        {
            "roadmap_id": roadmap_ids["Digital Banking Transformation"],
            "title": "Security Audit",
            "description": "Conduct comprehensive security audit",
            "status": "pending",
            "order": 3,
            "due_date": now + timedelta(days=150),
            "deliverables": "Security audit report",
            "success_criteria": "Pass all security requirements",
        },
        # Telemedicine Platform Launch milestones
        {
            "roadmap_id": roadmap_ids["Telemedicine Platform Launch"],
            "title": "Video Consultation Feature",
            "description": "Implement secure video consultation system",
            "status": "in_progress",
            "order": 1,
            "due_date": now + timedelta(days=30),
            "deliverables": "Video consultation platform",
            "success_criteria": "HD video quality with encryption",
        },
        {
            "roadmap_id": roadmap_ids["Telemedicine Platform Launch"],
            "title": "Doctor Onboarding",
            "description": "Onboard healthcare providers to platform",
            "status": "pending",
            "order": 2,
            "due_date": now + timedelta(days=60),
            "deliverables": "100 doctors onboarded",
            "success_criteria": "Verified credentials for all",
        },
    ]

    milestone_count = 0

    for milestone_data in milestones_data:
        await db.milestone.create(data=milestone_data)
        milestone_count += 1
        logger.info(f"Created milestone: {milestone_data['title']}")

    logger.info(f"Created {milestone_count} milestones")
    return milestone_count


async def seed_relationships(
    db: Prisma, entity_ids: dict[str, str]
) -> int:
    """
    Seed entity relationships.

    Args:
        db: Prisma client instance
        entity_ids: Mapping of entity names to their IDs

    Returns:
        int: Number of relationships created
    """
    logger.info("Seeding entity relationships...")

    relationships_data = [
        {
            "source_entity_id": entity_ids["TechCorp Solutions"],
            "target_entity_id": entity_ids["FinServe Banking"],
            "relationship_type": "partnership",
            "strength": 0.8,
            "description": "Technology partnership for banking solutions",
            "metadata": '{"partnership_type": "technology", "start_date": "2024-01-01"}',
        },
        {
            "source_entity_id": entity_ids["HealthTech Innovators"],
            "target_entity_id": entity_ids["TechCorp Solutions"],
            "relationship_type": "vendor",
            "strength": 0.7,
            "description": "Cloud infrastructure vendor relationship",
            "metadata": '{"contract_type": "infrastructure", "annual_value": 500000}',
        },
        {
            "source_entity_id": entity_ids["RetailNext"],
            "target_entity_id": entity_ids["LogiTrans Global"],
            "relationship_type": "supplier",
            "strength": 0.9,
            "description": "Logistics and supply chain partner",
            "metadata": '{"service_type": "logistics", "coverage": "global"}',
        },
        {
            "source_entity_id": entity_ids["EduLearn Platform"],
            "target_entity_id": entity_ids["MediaStream Pro"],
            "relationship_type": "content_provider",
            "strength": 0.6,
            "description": "Educational content streaming partnership",
            "metadata": '{"content_type": "educational", "duration": "12_months"}',
        },
        {
            "source_entity_id": entity_ids["GreenEnergy Systems"],
            "target_entity_id": entity_ids["TechCorp Solutions"],
            "relationship_type": "client",
            "strength": 0.75,
            "description": "Software development client",
            "metadata": '{"project_type": "smart_grid", "value": 750000}',
        },
    ]

    relationship_count = 0

    for rel_data in relationships_data:
        await db.entityrelationship.create(data=rel_data)
        relationship_count += 1
        logger.info(
            f"Created relationship: {rel_data['relationship_type']} between entities"
        )

    logger.info(f"Created {relationship_count} relationships")
    return relationship_count


async def main() -> None:
    """
    Main seeding function that orchestrates the entire seeding process.
    """
    logger.info("Starting database seeding process...")

    db = Prisma()

    try:
        logger.info("Connecting to database...")
        await db.connect()
        logger.info("Database connected successfully")

        # Seed entities first
        entity_ids = await seed_entities(db)

        # Seed roadmaps
        roadmap_ids = await seed_roadmaps(db, entity_ids)

        # Seed milestones
        milestone_count = await seed_milestones(db, roadmap_ids)

        # Seed relationships
        relationship_count = await seed_relationships(db, entity_ids)

        logger.info("=" * 50)
        logger.info("Database seeding completed successfully!")
        logger.info(f"Entities created: {len(entity_ids)}")
        logger.info(f"Roadmaps created: {len(roadmap_ids)}")
        logger.info(f"Milestones created: {milestone_count}")
        logger.info(f"Relationships created: {relationship_count}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error during seeding: {e}", exc_info=True)
        raise

    finally:
        logger.info("Disconnecting from database...")
        await db.disconnect()
        logger.info("Database disconnected")


if __name__ == "__main__":
    asyncio.run(main())
