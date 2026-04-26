"""Tool "Hello World" for AI Circus.
Author: Angel Martinez-Tenor, 2026. Adapted from https://github.com/angelmtenor/ds-template
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_circus.core.info import info_system
from ai_circus.core.logger import configure_logger, get_logger


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    log_level: str = "INFO"
    app_name: str = "AI Circus"
    openai_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached tool settings."""
    return Settings()


logger = get_logger(__name__)


class SimpleClass:
    """A simple class for demonstration purposes."""

    def __init__(self, name: str) -> None:
        """Initialize the class with a name."""
        self.name = name

    def greet(self) -> None:
        """Print a greeting message."""
        logger.info(f"Hello, {self.name}!")


def main() -> None:
    """Main function to demonstrate the functionality of the module."""
    settings = get_settings()
    configure_logger(level=settings.log_level)
    info_system()

    simple = SimpleClass(settings.app_name)
    simple.greet()


if __name__ == "__main__":
    main()
