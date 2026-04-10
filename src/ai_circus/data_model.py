"""
data_model.py
-----------
Generated Pydantic Settings model from env_config.yaml.
DO NOT EDIT DIRECTLY. Run 'make generate' to update.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import re
from typing import Any

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
    OPENAI_API_KEY: SecretStr | None = Field(
        default=None, description="API key for accessing OpenAI services for AI-related functionalities"
    )
    GEMINI_API_KEY: SecretStr | None = Field(
        default=None, description="API key for accessing Google services (e.g., Maps, Cloud)"
    )
    TAVILY_API_KEY: SecretStr | None = Field(
        default=None, description="API key for accessing Tavily services (e.g., data aggregation)"
    )

    @field_validator("OPENAI_API_KEY", mode="after")
    @classmethod
    def validate_openai_api_key(cls, v: Any) -> Any:
        """Validate field format via regex."""
        if v is None:
            return v
        val = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
        if not re.match(r"^[a-zA-Z0-9-]{20,}$", val):
            raise ValueError("Invalid OpenAI API key format. Expected a string of at least 20 alphanumeric characters.")
        return v

    @field_validator("GEMINI_API_KEY", mode="after")
    @classmethod
    def validate_gemini_api_key(cls, v: Any) -> Any:
        """Validate field format via regex."""
        if v is None:
            return v
        val = v.get_secret_value() if hasattr(v, "get_secret_value") else str(v)
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
        if not re.match(r"^[a-zA-Z0-9_-]{16,}$", val):
            raise ValueError("Invalid Tavily API key format. Expected at least 16 alphanumeric characters.")
        return v


EnvConfig.model_rebuild()

env_config = EnvConfig()


def main() -> None:
    """Display the loaded configuration (redacted)."""
    print("--- Loaded Configuration ---")  # noqa: T201
    for field in EnvConfig.model_fields:
        val = getattr(env_config, field)
        if hasattr(val, "get_secret_value"):
            val = "****" + val.get_secret_value()[-4:] if val and val.get_secret_value() else "None"
        print(f"{field}: {val}")  # noqa: T201


if __name__ == "__main__":
    main()
