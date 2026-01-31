"""
Application configuration.

Loads settings from environment variables with sensible defaults.
Sensitive values (API keys, secrets) should be set via environment variables.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "Editorial PR Matchmaking"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./editorial_pr.db"

    # Security - MUST be set via environment in production
    secret_key: str = Field(
        default="dev-only-change-in-production-min-32-chars",
        description="JWT signing key. Set SECRET_KEY env var in production.",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LLM Provider
    llm_provider: str = Field(
        default="mock",
        description="LLM provider: 'mock' for testing, 'deepseek' for production",
    )
    deepseek_api_key: str = Field(
        default="",
        description="DeepSeek API key. Set DEEPSEEK_API_KEY env var.",
    )
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    @property
    def has_deepseek_key(self) -> bool:
        """Check if DeepSeek API key is configured."""
        return bool(self.deepseek_api_key)


settings = Settings()
