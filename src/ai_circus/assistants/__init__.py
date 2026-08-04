"""Assistants module for AI Circus.

This module provides pre-built AI assistant workflows and components including:
- Document extraction and retrieval
- Intent detection using LangGraph
- Sample assistant for interactive conversations (LangGraph and OpenAI Agents SDK)
"""

from __future__ import annotations

from ai_circus.assistants.document_extractor import DocumentExtractor
from ai_circus.assistants.intent_detector_graph import build_graph
from ai_circus.assistants.retriever import Retriever
from ai_circus.assistants.sample_agentic_assistant import run_demo
from ai_circus.assistants.sample_assistant import run_assistant_workflow

__all__ = [
    "DocumentExtractor",
    "Retriever",
    "build_graph",
    "run_assistant_workflow",
    "run_demo",
]
