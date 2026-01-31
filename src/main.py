"""
FastAPI application entry point.

Editorial PR Matchmaking Platform - Phase 4: Embedding-based discovery
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.companies.router import router as companies_router
from src.core.config import settings
from src.core.database import Base, SessionLocal, engine
from src.journalists.router import router as journalists_router
from src.matching.router import router as matching_router
from src.topics.router import router as topics_router
from src.topics.service import seed_topics
from src.users.router import router as users_router

# Import models to register them with SQLAlchemy
from src.companies.models import CompanyProfile  # noqa: F401
from src.embeddings.models import ProfileEmbedding  # noqa: F401
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
    version="0.4.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(topics_router)
app.include_router(journalists_router)
app.include_router(companies_router)
app.include_router(matching_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "phase": "4 - Embedding-based discovery"}
