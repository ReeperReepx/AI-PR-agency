"""
Topic API endpoints.

Topics are publicly readable but only admins can create new ones.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.core.database import get_db
from src.topics.schemas import TopicCreate, TopicResponse
from src.topics.service import create_topic, get_topic_by_name, list_topics
from src.users.models import User
from src.users.service import is_admin

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=list[TopicResponse])
def get_topics(
    category: str | None = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List all topics in the taxonomy.

    Public endpoint - no authentication required.
    """
    return list_topics(db, category=category, skip=skip, limit=limit)


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_new_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new topic. Admin only.
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to create topics",
        )

    existing = get_topic_by_name(db, topic_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Topic '{topic_data.name}' already exists",
        )

    return create_topic(db, topic_data)
