"""Tests for the API client module.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import importlib

import pytest

from ai_circus.tools.check_api_keys import APIClient, APIConfig, resolve_api_config

api_client_module = importlib.import_module("ai_circus.tools.check_api_keys")


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

    def test_resolve_api_config_keeps_source_immutable(self) -> None:
        """Test that dynamic request values are resolved without mutating the input config."""
        config = APIConfig(
            name="OpenAI",
            url=lambda key: f"https://example.com/{key}",
            headers=lambda key: {"Authorization": f"Bearer {key}"},
        )

        resolved = resolve_api_config(config, "secret")

        assert callable(config.url)
        assert callable(config.headers)
        assert resolved.url == "https://example.com/secret"
        assert resolved.headers == {"Authorization": "Bearer secret"}

    def test_fetch_data_returns_json_on_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that fetch_data parses JSON responses through the configured client."""

        class FakeResponse:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> dict[str, str]:
                return {"status": "ok"}

        class FakeClient:
            def __enter__(self) -> FakeClient:
                return self

            def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
                return None

            def get(self, **kwargs: object) -> FakeResponse:
                return FakeResponse()

        monkeypatch.setattr(api_client_module.httpx, "Client", FakeClient)

        config = APIConfig(name="test_api", url="https://api.example.com")
        result = APIClient.fetch_data(config)

        assert result == {"status": "ok"}

    def test_fetch_data_returns_none_on_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that fetch_data returns None when the client raises an HTTP error."""

        class FakeClient:
            def __enter__(self) -> FakeClient:
                return self

            def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
                return None

            def get(self, **kwargs: object) -> object:
                raise api_client_module.httpx.HTTPError("boom")

        monkeypatch.setattr(api_client_module.httpx, "Client", FakeClient)

        config = APIConfig(name="invalid_api", url="https://api.example.com")
        result = APIClient.fetch_data(config)

        assert result is None
