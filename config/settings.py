from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.
    All configuration values must be loaded from this class.
    """

    APP_NAME: str = "ATOS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    SECRET_KEY: str = Field(default="CHANGE_ME")

    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/atos"
    )

    REDIS_URL: str = Field(
        default="redis://localhost:6379/0"
    )

    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()