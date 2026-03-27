"""
Configuration management using Pydantic settings.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(
        default="Digital Architect Platform - Core Logic Engine",
        description="Application name",
    )
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)

    # Database settings
    database_url: str = Field(
        default="postgresql://localhost:5432/digital_architect",
        description="Database connection URL",
    )

    # Pinecone settings
    pinecone_api_key: str = Field(default="", description="Pinecone API key")
    pinecone_environment: str = Field(
        default="", description="Pinecone environment"
    )
    pinecone_index_name: str = Field(
        default="digital-architect", description="Pinecone index name"
    )

    # CORS settings
    cors_origins: list[str] = Field(
        default=["*"], description="Allowed CORS origins"
    )

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )


settings = Settings()
