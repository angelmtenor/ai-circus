"""Tests for the sample assistant workflow helpers."""

from __future__ import annotations

from langchain_core.documents import Document

import ai_circus.assistants.sample_assistant as sample_assistant


def test_extract_document_chunks_returns_serializable_chunks(monkeypatch: object) -> None:
    """The extractor wrapper should convert Document objects into plain dictionaries."""

    class FakeExtractor:
        def extract_text(self, *args: object, **kwargs: object) -> list[Document]:
            return [Document(page_content="chunk-a", metadata={"source": "doc.md"})]

    monkeypatch.setattr(sample_assistant, "DocumentExtractor", FakeExtractor)

    chunks = sample_assistant.extract_document_chunks("doc.md", 100, 10)

    assert list(chunks) == [{"page_content": "chunk-a", "metadata": {"source": "doc.md"}}]


def test_initialize_document_retriever_populates_retriever(monkeypatch: object) -> None:
    """The sample wrapper should pass texts and metadata into the retriever."""
    captured: dict[str, object] = {}

    class FakeRetriever:
        def __init__(self, **kwargs: object) -> None:
            captured["init"] = kwargs

        def add_texts(self, texts: list[str], metadatas: list[dict[str, object]]) -> None:
            captured["texts"] = texts
            captured["metadatas"] = metadatas

    monkeypatch.setattr(sample_assistant, "Retriever", FakeRetriever)

    retriever = sample_assistant.initialize_document_retriever([
        {"page_content": "chunk-a", "metadata": {"source": "doc.md"}}
    ])

    assert isinstance(retriever, FakeRetriever)
    assert captured["init"] == {"default_k": 2}
    assert captured["texts"] == ["chunk-a"]
    assert captured["metadatas"] == [{"source": "doc.md"}]


def test_process_user_query_returns_response_and_history() -> None:
    """The graph wrapper should normalize the returned state into its tuple contract."""

    class FakeGraph:
        def invoke(self, state: object) -> dict[str, object]:
            return {
                "user_input": "What is DRY?",
                "history": [{"user": "What is DRY?", "assistant": "Do not repeat yourself."}],
                "intent_output": {"intent": "retrieve"},
                "response_output": {"response": "Do not repeat yourself."},
                "retrieved_documents": ["doc-a"],
            }

    response, history, intent_output, response_output = sample_assistant.process_user_query(
        graph=FakeGraph(),
        query="What is DRY?",
        conversation_history=[],
        document_path="doc.md",
        chunk_index=0,
    )

    assert response == "Do not repeat yourself."
    assert history == [{"user": "What is DRY?", "assistant": "Do not repeat yourself."}]
    assert intent_output == {"intent": "retrieve"}
    assert response_output == {"response": "Do not repeat yourself."}


def test_main_configures_logging_before_running_workflow(monkeypatch: object) -> None:
    """Running the sample entrypoint should configure logging explicitly."""
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(sample_assistant, "configure_logger", lambda **kwargs: calls.append(("configure", kwargs)))
    monkeypatch.setattr(sample_assistant, "run_assistant_workflow", lambda: calls.append(("run", None)))

    sample_assistant.main()

    assert calls == [("configure", {"level": "DEBUG"}), ("run", None)]
