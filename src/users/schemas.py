"""
Pydantic schemas for user data validation.

Separates input (Create), output (Response), and internal (InDB) representations.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.users.models import UserType


class UserCreate(BaseModel):
    """Schema for user registration input."""

    email: EmailStr
    password: str
    user_type: UserType


class UserResponse(BaseModel):
    """Schema for user data returned to clients. Never includes password."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    user_type: UserType
    is_active: bool
    created_at: datetime


class UserInDB(BaseModel):
    """Internal schema including password hash. Never returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    password_hash: str
    user_type: UserType
    is_active: bool
    created_at: datetime
    updated_at: datetime
