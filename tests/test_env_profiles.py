"""
test_env_profiles.py
--------------------

Tests for the environment-aware configuration loading.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import pytest

from ai_circus.data_model import get_env_config


@pytest.fixture(autouse=True)
def _clear_env_config_cache() -> None:
    """Clear the lru_cache on get_env_config before each test."""
    get_env_config.cache_clear()


def test_get_env_config_default_local(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that default environment is 'local'."""
    monkeypatch.delenv("APP_ENV", raising=False)
    # Ensure mandatory secrets are provided for Pydantic validation
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-that-is-at-least-20-chars-long")  # gitleaks:allow
    monkeypatch.setenv("GEMINI_API_KEY", "google-test-key-that-is-exactly-39-chars-")  # gitleaks:allow

    config = get_env_config()
    # Assuming 'local' sets GEMINI_MODEL to 'gemini-3-flash-preview'
    # and LLM_PROVIDER to 'google'
    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3-flash-preview"


def test_get_env_config_with_explicit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test passing an explicit env name to get_env_config."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-that-is-at-least-20-chars-long")  # gitleaks:allow
    monkeypatch.setenv("GEMINI_API_KEY", "google-test-key-that-is-exactly-39-chars-")  # gitleaks:allow

    # Even if APP_ENV is set...
    monkeypatch.setenv("APP_ENV", "ministack")

    # ...an explicit argument should override it
    config = get_env_config(env="fucci")

    # Depending on how fucci is defined in settings.yaml, we check the result.
    # Currently fucci sets LLM_PROVIDER="google" and GEMINI_MODEL="gemini-3-flash-preview".
    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3-flash-preview"


def test_get_env_config_reads_app_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_env_config reads the APP_ENV environment variable."""
    monkeypatch.setenv("APP_ENV", "ministack")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-that-is-at-least-20-chars-long")  # gitleaks:allow
    monkeypatch.setenv("GEMINI_API_KEY", "google-test-key-that-is-exactly-39-chars-")  # gitleaks:allow

    config = get_env_config()

    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3-flash-preview"
