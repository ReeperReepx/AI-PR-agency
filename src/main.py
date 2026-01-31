"""
FastAPI application entry point.

Editorial PR Matchmaking Platform - Phase 6: Continuous refinement
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.analytics.router import router as analytics_router
from src.auth.router import router as auth_router
from src.companies.router import router as companies_router
from src.core.config import settings
from src.core.database import Base, SessionLocal, engine
from src.feedback.router import router as feedback_router
from src.frontend.router import router as frontend_router
from src.journalists.router import router as journalists_router
from src.matching.router import router as matching_router
from src.topics.router import router as topics_router
from src.topics.service import seed_topics
from src.users.router import router as users_router

# Frontend static files directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Import models to register them with SQLAlchemy
from src.companies.models import CompanyProfile  # noqa: F401
from src.embeddings.models import ProfileEmbedding  # noqa: F401
from src.feedback.models import MatchFeedback  # noqa: F401
from src.journalists.models import JournalistProfile  # noqa: F401
from src.topics.models import Topic  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup: create tables and seed topics
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = seed_topics(db)
        if created > 0:
            print(f"Seeded {created} topics")
    finally:
        db.close()
    yield
    # Shutdown: nothing needed


app = FastAPI(
    title=settings.app_name,
    description="Journalist-first PR matchmaking platform. High-signal, trust-based editorial connections.",
    version="0.7.0",
    lifespan=lifespan,
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

# Include API routers (backwards compatible, no prefix)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(topics_router)
app.include_router(journalists_router)
app.include_router(companies_router)
app.include_router(matching_router)
app.include_router(feedback_router)
app.include_router(analytics_router)

# Include frontend router (no prefix, serves HTML pages)
app.include_router(frontend_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "phase": "6 - Continuous refinement"}
