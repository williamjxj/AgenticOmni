"""Global settings instance for AgenticOmni.

This module provides a singleton settings instance that is used throughout
the application. The settings are loaded once at module import time.

Usage:
    >>> from src.shared.config import settings
    >>> print(settings.database_url)
    >>> print(settings.api_port)
"""

from config.settings import Settings

from src.shared.exceptions import ConfigurationError


def load_settings() -> Settings:
    """Load and validate settings from environment variables.

    Returns:
        Settings: Validated settings instance

    Raises:
        ConfigurationError: If required settings are missing or invalid
    """
    try:
        return Settings()
    except ValueError as e:
        # Pydantic validation errors
        raise ConfigurationError(
            "Failed to load application settings. Check your environment variables.",
            details={"error": str(e)},
        ) from e
    except Exception as e:
        # Other configuration errors
        raise ConfigurationError(
            "Unexpected error while loading settings",
            details={"error": str(e), "type": type(e).__name__},
        ) from e


# Global settings instance
# This is loaded once when the module is imported
settings: Settings = load_settings()
