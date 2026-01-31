"""
Analytics API endpoints.

Provides platform metrics and user engagement data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.analytics.schemas import PlatformMetrics, UserMetrics
from src.analytics.service import get_platform_metrics, get_user_metrics
from src.auth.service import get_current_user
from src.core.database import get_db
from src.users.models import User
from src.users.service import is_admin

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/me", response_model=UserMetrics)
def get_my_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get your engagement metrics.

    Shows profile status, match counts, and activity.
    """
    return get_user_metrics(db, current_user)


@router.get("/platform", response_model=PlatformMetrics)
def get_platform_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get platform-wide analytics.

    Admin only. Shows user counts, match quality, and engagement.
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return get_platform_metrics(db)
