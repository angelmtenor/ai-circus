"""Shared configuration for the two assistant demos (LangGraph and OpenAI Agents SDK).

Both sample_assistant.py and sample_agentic_assistant.py build the same "document
Q&A" demo on different frameworks; this module holds the values they'd otherwise
each redefine, so the two stay in sync instead of drifting apart.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

from ai_circus.models import DEFAULT_EMBEDDING_MODEL_GOOGLE, DEFAULT_EMBEDDING_MODEL_OPENAI

SAMPLE_FILE_PATH: str = "scenarios/python_development/documents/15_software_engineering_principles.md"

# Smaller than DocumentExtractor's library defaults (5000/100): tuned for fast interactive demos.
CHUNK_SIZE: int = 2000
CHUNK_OVERLAP: int = 50

# The OpenAI-compatible embeddings endpoint (used directly by the Agents SDK demo) expects a bare
# model id, unlike langchain_google_genai which requires the "models/" prefix.
GOOGLE_EMBEDDING_MODEL_RAW: str = DEFAULT_EMBEDDING_MODEL_GOOGLE.removeprefix("models/")
OPENAI_EMBEDDING_MODEL: str = DEFAULT_EMBEDDING_MODEL_OPENAI
