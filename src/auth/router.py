"""
Authentication API endpoints.

Handles registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.auth.service import authenticate_user, create_user_token
from src.core.database import get_db
from src.users.schemas import UserCreate, UserResponse
from src.users.service import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    - Email must be unique
    - Password is hashed before storage
    - Returns created user (without password)
    """
    try:
        user_data = UserCreate(
            email=request.email,
            password=request.password,
            user_type=request.user_type,
        )
        user = create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate and get an access token.

    - Returns JWT token on success
    - Token expires after configured time (default: 60 minutes)
    """
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_user_token(user)
    return TokenResponse(access_token=token)
