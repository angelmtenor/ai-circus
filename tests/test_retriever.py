"""Tests for the FAISS-backed Retriever.

Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

import pytest
from langchain_core.documents import Document

import ai_circus.assistants.retriever as retriever_module
from ai_circus.assistants.retriever import Retriever


class FakeVectorStore:
    """Minimal FAISS stand-in that records added documents without building a real index."""

    def __init__(self) -> None:
        """Seed a fake placeholder entry, mirroring FAISS.from_texts(["placeholder"], ...)."""
        self.index_to_docstore_id = {0: "placeholder-id"}
        self.deleted: list[str] = []
        self.documents: list[Document] = []

    @classmethod
    def from_texts(cls, texts: list[str], embeddings: object) -> FakeVectorStore:
        """Mimic FAISS.from_texts by returning a fresh fake store."""
        return cls()

    def delete(self, ids: list[str]) -> None:
        """Record deleted ids."""
        self.deleted.extend(ids)

    def add_documents(self, documents: list[Document]) -> None:
        """Record added documents."""
        self.documents.extend(documents)

    def as_retriever(self, search_kwargs: dict[str, int]) -> object:
        """Return an object whose invoke() returns the first k stored documents."""
        docs = self.documents[: search_kwargs["k"]]

        class _SubRetriever:
            def invoke(self, query: str) -> list[Document]:
                return docs

        return _SubRetriever()


@pytest.fixture(autouse=True)
def fake_faiss(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch FAISS with an in-memory stand-in so no real embeddings/index are built."""
    monkeypatch.setattr(retriever_module, "FAISS", FakeVectorStore)


def make_retriever(**kwargs: object) -> Retriever:
    """Build a Retriever with a dummy embeddings object (never called by FakeVectorStore)."""
    return Retriever(embeddings=object(), **kwargs)


def test_init_removes_placeholder_document() -> None:
    """The constructor should clean up the dummy placeholder document used to init FAISS."""
    retriever = make_retriever()

    assert retriever.vectorstore.deleted == ["placeholder-id"]


def test_add_texts_requires_matching_metadata_length() -> None:
    """add_texts should reject mismatched texts/metadatas lengths."""
    retriever = make_retriever()

    with pytest.raises(ValueError, match="must match"):
        retriever.add_texts(["a", "b"], metadatas=[{"source": "x"}])


def test_add_texts_populates_vectorstore_and_hybrid_documents() -> None:
    """add_texts should add documents to the vectorstore, and to .documents when hybrid=True."""
    retriever = make_retriever(hybrid=True)

    retriever.add_texts(["a", "b"], metadatas=[{"source": "x"}, {"source": "y"}])

    assert [d.page_content for d in retriever.vectorstore.documents] == ["a", "b"]
    assert [d.page_content for d in retriever.documents] == ["a", "b"]


def test_retrieve_returns_empty_list_for_blank_query() -> None:
    """retrieve() should short-circuit on empty/whitespace-only queries."""
    retriever = make_retriever()

    assert retriever.retrieve("   ") == []


def test_retrieve_uses_default_k_and_returns_documents() -> None:
    """retrieve() should query the vectorstore with default_k when k is not given."""
    retriever = make_retriever(default_k=1)
    retriever.add_texts(["a", "b"])

    results = retriever.retrieve("query")

    assert len(results) == 1


def test_get_relevant_documents_delegates_to_retrieve() -> None:
    """The BaseRetriever hook should delegate to retrieve()."""
    retriever = make_retriever()
    retriever.add_texts(["only text"])

    docs = retriever._get_relevant_documents("query")

    assert [d.page_content for d in docs] == ["only text"]
