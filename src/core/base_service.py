"""
Generic base service for profile CRUD operations.

Reduces code duplication between companies and journalists services.
"""

from typing import TypeVar, Generic, Any
from sqlalchemy.orm import Session, selectinload

from src.core.exceptions import ProfileNotFoundError, ProfileExistsError
from src.topics.service import get_topics_by_ids

# Type variables for generic service
ModelT = TypeVar("ModelT")  # SQLAlchemy model type
CreateSchemaT = TypeVar("CreateSchemaT")  # Pydantic create schema
UpdateSchemaT = TypeVar("UpdateSchemaT")  # Pydantic update schema


class BaseProfileService(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Generic CRUD service for profile models.

    Handles common operations:
    - Get by ID / user ID
    - Create with topic association
    - Update with partial data
    - List with filters and pagination

    Subclasses should set:
    - model_class: The SQLAlchemy model
    - profile_type: String name for error messages ("company", "journalist")
    - filter_field: Field name for active/accepting filter
    """

    model_class: type[ModelT]
    profile_type: str
    filter_field: str | None = None  # e.g., "is_active" or "is_accepting_pitches"

    def get_by_id(self, db: Session, profile_id: str) -> ModelT | None:
        """Get a profile by its ID with topics eagerly loaded."""
        return (
            db.query(self.model_class)
            .options(selectinload(self.model_class.topics))
            .filter(self.model_class.id == profile_id)
            .first()
        )

    def get_by_user_id(self, db: Session, user_id: str) -> ModelT | None:
        """Get a profile by its owner's user ID with topics eagerly loaded."""
        return (
            db.query(self.model_class)
            .options(selectinload(self.model_class.topics))
            .filter(self.model_class.user_id == user_id)
            .first()
        )

    def get_by_id_or_raise(self, db: Session, profile_id: str) -> ModelT:
        """Get a profile by ID or raise ProfileNotFoundError."""
        profile = self.get_by_id(db, profile_id)
        if not profile:
            raise ProfileNotFoundError(self.profile_type, profile_id)
        return profile

    def get_by_user_id_or_raise(self, db: Session, user_id: str) -> ModelT:
        """Get a profile by user ID or raise ProfileNotFoundError."""
        profile = self.get_by_user_id(db, user_id)
        if not profile:
            raise ProfileNotFoundError(self.profile_type)
        return profile

    def create(
        self,
        db: Session,
        user_id: str,
        data: CreateSchemaT,
        extra_fields: dict[str, Any] | None = None,
    ) -> ModelT:
        """
        Create a new profile.

        Args:
            db: Database session
            user_id: Owner's user ID
            data: Pydantic schema with profile data
            extra_fields: Additional fields to set on the model

        Raises:
            ProfileExistsError: If user already has a profile
        """
        # Check for existing profile
        existing = self.get_by_user_id(db, user_id)
        if existing:
            raise ProfileExistsError(self.profile_type)

        # Get topics if provided
        data_dict = data.model_dump()
        topic_ids = data_dict.pop("topic_ids", [])
        topics = get_topics_by_ids(db, topic_ids) if topic_ids else []

        # Create profile
        profile = self.model_class(
            user_id=user_id,
            topics=topics,
            **data_dict,
            **(extra_fields or {}),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def update(self, db: Session, profile: ModelT, data: UpdateSchemaT) -> ModelT:
        """
        Update an existing profile with partial data.

        Only updates fields that are explicitly set in the schema.
        """
        update_dict = data.model_dump(exclude_unset=True)

        # Handle topics separately
        if "topic_ids" in update_dict:
            topic_ids = update_dict.pop("topic_ids")
            profile.topics = get_topics_by_ids(db, topic_ids)

        # Update other fields
        for field, value in update_dict.items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)
        return profile

    def list_all(
        self,
        db: Session,
        filter_active: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        """
        List profiles with optional filtering and pagination.

        Args:
            db: Database session
            filter_active: If True, only return active/accepting profiles
            skip: Number of records to skip
            limit: Maximum records to return
        """
        query = db.query(self.model_class).options(
            selectinload(self.model_class.topics)
        )

        if filter_active and self.filter_field:
            filter_attr = getattr(self.model_class, self.filter_field)
            query = query.filter(filter_attr.is_(True))

        return query.offset(skip).limit(limit).all()
