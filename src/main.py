"""
FastAPI application entry point.

Editorial PR Matchmaking Platform - Phase 1: Core platform & identity
"""

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.core.config import settings
from src.core.database import Base, engine
from src.users.router import router as users_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Journalist-first PR matchmaking platform. High-signal, trust-based editorial connections.",
    version="0.1.0",
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "phase": "1 - Core platform & identity"}
