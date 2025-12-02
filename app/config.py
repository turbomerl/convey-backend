"""
Application configuration using Pydantic Settings.
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Keys
    openai_api_key: str
    google_api_key: str | None = None  # Optional for now since Gemini is a stub

    # CORS Configuration
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
    ]

    # File Upload Configuration
    max_upload_size: int = 25 * 1024 * 1024  # 25 MB in bytes

    # Default Provider
    default_provider: str = "openai"

    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/convey"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
