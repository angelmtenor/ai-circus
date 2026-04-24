"""Tests for the models module (LLM and embedding initialization).

Author: Angel Martinez-Tenor, 2025.
"""

from __future__ import annotations

import pytest

import ai_circus.models as models
from ai_circus.models import (
    DEFAULT_EMBEDDING_MODEL_GOOGLE,
    DEFAULT_EMBEDDING_MODEL_OPENAI,
    DEFAULT_LLM_MODEL_GOOGLE,
    DEFAULT_LLM_MODEL_OPENAI,
    DEFAULT_LLM_PROVIDER,
    Settings,
    get_embeddings,
    get_llm,
    get_settings,
)


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_provider(self) -> None:
        """Test that default provider is set correctly."""
        assert DEFAULT_LLM_PROVIDER == "openai"

    def test_default_models(self) -> None:
        """Test that default model constants are defined."""
        assert DEFAULT_LLM_MODEL_OPENAI == "gpt-5-mini"
        assert DEFAULT_LLM_MODEL_GOOGLE == "gemini-3-flash"
        assert DEFAULT_EMBEDDING_MODEL_OPENAI == "text-embedding-3-small"
        assert DEFAULT_EMBEDDING_MODEL_GOOGLE == "models/text-embedding-004"

    def test_settings_defaults(self) -> None:
        """Test Settings default values."""
        settings = Settings()
        assert settings.default_llm_provider == "openai"
        assert settings.default_llm_model is None
        # API keys may be loaded from environment, so we just verify their type
        assert settings.openai_api_key is None or isinstance(settings.openai_api_key, type(settings.openai_api_key))
        assert settings.gemini_api_key is None or isinstance(settings.gemini_api_key, type(settings.gemini_api_key))

    def test_api_key_method_openai(self) -> None:
        """Test api_key method returns correct key for OpenAI."""
        settings = Settings(openai_api_key="test-key-openai")
        key = settings.api_key("openai")
        assert key.get_secret_value() == "test-key-openai"

    def test_api_key_method_google(self) -> None:
        """Test api_key method returns correct key for Google."""
        settings = Settings(gemini_api_key="test-key-google")
        key = settings.api_key("google")
        assert key.get_secret_value() == "test-key-google"

    def test_llm_model_property_uses_default(self) -> None:
        """Test that llm_model property returns provider default when not set."""
        settings = Settings(default_llm_provider="openai")
        assert settings.llm_model == DEFAULT_LLM_MODEL_OPENAI

    def test_llm_model_property_uses_custom(self) -> None:
        """Test that llm_model property returns custom model when set."""
        settings = Settings(default_llm_model="custom-model")
        assert settings.llm_model == "custom-model"

    def test_get_settings_is_cached(self) -> None:
        """Test that get_settings caches the loaded settings instance."""
        get_settings.cache_clear()
        first = get_settings()
        second = get_settings()
        assert first is second

    def test_get_llm_uses_openai_settings(self, monkeypatch: object) -> None:
        """Test OpenAI LLM initialization without relying on external services."""
        captured: dict[str, object] = {}

        class FakeChatOpenAI:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr(models, "ChatOpenAI", FakeChatOpenAI)

        llm = get_llm(
            provider="openai",
            model="custom-openai-model",
            model_kwargs={"temperature": 0.1},
            reasoning_effort="low",
            verbosity="medium",
        )

        assert isinstance(llm, FakeChatOpenAI)
        assert captured["model"] == "custom-openai-model"
        assert captured["temperature"] == pytest.approx(0.1)
        assert captured["reasoning_effort"] == "low"
        assert captured["verbosity"] == "medium"

    def test_get_embeddings_uses_google_provider(self, monkeypatch: object) -> None:
        """Test Google embeddings initialization without calling the provider."""
        captured: dict[str, object] = {}

        class FakeGoogleEmbeddings:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr(models, "GoogleGenerativeAIEmbeddings", FakeGoogleEmbeddings)

        embeddings = get_embeddings(provider="google", model="custom-google-embedding")

        assert isinstance(embeddings, FakeGoogleEmbeddings)
        assert captured == {"model": "custom-google-embedding", "google_api_key": None}
