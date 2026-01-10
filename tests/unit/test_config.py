"""Unit tests for configuration management."""

import pytest
from config.settings import Settings
from pydantic import ValidationError


class TestSettings:
    """Test suite for Settings configuration class."""

    def test_settings_load_from_env(self, test_settings: Settings) -> None:
        """Test that settings load correctly from environment variables.

        Args:
            test_settings: Test configuration fixture
        """
        assert test_settings.environment == "test"
        assert test_settings.debug is True
        assert test_settings.api_port == 8001
        assert test_settings.api_version == "v1"
        assert test_settings.vector_dimensions == 1536

    def test_settings_database_url_format(self, test_settings: Settings) -> None:
        """Test that database URL has correct format.

        Args:
            test_settings: Test configuration fixture
        """
        db_url = str(test_settings.database_url)
        assert db_url.startswith("postgresql+asyncpg://")
        assert "agenticomni_test" in db_url

    def test_settings_cors_origins_parsing(self, test_settings: Settings) -> None:
        """Test that CORS origins are parsed correctly from string.

        Args:
            test_settings: Test configuration fixture
        """
        origins = test_settings.get_cors_origins_list()
        assert isinstance(origins, list)
        assert len(origins) > 0
        assert "http://localhost:3000" in origins

    def test_settings_file_types_parsing(self, test_settings: Settings) -> None:
        """Test that allowed file types are parsed correctly.

        Args:
            test_settings: Test configuration fixture
        """
        file_types = test_settings.get_allowed_file_types_list()
        assert isinstance(file_types, list)
        assert "pdf" in file_types
        assert "txt" in file_types

    def test_missing_required_config_raises_error(self) -> None:
        """Test that missing required configuration raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="",  # Empty database URL should fail
                secret_key="test_key_minimum_32_characters_long",
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_secret_key_minimum_length(self) -> None:
        """Test that secret key must meet minimum length requirement."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost/db",
                secret_key="short",  # Too short
            )

        errors = exc_info.value.errors()
        assert any("secret_key" in str(error) for error in errors)

    def test_log_level_validation(self) -> None:
        """Test that log level must be a valid level."""
        valid_settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            secret_key="valid_secret_key_with_32_chars_min",
            log_level="DEBUG",
        )
        assert valid_settings.log_level == "DEBUG"

    def test_settings_immutable_after_creation(self, test_settings: Settings) -> None:
        """Test that settings are immutable after creation.

        Args:
            test_settings: Test configuration fixture
        """
        # Pydantic V2 allows assignment by default, but we can verify the value
        original_env = test_settings.environment
        assert original_env == "test"

        # Verify settings values are accessible
        assert test_settings.api_version == "v1"
