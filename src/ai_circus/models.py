"""
models.py
----------

Initialize and return language models (LLMs) and embedding models
for OpenAI or Google providers. Configuration is handled via Pydantic
Settings and environment variables.

Author: Angel Martinez-Tenor
Date: 2025
"""

from __future__ import annotations

from typing import Literal

from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr
from pydantic_settings import BaseSettings

# Module-level defaults (can be overridden at import time if needed)
DEFAULT_LLM_PROVIDER: Literal["openai", "google"] = "openai"

# Provider-specific defaults (late-2025 low-latency models)
DEFAULT_LLM_MODEL_OPENAI: str = "gpt-5.2-chat-latest"  # Instant/low-latency variant
DEFAULT_LLM_MODEL_GOOGLE: str = "gemini-3-flash"  # Fastest Gemini variant
DEFAULT_EMBEDDING_MODEL_OPENAI: str = "text-embedding-3-large"
DEFAULT_EMBEDDING_MODEL_GOOGLE: str = "models/embedding-001"

# Default reasoning effort: "minimal" for lowest latency on GPT-5 series
DEFAULT_REASONING_EFFORT: str | None = None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    default_llm_provider: Literal["openai", "google"] = DEFAULT_LLM_PROVIDER
    default_llm_model: str | None = None
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None

    class Config:
        """Pydantic configuration for environment variable loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def llm_model(self) -> str:
        """Fallback model if not explicitly set."""
        if self.default_llm_model:
            return self.default_llm_model
        return DEFAULT_LLM_MODEL_OPENAI if self.default_llm_provider == "openai" else DEFAULT_LLM_MODEL_GOOGLE

    def api_key(self, provider: Literal["openai", "google"]) -> SecretStr | None:
        """Return the API key for the given provider (may be None if not set)."""
        if provider == "openai":
            return self.openai_api_key
        return self.gemini_api_key


settings = Settings()


def get_llm(
    provider: Literal["openai", "google"] | None = None,
    *,
    reasoning_effort: str | None = DEFAULT_REASONING_EFFORT,
    model: str | None = None,
    model_kwargs: dict | None = None,
) -> ChatOpenAI | ChatGoogleGenerativeAI:
    """
    Initialize and return the LLM based on the provider.

    Parameters
    ----------
    provider
        "openai" or "google". Defaults to module/settings default.
    reasoning_effort
        For OpenAI 5.2 reasoning models. Defaults to None for lower latency.
        Increase to "medium" or higher for more detailed reasoning.
    model
        Explicit model name override.
    model_kwargs
        Additional kwargs passed to the LangChain client.
    """
    provider = provider or settings.default_llm_provider
    key = settings.api_key(provider)
    model_kwargs = model_kwargs or {}

    # Resolve model name
    if model is None:
        model = DEFAULT_LLM_MODEL_OPENAI if provider == "openai" else DEFAULT_LLM_MODEL_GOOGLE
        model = model or settings.llm_model

    # LangChain accepts SecretStr | None directly
    api_key_secret = key

    # Apply reasoning_effort for OpenAI (top-level parameter)
    if provider == "openai" and reasoning_effort is not None:
        model_kwargs["reasoning_effort"] = reasoning_effort

    if provider == "openai":
        return ChatOpenAI(
            model=model,
            api_key=api_key_secret,
            model_kwargs=model_kwargs,
        )

    # Google
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key_secret,
        **model_kwargs,
    )


def get_embeddings(
    provider: Literal["openai", "google"] | None = None,
    *,
    model: str | None = None,
) -> Embeddings:
    """
    Return an embedding model based on the provider.

    Parameters
    ----------
    provider
        "openai" or "google". Defaults to settings default provider.
    model
        Optional explicit model name.
    """
    provider = provider or settings.default_llm_provider
    key = settings.api_key(provider)
    api_key_secret = key

    if provider == "openai":
        embedding_model = model or DEFAULT_EMBEDDING_MODEL_OPENAI
        return OpenAIEmbeddings(
            api_key=api_key_secret,
            model=embedding_model,
        )

    # Google
    embedding_model = model or DEFAULT_EMBEDDING_MODEL_GOOGLE
    return GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=api_key_secret,
    )
