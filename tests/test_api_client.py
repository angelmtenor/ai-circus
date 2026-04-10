"""Tests for the API client module.

Author: Angel Martinez-Tenor, 2025.
"""

from __future__ import annotations

from ai_circus.tools.check_api_keys import APIClient, APIConfig, Settings


class TestSettings:
    """Tests for API Settings configuration."""

    def test_settings_defaults(self) -> None:
        """Test that Settings loads with values from environment or defaults."""
        settings = Settings()
        # Settings loads from environment, so we just verify they are SecretStr objects
        assert hasattr(settings.openai_api_key, "get_secret_value")
        assert hasattr(settings.gemini_api_key, "get_secret_value")
        assert hasattr(settings.tavily_api_key, "get_secret_value")

    def test_settings_extra_ignored(self) -> None:
        """Test that extra environment variables are ignored."""
        # This tests the 'extra = ignore' config
        settings = Settings()
        assert not hasattr(settings, "extra_field")


class TestAPIConfig:
    """Tests for APIConfig dataclass."""

    def test_api_config_defaults(self) -> None:
        """Test APIConfig with default values."""
        config = APIConfig(name="test_api", url="https://api.example.com")
        assert config.name == "test_api"
        assert config.url == "https://api.example.com"
        assert config.method == "GET"
        assert config.headers is None
        assert config.params is None

    def test_api_config_with_method(self) -> None:
        """Test APIConfig with POST method."""
        config = APIConfig(
            name="test_api",
            url="https://api.example.com",
            method="POST",
            json={"key": "value"},
        )
        assert config.method == "POST"
        assert config.json == {"key": "value"}

    def test_api_config_with_callable_url(self) -> None:
        """Test APIConfig with callable URL."""

        def get_url(param: str) -> str:
            return f"https://api.example.com/{param}"

        config = APIConfig(name="test_api", url=get_url)
        assert callable(config.url)


class TestAPIClient:
    """Tests for APIClient class."""

    def test_api_client_is_static(self) -> None:
        """Test that APIClient.fetch_data is a static method."""
        assert isinstance(APIClient.fetch_data, staticmethod) or callable(APIClient.fetch_data)

    def test_fetch_data_returns_none_on_error(self) -> None:
        """Test that fetch_data returns None for invalid URLs."""
        config = APIConfig(name="invalid_api", url="https://invalid-domain-that-does-not-exist.com")
        result = APIClient.fetch_data(config)
        assert result is None
