"""Tests for intent detector graph helpers."""

from __future__ import annotations

from typing import Any, cast

from langchain_core.documents import Document

from ai_circus.assistants.intent_detector_graph import GraphState, process_llm_response, retriever_node


def test_process_llm_response_handles_fenced_json() -> None:
    """The JSON parser should accept fenced code blocks from model output."""
    content = '```json\n{"intent": "retrieve"}\n```'

    parsed = process_llm_response(content)

    assert parsed == {"intent": "retrieve"}


def test_retriever_node_uses_public_retriever_method() -> None:
    """The graph should use the public retriever boundary instead of a private method."""

    class FakeRetriever:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def invoke(self, query: str) -> list[Document]:
            self.calls.append(query)
            return [Document(page_content="doc-1"), Document(page_content="doc-2")]

    retriever = FakeRetriever()
    state = GraphState(
        user_input="original",
        intent_output={"intent": "retrieve", "reformulated_question": "normalized question"},
    )

    result = retriever_node(state, cast(Any, retriever))

    assert retriever.calls == ["normalized question"]
    assert result.retrieved_documents == ["doc-1", "doc-2"]
