"""
Application configuration using Pydantic Settings.
"""
from typing import List, Union, Literal
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

    # Database Environment Selection
    db_environment: Literal["local", "production"] = "local"

    # Local Database Configuration (used when db_environment="local")
    local_db_host: str = "localhost"
    local_db_port: int = 5432
    local_db_name: str = "convey"
    local_db_user: str = "postgres"
    local_db_password: str = "postgres"

    # Production Database Configuration (used when db_environment="production")
    production_database_url: str | None = None

    # Legacy database_url (for backward compatibility, will be deprecated)
    database_url: str | None = None

    # Database Connection Pool Settings
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    def get_database_url(self) -> str:
        """
        Get database URL based on environment.

        Returns:
            Constructed database URL for the selected environment

        Raises:
            ValueError: If production environment is selected without PRODUCTION_DATABASE_URL
        """
        if self.db_environment == "local":
            return (
                f"postgresql+asyncpg://{self.local_db_user}:{self.local_db_password}"
                f"@{self.local_db_host}:{self.local_db_port}/{self.local_db_name}"
            )
        elif self.db_environment == "production":
            if self.production_database_url:
                return self.production_database_url
            # Fallback to legacy database_url for backward compatibility
            if self.database_url:
                return self.database_url
            raise ValueError(
                "Production database URL not configured. "
                "Set PRODUCTION_DATABASE_URL in environment."
            )
        else:
            raise ValueError(f"Invalid db_environment: {self.db_environment}")

    @property
    def is_local_db(self) -> bool:
        """Check if using local database."""
        return self.db_environment == "local"

    @property
    def is_production_db(self) -> bool:
        """Check if using production database."""
        return self.db_environment == "production"

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
