"""Tests for lazy environment configuration loading."""

from __future__ import annotations

import importlib
import sys


def test_data_model_import_does_not_validate_environment(monkeypatch: object) -> None:
    """Importing the module should not instantiate EnvConfig eagerly."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    sys.modules.pop("ai_circus.data_model", None)

    module = importlib.import_module("ai_circus.data_model")

    assert hasattr(module, "get_env_config")
    assert not hasattr(module, "env_config")
