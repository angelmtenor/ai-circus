"""
Document extraction module for the AI Circus project.
Author: Angel Martinez-Tenor, 2026.

Minimalist text extraction for plain-text formats (.md, .txt).
No heavy OCR or CV dependencies required — uses stdlib only.
"""

from __future__ import annotations

import re
from pathlib import Path

from langchain_core.documents import Document

from ai_circus.assistants.chunking import split_into_chunks
from ai_circus.core.logger import get_logger

# Module-level constants
CHUNK_SIZE: int = 5000  # Maximum characters per chunk
CHUNK_OVERLAP: int = 100  # Overlapping characters between chunks
SUPPORTED_EXTENSIONS: tuple[str, ...] = (".md", ".txt")

logger = get_logger(__name__)

# Each entry is (compiled_pattern, replacement_string)
_MD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"```.*?```", re.DOTALL), " "),  # fenced code blocks
    (re.compile(r"`[^`]+`"), " "),  # inline code
    (re.compile(r"^#{1,6}\s+", re.MULTILINE), ""),  # headings
    (re.compile(r"!\[.*?\]\(.*?\)"), " "),  # images
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"),  # links → keep label (1 group)
    (re.compile(r"(\*{1,2}|_{1,2})(.+?)\1"), r"\2"),  # bold/italic → keep text (2 groups)
    (re.compile(r"^[-*+]\s+", re.MULTILINE), ""),  # unordered list markers
    (re.compile(r"^\d+\.\s+", re.MULTILINE), ""),  # ordered list markers
    (re.compile(r"^>\s+", re.MULTILINE), ""),  # blockquotes
    (re.compile(r"^-{3,}$", re.MULTILINE), " "),  # horizontal rules
    (re.compile(r"\|.*?\|", re.MULTILINE), " "),  # table rows
]


def _strip_markdown(text: str) -> str:
    """Remove Markdown syntax, leaving plain readable text."""
    for pattern, replacement in _MD_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class DocumentExtractor:
    """Minimalist text extractor for .md and .txt files using stdlib only."""

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        """
        Split text into chunks with specified size and overlap.

        Args:
            text (str): Input text to chunk.
            chunk_size (int): Maximum characters per chunk.
            chunk_overlap (int): Overlapping characters between chunks.

        Returns:
            list[str]: List of text chunks.
        """
        text = " ".join(text.split())  # Normalize whitespace
        try:
            windows = split_into_chunks(text, chunk_size, chunk_overlap)
        except ValueError as e:
            logger.error(f"Invalid chunk parameters: size={chunk_size}, overlap={chunk_overlap}")
            raise ValueError(str(e)) from e
        return [content for _, _, content in windows if content.strip()]

    def extract_text(
        self,
        file_path: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        **kwargs: object,  # absorbs legacy strategy/languages args gracefully
    ) -> list[Document]:
        """
        Extract and chunk text from a .md or .txt file.

        Args:
            file_path (str): Path to the document file.
            chunk_size (int, optional): Maximum characters per chunk. Defaults to CHUNK_SIZE.
            chunk_overlap (int, optional): Overlapping characters between chunks. Defaults to CHUNK_OVERLAP.
            **kwargs: Ignored; kept for backwards-compatibility with callers that pass strategy/languages.

        Returns:
            list[Document]: List of Document objects containing the extracted text and metadata.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            logger.error(f"File not found or is not a file: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")
            raise ValueError(f"Unsupported file type: {ext}")

        chunk_size = chunk_size if chunk_size is not None else CHUNK_SIZE
        chunk_overlap = chunk_overlap if chunk_overlap is not None else CHUNK_OVERLAP

        try:
            logger.info(f"Extracting text from {file_path}")
            raw = path.read_text(encoding="utf-8", errors="replace")
            text = _strip_markdown(raw) if ext == ".md" else raw
            logger.debug(f"Extracted {len(text)} characters from {file_path}")

            chunks = self._chunk_text(text, chunk_size, chunk_overlap)
            base_metadata: dict[str, str] = {"source": file_path}

            documents = [
                Document(
                    page_content=chunk,
                    metadata={**base_metadata, "chunk_index": str(i), "total_chunks": str(len(chunks))},
                )
                for i, chunk in enumerate(chunks)
            ]
            logger.info(f"Extracted and chunked {len(documents)} Document objects from {file_path}")
            return documents

        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise ValueError(f"Failed to extract text: {e}") from e


if __name__ == "__main__":
    extractor = DocumentExtractor()
    sample_file = "scenarios/python_development/documents/15_software_engineering_principles.md"
    try:
        documents = extractor.extract_text(sample_file, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        logger.info(f"Extracted {len(documents)} Document objects")
        for i, doc in enumerate(documents[:5]):
            logger.info(f"Document {i + 1}:")
            logger.info(f"  Content (first 100 chars): {doc.page_content[:100]}...")
            logger.info(f"  Metadata: {doc.metadata}")
    except Exception as e:
        logger.error(f"Error: {e}")
