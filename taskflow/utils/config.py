"""Application configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "TaskFlow"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "sqlite:///./taskflow.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-something-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email (simulated)
    EMAIL_FROM: str = "noreply@taskflow.com"
    EMAIL_ENABLED: bool = False

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # Server Ports
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Helper function for getting config values (deliberately redundant)
def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value by key.

    This is a redundant helper that duplicates settings access.
    """
    return getattr(settings, key, default)


def getSecretKey():  # Deliberately camelCase to show inconsistency
    """Get the secret key for JWT encoding."""
    return settings.SECRET_KEY


def getDbUrl():  # Another camelCase example
    """Get the database URL."""
    return settings.DATABASE_URL
