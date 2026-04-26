"""AI Circus: A building block for generative AI tool applications.

This package provides state-of-the-art tools and components for building intelligent
AI applications with LangChain, LangGraph, and various LLM providers.

Main components:
- assistants: Pre-built AI assistant workflows
- core: Core utilities (logger, system info, models)
- tools: Command-line tools and utilities
- models: LLM and embedding model initialization
"""

from __future__ import annotations

from ai_circus.data_model import get_env_config
from ai_circus.models import get_embeddings, get_llm

__version__ = "0.1.1"
__author__ = "Angel Martinez-Tenor"
__all__: list[str] = ["get_embeddings", "get_env_config", "get_llm"]
