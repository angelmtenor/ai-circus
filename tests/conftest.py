"""Shared test fixtures for ai-circus test suite."""

from __future__ import annotations

import warnings

# langchain_core.__init__ unconditionally re-enables its own pending-deprecation
# warnings on import (surface_langchain_deprecation_warnings), which overrides any
# "ignore" filter set beforehand (e.g. via pyproject.toml). Import it and re-silence
# here, before anything below pulls in ai_circus (whose package __init__ eagerly
# imports langgraph and triggers the warning), so our filter takes precedence.
from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

import sys  # noqa: E402
from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402

import ai_circus.core.logger as _logger_module  # noqa: E402


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
