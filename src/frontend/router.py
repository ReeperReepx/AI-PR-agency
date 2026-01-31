"""
Frontend routes for serving HTML templates.

Uses Jinja2 for template rendering with the Measured UI-inspired styling.
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Get the frontend templates directory
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect to dashboard or login."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard with progress tracking and analytics."""
    # Sample stats for template rendering
    stats = {
        "total_matches": 47,
        "outreach_sent": 23,
        "response_rate": 34,
        "avg_score": 85,
    }

    # Sample recent matches
    recent_matches = []

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "stats": stats,
            "recent_matches": recent_matches,
        },
    )


@router.get("/matches", response_class=HTMLResponse)
async def matches_page(request: Request):
    """Matches discovery page."""
    return templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "active_page": "matches",
        },
    )


@router.get("/journalists", response_class=HTMLResponse)
async def journalists_page(request: Request):
    """Journalists listing page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "journalists",
            "stats": {"total_matches": 0, "outreach_sent": 0, "response_rate": 0, "avg_score": 0},
            "recent_matches": [],
        },
    )


@router.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    """Companies listing page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "companies",
            "stats": {"total_matches": 0, "outreach_sent": 0, "response_rate": 0, "avg_score": 0},
            "recent_matches": [],
        },
    )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "analytics",
            "stats": {"total_matches": 0, "outreach_sent": 0, "response_rate": 0, "avg_score": 0},
            "recent_matches": [],
        },
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "profile",
            "stats": {"total_matches": 0, "outreach_sent": 0, "response_rate": 0, "avg_score": 0},
            "recent_matches": [],
        },
    )
