"""
User service layer.

Handles user business logic: creation, retrieval, validation.
Does NOT handle authentication (that's auth/service.py).
"""

from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.users.models import User, UserType
from src.users.schemas import UserCreate


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Retrieve a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """List all users with pagination. Admin use only."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user.

    Raises ValueError if email already exists.
    """
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise ValueError("Email already registered")

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        user_type=user_data.user_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def is_admin(user: User) -> bool:
    """Check if a user has admin privileges."""
    return user.user_type == UserType.admin
