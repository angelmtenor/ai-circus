"""Tool "Hello World" for AI Circus.
Author: Angel Martinez-Tenor, 2025. Adapted from https://github.com/angelmtenor/ds-template
"""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings

from ai_circus.core.info import info_system
from ai_circus.core.logger import configure_logger


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    log_level: str = "INFO"
    app_name: str = "AI Circus"
    openai_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")

    class Config:
        """Pydantic configuration for environment variable loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Load settings
settings = Settings()

# Initialize logger
logger = configure_logger(level=settings.log_level)


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
    info_system()

    simple = SimpleClass(settings.app_name)
    simple.greet()


if __name__ == "__main__":
    main()
