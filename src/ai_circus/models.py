"""
models.py
----------

Initialize and return language models (LLMs) and embedding models
for OpenAI or Google providers. Configuration is handled via
the centralized EnvConfig.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ai_circus.data_model import get_env_config

# Default embedding models
DEFAULT_EMBEDDING_MODEL_OPENAI: str = "text-embedding-3-small"
DEFAULT_EMBEDDING_MODEL_GOOGLE: str = "models/gemini-embedding-001"


def get_llm(
    provider: str | None = None,
    *,
    model: str | None = None,
    **kwargs: Any,
) -> ChatOpenAI | ChatGoogleGenerativeAI:
    """
    Initialize and return the LLM.

    Parameters
    ----------
    provider
        "openai" or "google" (any other value falls back to "google"). Defaults to LLM_PROVIDER in env.
    model
        Explicit model name override.
    **kwargs
        Additional kwargs passed directly to the LangChain client.
    """
    config = get_env_config()
    provider = provider or config.LLM_PROVIDER

    if provider == "openai":
        llm_model = model or config.OPENAI_MODEL
        api_key = config.OPENAI_API_KEY
        return ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            **kwargs,
        )

    # Google
    llm_model = model or config.GEMINI_MODEL
    api_key = config.GEMINI_API_KEY
    return ChatGoogleGenerativeAI(
        model=llm_model,
        api_key=api_key,
        **kwargs,
    )


def get_embeddings(
    provider: str | None = None,
    *,
    model: str | None = None,
) -> Embeddings:
    """Return an embedding model."""
    config = get_env_config()
    provider = provider or config.LLM_PROVIDER

    if provider == "openai":
        embedding_model = model or DEFAULT_EMBEDDING_MODEL_OPENAI
        return OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY,
            model=embedding_model,
        )

    embedding_model = model or DEFAULT_EMBEDDING_MODEL_GOOGLE
    return GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=config.GEMINI_API_KEY,
    )
