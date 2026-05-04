"""Shared test fixtures for ai-circus test suite."""

from __future__ import annotations

import sys
from collections.abc import Generator

import pytest

import ai_circus.core.logger as _logger_module


@pytest.fixture(autouse=True)
def reset_singletons() -> Generator[None]:
    """Clear lru_cache singletons and module-level state between tests."""
    # Clear cached module to force re-import
    sys.modules.pop("ai_circus.data_model", None)
    # Reset loguru configuration flag so configure_logger() works fresh each test
    _logger_module._configured = False

    yield

    # Post-test cleanup: reset any cached settings
    try:
        from ai_circus.data_model import get_env_config

        get_env_config.cache_clear()
    except ImportError:
        pass
