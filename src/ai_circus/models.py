"""
models.py
----------

Initialize and return language models (LLMs) and embedding models
for OpenAI or Google providers. Configuration is handled via Pydantic
Settings and environment variables.

Key features (December 2025):
- Accurate model names: gpt-5.2-chat-latest (low-latency) and gemini-3-flash
- Support for OpenAI text.verbosity ("low" | "medium" | "high")
- Default verbosity: "low" (concise responses)
- reasoning_effort: optional parameter with default None
- Module-level constant DEFAULT_REASONING_EFFORT = None added as requested

Author: Angel Martinez-Tenor (original) + updates
Date: 2025
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Module-level defaults
DEFAULT_LLM_PROVIDER: Literal["openai", "google"] = "openai"

# Current accurate defaults
DEFAULT_LLM_MODEL_OPENAI: str = "gpt-5-mini"
DEFAULT_LLM_MODEL_GOOGLE: str = "gemini-3-flash"
DEFAULT_EMBEDDING_MODEL_OPENAI: str = "text-embedding-3-small"
DEFAULT_EMBEDDING_MODEL_GOOGLE: str = "models/text-embedding-004"

# Reasoning effort default (explicit module constant as requested)
DEFAULT_REASONING_EFFORT: Literal["low", "medium", "high"] | None = None

# Default verbosity: "low" for concise, minimal-prose responses
DEFAULT_VERBOSITY: Literal["low", "medium", "high"] = "low"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    default_llm_provider: Literal["openai", "google"] = DEFAULT_LLM_PROVIDER
    default_llm_model: str | None = None
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    openai_base_url: str | None = None

    @property
    def llm_model(self) -> str:
        """Return the effective LLM model name, falling back to provider defaults."""
        if self.default_llm_model:
            return self.default_llm_model
        return DEFAULT_LLM_MODEL_OPENAI if self.default_llm_provider == "openai" else DEFAULT_LLM_MODEL_GOOGLE

    def api_key(self, provider: Literal["openai", "google"]) -> SecretStr | None:
        """Return the API key for the specified provider."""
        if provider == "openai":
            return self.openai_api_key
        return self.gemini_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached model settings loaded from the environment."""
    return Settings()


def get_llm(
    provider: Literal["openai", "google"] | None = None,
    *,
    reasoning_effort: str | None = DEFAULT_REASONING_EFFORT,  # Uses module constant
    verbosity: Literal["low", "medium", "high"] | None = DEFAULT_VERBOSITY,
    model: str | None = None,
    model_kwargs: dict | None = None,
) -> ChatOpenAI | ChatGoogleGenerativeAI:
    """
    Initialize and return the LLM.

    Parameters
    ----------
    provider
        "openai" or "google". Defaults to settings.
    reasoning_effort
        For OpenAI GPT-5.2 models: None, "medium".
        Default is None (via DEFAULT_REASONING_EFFORT) → no override, model uses its own default.
    verbosity
        For OpenAI text output: "low" (concise), "medium", "high" (more detailed).
        Defaults to None.
    model
        Explicit model name override.
    model_kwargs
        Additional kwargs passed directly to the LangChain client.
    """
    settings = get_settings()
    provider = provider or settings.default_llm_provider
    key = settings.api_key(provider)
    model_kwargs = model_kwargs or {}

    if model is None:
        model = settings.llm_model

    api_key_secret = SecretStr(key.get_secret_value()) if key else None

    if provider == "openai":
        # Base kwargs - start with any user-provided extras
        chat_kwargs = model_kwargs or {}

        chat_kwargs["reasoning_effort"] = reasoning_effort

        # Handle verbosity (already a direct param)
        if verbosity is not None:
            chat_kwargs["verbosity"] = verbosity

        return ChatOpenAI(
            model=model,
            api_key=api_key_secret,
            base_url=settings.openai_base_url,
            **chat_kwargs,
        )

    # Google - no reasoning/verbosity parameters
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=api_key_secret,
        **model_kwargs,
    )


def get_embeddings(
    provider: Literal["openai", "google"] | None = None,
    *,
    model: str | None = None,
) -> Embeddings:
    """Return an embedding model."""
    settings = get_settings()
    provider = provider or settings.default_llm_provider
    key = settings.api_key(provider)
    api_key_secret = SecretStr(key.get_secret_value()) if key else None

    if provider == "openai":
        embedding_model = model or DEFAULT_EMBEDDING_MODEL_OPENAI
        return OpenAIEmbeddings(
            api_key=api_key_secret,
            model=embedding_model,
        )

    embedding_model = model or DEFAULT_EMBEDDING_MODEL_GOOGLE
    return GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=api_key_secret,
    )
