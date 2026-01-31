"""
Feedback API endpoints.

Enables users to provide feedback on match quality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.core.database import get_db
from src.feedback.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
    FeedbackSummary,
)
from src.feedback.service import (
    create_feedback,
    get_feedback_stats,
    get_user_feedback,
)
from src.users.models import User

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit feedback on a match.

    Companies rate journalist matches, journalists rate company matches.
    Feedback helps improve match quality over time.
    """
    # Verify the profiles exist
    from src.companies.service import get_profile_by_id as get_company
    from src.journalists.service import get_profile_by_id as get_journalist

    journalist = get_journalist(db, feedback_data.journalist_profile_id)
    if not journalist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journalist profile not found",
        )

    company = get_company(db, feedback_data.company_profile_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    feedback = create_feedback(db, current_user.id, feedback_data)
    return feedback


@router.get("/me", response_model=FeedbackSummary)
def get_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get your feedback history and statistics.

    Shows all feedback you've submitted and success metrics.
    """
    stats = get_feedback_stats(db, user_id=current_user.id)
    recent = get_user_feedback(db, current_user.id, limit=10)

    return FeedbackSummary(
        user_id=current_user.id,
        stats=stats,
        recent_feedback=[FeedbackResponse.model_validate(f) for f in recent],
    )


@router.get("/stats", response_model=FeedbackStats)
def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get platform-wide feedback statistics.

    Shows overall match quality metrics.
    """
    from src.users.service import is_admin

    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for platform stats",
        )

    return get_feedback_stats(db)
