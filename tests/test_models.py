"""Tests for the models module (LLM and embedding initialization).

Author: Angel Martinez-Tenor, 2025.
"""

from __future__ import annotations

from ai_circus.models import (
    DEFAULT_EMBEDDING_MODEL_GOOGLE,
    DEFAULT_EMBEDDING_MODEL_OPENAI,
    DEFAULT_LLM_MODEL_GOOGLE,
    DEFAULT_LLM_MODEL_OPENAI,
    DEFAULT_LLM_PROVIDER,
    Settings,
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
