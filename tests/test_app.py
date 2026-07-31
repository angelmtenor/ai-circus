"""Tests for application startup behavior."""

from __future__ import annotations

from types import SimpleNamespace
from typing import ClassVar

import pytest
from pydantic import BaseModel, ValidationError

import ai_circus.app as app
from tests.conftest import FakeSecret


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

    class FakeEnvConfig:
        model_fields: ClassVar[dict[str, object]] = {
            "OPENAI_API_KEY": object(),
            "LLM_LANGUAGES": object(),
            "LLM_PROVIDER": object(),
            "OPENAI_MODEL": object(),
            "GEMINI_MODEL": object(),
        }

        def __init__(self) -> None:
            self.OPENAI_API_KEY = FakeSecret()
            self.LLM_LANGUAGES = "Spanish"
            self.LLM_PROVIDER = "openai"
            self.OPENAI_MODEL = "gpt-4o"
            self.GEMINI_MODEL = "gemini-1.5-flash"

    # A real instance (not a SimpleNamespace) so that `type(config).model_fields`
    # resolves the same way it does for the real Pydantic EnvConfig.
    fake_env = FakeEnvConfig()

    class FakeLLM:
        def invoke(self, prompt: str) -> SimpleNamespace:
            return SimpleNamespace(content=f"response for {prompt}")

    monkeypatch.setattr(app, "logger", fake_logger)
    monkeypatch.setattr(app, "configure_logger", lambda: None)
    monkeypatch.setattr(app, "get_env_config", lambda: fake_env)
    monkeypatch.setattr(app, "get_llm", lambda: FakeLLM())

    app.main()

    assert fake_logger.success_messages
    assert any("Spanish" in str(args) for args in fake_logger.info_messages)


def test_main_exits_on_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that app.main exits with code 1 when config validation fails."""
    fake_logger = FakeLogger()
    validation_error = build_validation_error()

    def raise_validation_error() -> object:
        raise validation_error

    monkeypatch.setattr(app, "logger", fake_logger)
    monkeypatch.setattr(app, "configure_logger", lambda: None)
    monkeypatch.setattr(app, "get_env_config", raise_validation_error)

    with pytest.raises(SystemExit) as exc_info:
        app.main()

    assert exc_info.value.code == 1
    assert fake_logger.error_messages
