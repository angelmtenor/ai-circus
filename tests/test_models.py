"""Tests for the models module (LLM and embedding initialization).

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import pytest

from ai_circus import get_embeddings, get_llm


class TestLLMInitialization:
    """Tests for LLM initialization."""

    def test_get_llm_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test OpenAI LLM initialization."""
        captured: dict[str, object] = {}

        class FakeChatOpenAI:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr("ai_circus.models.ChatOpenAI", FakeChatOpenAI)

        llm = get_llm(provider="openai", model="gpt-4o", temperature=0.7)

        assert isinstance(llm, FakeChatOpenAI)
        assert captured["model"] == "gpt-4o"
        assert captured["temperature"] == pytest.approx(0.7)

    def test_get_llm_google(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Google LLM initialization."""
        captured: dict[str, object] = {}

        class FakeChatGoogle:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr("ai_circus.models.ChatGoogleGenerativeAI", FakeChatGoogle)

        llm = get_llm(provider="google", model="gemini-1.5-pro")

        assert isinstance(llm, FakeChatGoogle)
        assert captured["model"] == "gemini-1.5-pro"


class TestEmbeddingsInitialization:
    """Tests for Embeddings initialization."""

    def test_get_embeddings_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test OpenAI embeddings initialization."""
        captured: dict[str, object] = {}

        class FakeOpenAIEmbeddings:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr("ai_circus.models.OpenAIEmbeddings", FakeOpenAIEmbeddings)

        get_embeddings(provider="openai", model="text-embedding-3-large")
        assert captured["model"] == "text-embedding-3-large"

    def test_get_embeddings_google(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Google embeddings initialization."""
        captured: dict[str, object] = {}

        class FakeGoogleEmbeddings:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        monkeypatch.setattr("ai_circus.models.GoogleGenerativeAIEmbeddings", FakeGoogleEmbeddings)

        get_embeddings(provider="google", model="models/text-embedding-004")
        assert captured["model"] == "models/text-embedding-004"
