"""Shared test fixtures for ai-circus test suite."""

from __future__ import annotations

import sys
from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None]:
    """Clear lru_cache singletons between tests to ensure isolation."""
    # Clear cached module to force re-import
    sys.modules.pop("ai_circus.data_model", None)

    yield

    # Post-test cleanup: reset any cached settings
    try:
        from ai_circus.data_model import get_env_config

        get_env_config.cache_clear()
    except ImportError:
        pass
