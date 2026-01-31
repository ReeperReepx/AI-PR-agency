"""
Topic service for CRUD operations and seeding.
"""

from sqlalchemy.orm import Session

from src.topics.models import Topic
from src.topics.schemas import TopicCreate


def get_topic_by_id(db: Session, topic_id: str) -> Topic | None:
    """Get a topic by ID."""
    return db.query(Topic).filter(Topic.id == topic_id).first()


def get_topic_by_name(db: Session, name: str) -> Topic | None:
    """Get a topic by slug name."""
    return db.query(Topic).filter(Topic.name == name).first()


def list_topics(
    db: Session, category: str | None = None, skip: int = 0, limit: int = 100
) -> list[Topic]:
    """List topics, optionally filtered by category."""
    query = db.query(Topic)
    if category:
        query = query.filter(Topic.category == category)
    return query.order_by(Topic.category, Topic.display_name).offset(skip).limit(limit).all()


def create_topic(db: Session, topic_data: TopicCreate) -> Topic:
    """Create a new topic."""
    topic = Topic(
        name=topic_data.name,
        display_name=topic_data.display_name,
        category=topic_data.category,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def get_topics_by_ids(db: Session, topic_ids: list[str]) -> list[Topic]:
    """Get multiple topics by their IDs."""
    if not topic_ids:
        return []
    return db.query(Topic).filter(Topic.id.in_(topic_ids)).all()


# Seed data for initial taxonomy
SEED_TOPICS = [
    # Technology
    ("artificial-intelligence", "Artificial Intelligence", "technology"),
    ("machine-learning", "Machine Learning", "technology"),
    ("cybersecurity", "Cybersecurity", "technology"),
    ("cloud-computing", "Cloud Computing", "technology"),
    ("blockchain", "Blockchain", "technology"),
    ("software-development", "Software Development", "technology"),
    ("data-privacy", "Data Privacy", "technology"),
    # Business
    ("startups", "Startups", "business"),
    ("venture-capital", "Venture Capital", "business"),
    ("mergers-acquisitions", "Mergers & Acquisitions", "business"),
    ("leadership", "Leadership", "business"),
    ("remote-work", "Remote Work", "business"),
    ("fintech", "Fintech", "business"),
    ("ecommerce", "E-commerce", "business"),
    # Healthcare
    ("digital-health", "Digital Health", "healthcare"),
    ("biotech", "Biotech", "healthcare"),
    ("pharmaceuticals", "Pharmaceuticals", "healthcare"),
    ("mental-health", "Mental Health", "healthcare"),
    ("healthcare-policy", "Healthcare Policy", "healthcare"),
    # Energy & Environment
    ("climate-tech", "Climate Tech", "energy"),
    ("renewable-energy", "Renewable Energy", "energy"),
    ("sustainability", "Sustainability", "energy"),
    ("electric-vehicles", "Electric Vehicles", "energy"),
    # Media & Entertainment
    ("streaming", "Streaming", "media"),
    ("gaming", "Gaming", "media"),
    ("social-media", "Social Media", "media"),
    ("creator-economy", "Creator Economy", "media"),
]


def seed_topics(db: Session) -> int:
    """
    Seed the database with initial topics.
    Returns the number of topics created.
    """
    created = 0
    for name, display_name, category in SEED_TOPICS:
        existing = get_topic_by_name(db, name)
        if not existing:
            topic = Topic(name=name, display_name=display_name, category=category)
            db.add(topic)
            created += 1
    db.commit()
    return created
