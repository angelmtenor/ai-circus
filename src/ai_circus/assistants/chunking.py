"""Shared character-based chunking primitive for the assistant demos.

Both the LangGraph demo (document_extractor.py) and the OpenAI Agents SDK demo
(sample_agentic_assistant.py) need to split raw text into overlapping windows;
this module holds that one splitting algorithm so it isn't reimplemented twice.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations


def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[tuple[int, int, str]]:
    """Split text into overlapping (start_char, end_char, content) windows.

    Args:
        text: Input text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlapping characters between consecutive chunks.

    Returns:
        A list of (start_char, end_char, content) tuples covering the text left to right.

    Raises:
        ValueError: If chunk_size is not positive, or overlap is negative or >= chunk_size.
    """
    if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_size must be positive, and chunk_overlap must be non-negative and less than chunk_size")

    chunks: list[tuple[int, int, str]] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append((start, end, text[start:end]))
        start += chunk_size - chunk_overlap
    return chunks
