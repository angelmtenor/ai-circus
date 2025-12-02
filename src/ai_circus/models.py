"""
This module provides functions to initialize and return a language model (LLM)
and embedding model based on the specified provider (OpenAI or Google).
It uses Pydantic Settings for configuration.
Author: Angel Martinez-Tenor, 2025
"""

from __future__ import annotations

from typing import Literal

from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    default_llm_provider: Literal["openai", "google"] = "openai"
    default_llm_model: str | None = None
    openai_api_key: SecretStr = SecretStr("")
    google_api_key: SecretStr = SecretStr("")

    class Config:
        """Pydantic configuration for environment variable loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def llm_model(self) -> str:
        """Return default LLM model depending on the provider if not explicitly set."""
        if self.default_llm_model:
            return self.default_llm_model
        return "gpt-5-mini" if self.default_llm_provider == "openai" else "gemini-2.5-flash"

    def api_key(self, provider: Literal["openai", "google"]) -> SecretStr:
        """Return the API key for the given provider."""
        if provider == "openai":
            return self.openai_api_key
        if provider == "google":
            return self.google_api_key


# Load settings
settings = Settings()


def get_llm(
    provider: Literal["openai", "google"] = settings.default_llm_provider,
) -> ChatOpenAI | ChatGoogleGenerativeAI:
    """Initialize and return the LLM based on the provider."""
    key = settings.api_key(provider)

    if provider == "openai":
        return ChatOpenAI(model=settings.llm_model, api_key=key)
    if provider == "google":
        return ChatGoogleGenerativeAI(model=settings.llm_model, google_api_key=key.get_secret_value())


def get_embeddings(provider: Literal["openai", "google"] = settings.default_llm_provider) -> Embeddings:
    """Return an embedding model based on the provider."""
    key = settings.api_key(provider)

    if provider == "openai":
        return OpenAIEmbeddings(api_key=key, model="text-embedding-3-small")
    if provider == "google":
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=key)
