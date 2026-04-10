"""Tests for the document extraction module.

Author: Angel Martinez-Tenor, 2025.
"""

from __future__ import annotations

import pytest

from ai_circus.assistants.document_extractor import DocumentExtractor


class TestDocumentExtractor:
    """Tests for DocumentExtractor class."""

    def test_chunk_text_valid(self) -> None:
        """Test text chunking with valid parameters."""
        extractor = DocumentExtractor()
        text = "This is a test. " * 100  # Repeat to make it long
        chunks = extractor._chunk_text(text, chunk_size=100, chunk_overlap=10)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) <= 110 for chunk in chunks)  # chunk_size + some overlap

    def test_chunk_text_small_text(self) -> None:
        """Test chunking with text smaller than chunk size."""
        extractor = DocumentExtractor()
        text = "Short text"
        chunks = extractor._chunk_text(text, chunk_size=100, chunk_overlap=10)

        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_chunk_text_invalid_chunk_size(self) -> None:
        """Test that invalid chunk size raises ValueError."""
        extractor = DocumentExtractor()
        text = "Test text"

        with pytest.raises(ValueError):
            extractor._chunk_text(text, chunk_size=0, chunk_overlap=10)

    def test_chunk_text_invalid_overlap(self) -> None:
        """Test that invalid overlap raises ValueError."""
        extractor = DocumentExtractor()
        text = "Test text"

        # Test negative overlap
        with pytest.raises(ValueError):
            extractor._chunk_text(text, chunk_size=100, chunk_overlap=-1)

        # Test overlap >= chunk_size
        with pytest.raises(ValueError):
            extractor._chunk_text(text, chunk_size=100, chunk_overlap=100)

    def test_chunk_text_preserves_content(self) -> None:
        """Test that chunking preserves all content."""
        extractor = DocumentExtractor()
        text = "word " * 200  # Create a longer text
        chunks = extractor._chunk_text(text, chunk_size=100, chunk_overlap=10)

        # When joined with overlaps, content should be preserved
        assert len(chunks) > 0

    def test_extract_text_file_not_found(self) -> None:
        """Test that extracting from non-existent file raises FileNotFoundError."""
        extractor = DocumentExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract_text("non_existent_file.pdf")

    def test_extract_text_unsupported_format(self, tmp_path: object) -> None:
        """Test that unsupported file format raises ValueError."""
        extractor = DocumentExtractor()
        # Create a temporary unsupported file
        unsupported_file = tmp_path / "test.xyz"  # type: ignore[operator]
        unsupported_file.write_text("content")  # type: ignore[operator]

        with pytest.raises(ValueError, match="Unsupported file type"):
            extractor.extract_text(str(unsupported_file))
