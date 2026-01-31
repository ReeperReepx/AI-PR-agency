"""
Application configuration.

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env")

    # Application
    app_name: str = "Editorial PR Matchmaking"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./editorial_pr.db"

    # Security (default key is 32+ bytes for HS256)
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
