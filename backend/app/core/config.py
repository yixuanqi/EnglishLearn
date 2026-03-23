"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "English Trainer API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    database_url: str = "sqlite+aiosqlite:///./english_trainer.db"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "dev_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    openai_api_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    azure_speech_region: str = "eastus"
    stripe_secret_key: Optional[str] = None

    apple_shared_secret: Optional[str] = None
    google_package_name: str = "com.englishtrainer.app"
    google_service_account_json: Optional[str] = None

    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
