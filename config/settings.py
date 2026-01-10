"""Application settings using Pydantic BaseSettings.

This module defines the Settings class that loads and validates environment variables.
All configuration should be accessed through the settings instance in src.shared.config.
"""

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: str | list[str] | None) -> list[str]:
    """Parse CORS origins from comma-separated string or list."""
    if v is None or v == "":
        return ["http://localhost:3000"]
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    return v


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings are loaded from environment variables or .env file.
    Required settings will raise validation errors if missing.
    Optional settings have sensible defaults.

    Example:
        >>> from config.settings import Settings
        >>> settings = Settings()
        >>> print(settings.database_url)
        postgresql+asyncpg://user:pass@localhost/db
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # ========================================================================
    # Database Configuration
    # ========================================================================
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL with asyncpg driver",
        examples=["postgresql+asyncpg://user:pass@localhost:5436/agenticomni"],
    )

    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Database connection pool size",
    )

    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size",
    )

    # ========================================================================
    # Vector Store Configuration
    # ========================================================================
    vector_dimensions: int = Field(
        default=1536,
        ge=384,
        le=4096,
        description="Embedding vector dimensions (must match embedding model)",
    )

    # ========================================================================
    # API Server Configuration
    # ========================================================================
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host address",
    )

    api_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port",
    )

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
    )

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return parse_cors(self.cors_origins)

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}, got {v}")
        return v_upper

    log_format: str = Field(
        default="json",
        description="Log format: json or console",
    )

    # ========================================================================
    # Security Configuration
    # ========================================================================
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT tokens, session encryption, etc.",
    )

    enforce_tenant_isolation: bool = Field(
        default=True,
        description="Enforce row-level tenant isolation in database queries",
    )

    # ========================================================================
    # Optional: LLM API Keys
    # ========================================================================
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for embeddings and chat completion",
    )

    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude models",
    )

    # ========================================================================
    # Redis Configuration
    # ========================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    redis_max_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum Redis connections in pool",
    )

    # ========================================================================
    # Application Configuration
    # ========================================================================
    environment: str = Field(
        default="development",
        description="Application environment: development, staging, production",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode (detailed errors, auto-reload)",
    )

    api_version: str = Field(
        default="v1",
        description="API version prefix",
    )

    # ========================================================================
    # File Storage Configuration
    # ========================================================================
    upload_dir: str = Field(
        default="./uploads",
        description="Directory for uploaded files (local storage)",
    )

    max_upload_size_mb: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum file upload size in MB",
    )

    allowed_file_types: str = Field(
        default="pdf,docx,pptx,txt",
        description="Allowed file types for upload (comma-separated)",
    )

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: str | list[str] | None) -> str:
        """Parse allowed file types from list or comma-separated string."""
        if v is None or v == "":
            return "pdf,docx,pptx,txt"
        if isinstance(v, list):
            return ",".join(v)
        return v

    def get_allowed_file_types_list(self) -> list[str]:
        """Get allowed file types as a list."""
        return [ft.strip() for ft in self.allowed_file_types.split(",") if ft.strip()]

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_file_types(cls, v: str | list[str]) -> list[str]:
        """Parse allowed file types from comma-separated string or list."""
        if isinstance(v, str):
            return [ft.strip().lower() for ft in v.split(",") if ft.strip()]
        return [ft.lower() for ft in v]

    # ========================================================================
    # Property Methods
    # ========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024
