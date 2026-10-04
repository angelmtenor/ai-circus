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
def _prepare_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide mandatory secrets and clear the lru_cache before each test."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-that-is-at-least-20-chars-long")  # gitleaks:allow
    monkeypatch.setenv("GEMINI_API_KEY", "google-test-key-exactly-39-chars-longxx")  # gitleaks:allow
    get_env_config.cache_clear()


def test_get_env_config_default_local(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no APP_ENVIRONMENT set, the 'local' profile (base defaults) is used."""
    monkeypatch.delenv("APP_ENVIRONMENT", raising=False)

    config = get_env_config()

    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3.1-flash-lite"


@pytest.mark.parametrize("profile", ["local", "staging", "production"])
def test_get_env_config_reads_app_environment(monkeypatch: pytest.MonkeyPatch, profile: str) -> None:
    """APP_ENVIRONMENT selects the active profile (all profiles currently fall back to base defaults)."""
    monkeypatch.setenv("APP_ENVIRONMENT", profile)

    config = get_env_config()

    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3.1-flash-lite"


def test_get_env_config_explicit_env_overrides_app_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit `env=` argument takes priority over the APP_ENVIRONMENT variable."""
    monkeypatch.setenv("APP_ENVIRONMENT", "production")

    config = get_env_config(env="staging")

    assert config.LLM_PROVIDER == "google"
    assert config.GEMINI_MODEL == "gemini-3.1-flash-lite"
