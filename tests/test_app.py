"""Tests for application startup behavior."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace
from typing import ClassVar

import pytest
from pydantic import BaseModel, ValidationError

import ai_circus.app as app


class FakeLogger:
    """Minimal logger used to capture app log calls."""

    def __init__(self) -> None:
        """Initialize in-memory message collectors used by tests."""
        self.success_messages: list[tuple[object, ...]] = []
        self.error_messages: list[tuple[object, ...]] = []
        self.info_messages: list[tuple[object, ...]] = []

    def success(self, *args: object) -> None:
        """Record success log calls."""
        self.success_messages.append(args)

    def error(self, *args: object) -> None:
        """Record error log calls."""
        self.error_messages.append(args)

    def info(self, *args: object) -> None:
        """Record info log calls."""
        self.info_messages.append(args)

    def exception(self, *args: object) -> None:
        """Map exception logging to the error collector for test assertions."""
        self.error(*args)


def build_validation_error() -> ValidationError:
    """Create a Pydantic validation error for testing startup failures."""

    class RequiredConfig(BaseModel):
        required_value: int

    try:
        RequiredConfig()
    except ValidationError as exc:
        return exc
    raise AssertionError("Expected ValidationError was not raised")


def test_main_runs_with_lazy_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that app.main loads config lazily and invokes the configured LLM."""
    fake_logger = FakeLogger()

    class FakeSecret:
        def get_secret_value(self) -> str:
            return "sk-test-12345678901234567890"

    class FakeEnvConfig:
        model_fields: ClassVar[dict[str, object]] = {"OPENAI_API_KEY": object(), "LLM_LANGUAGES": object()}

    fake_env = SimpleNamespace(OPENAI_API_KEY=FakeSecret(), LLM_LANGUAGES="Spanish")
    fake_data_model = ModuleType("ai_circus.data_model")
    fake_data_model.EnvConfig = FakeEnvConfig
    fake_data_model.get_env_config = lambda: fake_env

    class FakeLLM:
        def invoke(self, prompt: str) -> SimpleNamespace:
            return SimpleNamespace(content=f"response for {prompt}")

    fake_models = ModuleType("ai_circus.models")
    fake_models.get_llm = lambda provider=None: FakeLLM()

    monkeypatch.setattr(app, "logger", fake_logger)
    monkeypatch.setattr(app, "configure_logger", lambda: None)
    monkeypatch.setitem(sys.modules, "ai_circus.data_model", fake_data_model)
    monkeypatch.setitem(sys.modules, "ai_circus.models", fake_models)

    app.main()

    assert fake_logger.success_messages
    assert any("Spanish" in str(args) for args in fake_logger.info_messages)


def test_main_exits_on_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that app.main exits with code 1 when config validation fails."""
    fake_logger = FakeLogger()
    validation_error = build_validation_error()

    fake_data_model = ModuleType("ai_circus.data_model")
    fake_data_model.EnvConfig = SimpleNamespace(model_fields={})

    def raise_validation_error() -> object:
        raise validation_error

    fake_data_model.get_env_config = raise_validation_error

    monkeypatch.setattr(app, "logger", fake_logger)
    monkeypatch.setattr(app, "configure_logger", lambda: None)
    monkeypatch.setitem(sys.modules, "ai_circus.data_model", fake_data_model)

    with pytest.raises(SystemExit) as exc_info:
        app.main()

    assert exc_info.value.code == 1
    assert fake_logger.error_messages
