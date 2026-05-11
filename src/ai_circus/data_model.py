"""
data_model.py
-----------
Generated Pydantic Settings model from settings.yaml.
DO NOT EDIT DIRECTLY. Run 'make generate' to update.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Environment configuration model."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )
    LLM_PROVIDER: str = Field(description="Default LLM provider to use (openai or google)", default="google")
    OPENAI_MODEL: str = Field(description="Default OpenAI model to use", default="gpt-5.4-mini")
    GEMINI_MODEL: str = Field(description="Default Google/Gemini model to use", default="gemini-3-flash-preview")
    OPENAI_API_KEY: SecretStr | None = Field(
        description="API key for accessing OpenAI services for AI-related functionalities", default=None
    )
    GEMINI_API_KEY: SecretStr | None = Field(
        description="API key for accessing Google services (e.g., Maps, Cloud)", default=None
    )
    TAVILY_API_KEY: SecretStr | None = Field(
        description="API key for accessing Tavily services (e.g., data aggregation)", default=None
    )
    LLM_LANGUAGES: str = Field(description="Language for the LLM responses", default="English")

    @field_validator("OPENAI_API_KEY", mode="after")
    @classmethod
    def validate_openai_api_key(cls, v: Any) -> Any:
        """Validate field format via regex."""
        if v is None:
            return v
        val = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if not val:
            return None
        if not re.match(r"^sk-[A-Za-z0-9_-]{20,}$", val):
            raise ValueError(
                "Invalid OpenAI API key format. Expected an OpenAI key starting with sk- and at least 20 characters."
            )
        return v

    @field_validator("GEMINI_API_KEY", mode="after")
    @classmethod
    def validate_gemini_api_key(cls, v: Any) -> Any:
        """Validate field format via regex."""
        if v is None:
            return v
        val = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if not val:
            return None
        if not re.match(r"^[a-zA-Z0-9-_]{39}$", val):
            raise ValueError(
                "Invalid Google API key format. Expected a 39-character string with alphanumeric and hyphen/underscore."
            )
        return v

    @field_validator("TAVILY_API_KEY", mode="after")
    @classmethod
    def validate_tavily_api_key(cls, v: Any) -> Any:
        """Validate field format via regex."""
        if v is None:
            return v
        val = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if not val:
            return None
        if not re.match(r"^[a-zA-Z0-9_-]{16,}$", val):
            raise ValueError("Invalid Tavily API key format. Expected at least 16 alphanumeric characters.")
        return v


_SOURCE_YAML_HASH = "0a894183bb415b39470ba5b2b576c05eb69a5ac05a2e162c3cb2ff91961f5a18"


EnvConfig.model_rebuild()


def _load_env_overrides(env: str) -> dict[str, Any]:
    """Load per-environment non-secret defaults from settings.yaml.

    Merges the base non-secret defaults with the profile-specific
    overrides defined under ``environments.<env>`` in settings.yaml.
    """
    config_path = Path(__file__).parent.parent.parent / "settings.yaml"
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    base: dict[str, Any] = {}
    for v in data.get("env_variables", []):
        if v.get("default") is not None and not v.get("secret", False):
            base[v["name"]] = v["default"]
    base.update(data.get("environments", {}).get(env, {}))
    return base


@lru_cache(maxsize=4)
def get_env_config(env: str | None = None) -> EnvConfig:
    """Return the validated environment configuration for the given profile.

    The active profile is resolved from the *env* argument, then the
    ``APP_ENV`` environment variable, defaulting to ``"local"``.
    Valid profiles: local, fucci, ministack.
    """
    active_env = env or os.getenv("APP_ENV", "local")
    overrides = _load_env_overrides(active_env)
    return EnvConfig(**overrides)


def main() -> None:
    """Display the loaded configuration (redacted)."""
    env_config = get_env_config()
    print("--- Loaded Configuration ---")  # noqa: T201
    for field in EnvConfig.model_fields:
        val = getattr(env_config, field)
        if hasattr(val, "get_secret_value"):
            val = "****" + val.get_secret_value()[-4:] if val and val.get_secret_value() else "None"
        print(f"{field}: {val}")  # noqa: T201


if __name__ == "__main__":
    main()
