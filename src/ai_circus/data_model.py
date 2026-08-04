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
    LLM_PROVIDER: str = Field(description="Default LLM provider to use (openai or google)")
    OPENAI_MODEL: str = Field(description="Default OpenAI model to use")
    GEMINI_MODEL: str = Field(description="Default Google/Gemini model to use")
    OPENAI_API_KEY: SecretStr | None = Field(
        description="API key for accessing OpenAI services for AI-related functionalities", default=None
    )
    GEMINI_API_KEY: SecretStr | None = Field(
        description="API key for accessing Google services (e.g., Maps, Cloud)", default=None
    )
    TAVILY_API_KEY: SecretStr | None = Field(
        description="API key for accessing Tavily services (e.g., data aggregation)", default=None
    )
    LLM_LANGUAGES: str = Field(description="Language for the LLM responses")

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


_SOURCE_YAML_HASH = "68f1b8123451a4ddef95e1e9e26792c6152937bc7afb10313394e9a00366d48e"


EnvConfig.model_rebuild()


def _load_env_overrides(env: str) -> dict[str, Any]:
    """Load per-environment non-secret defaults from settings.yaml.

    Merges the base non-secret defaults with the profile-specific
    overrides defined under ``environments.<env>`` in settings.yaml.
    """
    config_path = Path(__file__).parent.parent.parent / "settings.yaml"
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    base: dict[str, Any] = data.get("environments", {}).get("base", {}).copy()
    base.update(data.get("environments", {}).get(env, {}))
    return base


@lru_cache(maxsize=4)
def get_env_config(env: str | None = None) -> EnvConfig:
    """Return the validated environment configuration for the given profile.

    The active profile is resolved from the *env* argument, then the
    ``APP_ENVIRONMENT`` environment variable, defaulting to ``"local"``.
    Valid profiles: local, staging, production.
    """
    active_env = env or os.getenv("APP_ENVIRONMENT", "local")
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
