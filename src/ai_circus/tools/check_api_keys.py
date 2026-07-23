"""Tool: Check API Keys and Fetch Data from APIs
Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import httpx

from ai_circus import get_env_config
from ai_circus.core.info import info_system
from ai_circus.core.logger import configure_logger, get_logger

logger = get_logger(__name__)


@dataclass
class APIConfig:
    """Configuration for API endpoints and request parameters."""

    name: str
    url: str | Callable[[str], str]
    method: str = "GET"
    headers: dict[str, str] | Callable[[str], dict[str, str]] | None = None
    json: dict[str, str] | Callable[[str], dict[str, str]] | None = None
    params: dict[str, str] | Callable[[str], dict[str, str]] | None = None


def resolve_api_config(config: APIConfig, api_key: str) -> APIConfig:
    """Resolve dynamic APIConfig callables without mutating the source config."""
    return APIConfig(
        name=config.name,
        url=config.url(api_key) if callable(config.url) else config.url,
        method=config.method,
        headers=config.headers(api_key) if callable(config.headers) else config.headers,
        json=config.json(api_key) if callable(config.json) else config.json,
        params=config.params(api_key) if callable(config.params) else config.params,
    )


def get_preview_key(config_name: str) -> str:
    """Return the expected top-level preview key for an API response."""
    if config_name == "OpenAI":
        return "data"
    return "results"


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
    configure_logger(level="INFO")
    logger.info("Starting the script...")
    info_system()
    config = get_env_config()

    # API configurations
    api_configs = [
        APIConfig(
            name="OpenAI",
            url="https://api.openai.com/v1/models",
            headers=lambda key: {"Authorization": f"Bearer {key}"},
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
        "OpenAI": config.OPENAI_API_KEY.get_secret_value() if config.OPENAI_API_KEY else "",
        "Gemini": config.GEMINI_API_KEY.get_secret_value() if config.GEMINI_API_KEY else "",
        "Tavily": config.TAVILY_API_KEY.get_secret_value() if config.TAVILY_API_KEY else "",
    }

    # Initialize checklist to log the status of each API
    checklist = []

    # Fetch data from APIs
    client = APIClient()
    for api_config in api_configs:
        api_key = api_keys.get(api_config.name, "")
        if not api_key:
            logger.warning(f"Skipping {api_config.name} API due to missing API key")
            checklist.append(f"[ ] {api_config.name}: missing API key (skipped)")
            continue
        logger.info(f"Fetching data from {api_config.name} API...")
        data = client.fetch_data(resolve_api_config(api_config, api_key))
        if data:
            if isinstance(data, dict):
                key = get_preview_key(api_config.name)
                sample = data.get(key, [])
                try:
                    preview = sample[:1]
                except Exception:
                    preview = sample
                logger.info(f"{api_config.name} data retrieved: {preview}")
            else:
                logger.info(f"{api_config.name} data retrieved (non-dict): type={type(data)}")
            checklist.append(f"[✔] {api_config.name}: data retrieved")
        else:
            checklist.append(f"[ ] {api_config.name}: call failed")

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
