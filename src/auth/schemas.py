"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, EmailStr

from src.users.models import UserType


class LoginRequest(BaseModel):
    """Schema for login input."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response after successful login."""

    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    """Schema for registration input."""

    email: EmailStr
    password: str
    user_type: UserType
