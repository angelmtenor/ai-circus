"""Tool: Check API Keys and Fetch Data from APIs
Author: Angel Martinez-Tenor, 2025. Adapted from https://github.com/angelmtenor/ds-template
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import httpx
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from ai_circus.core.info import info_system
from ai_circus.core.logger import configure_logger

# Initialize logger
logger = configure_logger(level="INFO")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")
    tavily_api_key: SecretStr = SecretStr("")

    class Config:
        """Pydantic configuration for environment variable loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Load settings
settings = Settings()


@dataclass
class APIConfig:
    """Configuration for API endpoints and request parameters."""

    name: str
    url: str | Callable[[str], str]
    method: str = "GET"
    headers: dict[str, str] | Callable[[str], dict[str, str]] | None = None
    json: dict | Callable[[str], dict] | None = None
    params: dict | Callable[[str], dict] | None = None


class APIClient:
    """Generic API client for making HTTP requests."""

    @staticmethod
    def fetch_data(config: APIConfig) -> dict | None:
        """Fetch data from an API with the given configuration."""
        try:
            with httpx.Client() as client:
                request_kwargs: dict = {"url": config.url, "timeout": 10.0}
                if config.headers:
                    request_kwargs["headers"] = config.headers
                if config.params:
                    request_kwargs["params"] = config.params
                # Only include json for POST requests
                if config.method.upper() == "POST":
                    request_kwargs["json"] = config.json

                if config.method.upper() == "GET":
                    response = client.get(**request_kwargs)
                else:
                    response = client.post(**request_kwargs)
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    resp = e.response
                    body = resp.text if resp is not None else "<no response body>"
                    status = resp.status_code if resp is not None else "<no status>"
                    logger.error(f"Failed to fetch {config.name} data: status={status} body={body}")
                    return None
                # Safely parse JSON responses
                try:
                    return response.json()
                except ValueError:
                    logger.error(f"Non-JSON response from {config.name}: {response.text}")
                    return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch {config.name} data: {e}")
            return None


def main() -> None:
    """Main function to execute API data fetching."""
    logger.info("Starting the script...")
    info_system()

    # API configurations
    api_configs = [
        APIConfig(
            name="OpenAI",
            url="https://api.openai.com/v1/models",
            headers=lambda key: {"Authorization": f"Bearer {key}"},
        ),
        APIConfig(
            name="Google",
            url="https://www.googleapis.com/discovery/v1/apis",
            params=lambda key: {"key": key},
        ),
        APIConfig(
            name="Gemini",
            url="https://generativelanguage.googleapis.com/v1/models",
            params=lambda key: {"key": key},
        ),
        APIConfig(
            name="Tavily",
            url="https://api.tavily.com/search",
            method="POST",
            json=lambda key: {"api_key": key, "query": "example search"},
        ),
    ]

    # Retrieve API keys
    api_keys = {
        "OpenAI": settings.openai_api_key.get_secret_value(),
        "Google": settings.gemini_api_key.get_secret_value(),
        "Gemini": settings.gemini_api_key.get_secret_value(),
        "Tavily": settings.tavily_api_key.get_secret_value(),
    }

    # Initialize checklist to log the status of each API
    checklist = []

    # Fetch data from APIs
    client = APIClient()
    for config in api_configs:
        api_key = api_keys.get(config.name, "")
        if not api_key:
            logger.warning(f"Skipping {config.name} API due to missing API key")
            checklist.append(f"[ ] {config.name}: missing API key (skipped)")
            continue
        logger.info(f"Fetching data from {config.name} API...")
        # Dynamically resolve headers, json, or params if they're callable
        config.headers = config.headers(api_key) if callable(config.headers) else config.headers
        config.json = config.json(api_key) if callable(config.json) else config.json
        config.params = config.params(api_key) if callable(config.params) else config.params
        config.url = config.url(api_key) if callable(config.url) else config.url

        data = client.fetch_data(config)
        if data:
            if isinstance(data, dict):
                key = "data" if config.name == "OpenAI" else "items" if config.name == "Google" else "results"
                sample = data.get(key, [])
                try:
                    preview = sample[:1]
                except Exception:
                    preview = sample
                logger.info(f"{config.name} data retrieved: {preview}")
            else:
                logger.info(f"{config.name} data retrieved (non-dict): type={type(data)}")
            checklist.append(f"[✔] {config.name}: data retrieved")
        else:
            checklist.append(f"[ ] {config.name}: call failed")

    # Print checklist summary
    logger.info("Checklist summary:")
    for item in checklist:
        logger.info(item)


class SimpleClass:
    """A simple class for demonstration purposes."""

    def __init__(self, name: str) -> None:
        """Initialize the class with a name."""
        self.name = name

    def greet(self) -> None:
        """Print a greeting message."""
        logger.info(f"Hello, {self.name}!")


if __name__ == "__main__":
    main()
