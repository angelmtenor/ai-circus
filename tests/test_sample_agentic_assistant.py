"""Tests for the agentic sample assistant helpers."""

from __future__ import annotations

import asyncio
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

import ai_circus.assistants.sample_agentic_assistant as sample_agentic


def test_load_and_chunk_splits_text_with_metadata(tmp_path: object) -> None:
    """The chunk loader should preserve source metadata and overlap positions."""
    file_path = tmp_path / "doc.md"
    file_path.write_text("abcdefghij", encoding="utf-8")

    chunks = sample_agentic.load_and_chunk(str(file_path), chunk_size=4, chunk_overlap=1)

    assert [chunk["page_content"] for chunk in chunks] == ["abcd", "defg", "ghij", "j"]
    assert chunks[0]["metadata"]["source"] == str(file_path)
    assert chunks[1]["metadata"]["start_char"] == 3


@pytest.mark.asyncio
async def test_build_assistant_creates_context_with_vector_store(monkeypatch: object) -> None:
    """Building the agentic assistant should load chunks and populate the vector store."""
    recorded: dict[str, object] = {}

    class FakeSecret:
        def get_secret_value(self) -> str:
            return "sk-test-12345678901234567890"

    class FakeEnvConfig:
        OPENAI_API_KEY = FakeSecret()

    class FakeVectorStore:
        def __init__(self, embedding_model: str) -> None:
            recorded["embedding_model"] = embedding_model

        async def add_texts(self, texts: list[str], metadatas: list[dict[str, object]]) -> None:
            await asyncio.sleep(0)
            recorded["texts"] = texts
            recorded["metadatas"] = metadatas

    monkeypatch.setattr(sample_agentic, "get_env_config", lambda: FakeEnvConfig())
    monkeypatch.setattr(sample_agentic, "configure_agents_runtime", lambda: recorded.setdefault("configured", True))
    monkeypatch.setattr(sample_agentic, "SimpleVectorStore", FakeVectorStore)
    monkeypatch.setattr(
        sample_agentic,
        "load_and_chunk",
        lambda *args, **kwargs: [{"page_content": "chunk-a", "metadata": {"source": "doc.md"}}],
    )

    context = await sample_agentic.build_assistant(file_path="doc.md", embedding_model="embed-model")

    assert recorded["configured"] is True
    assert recorded["embedding_model"] == "embed-model"
    assert recorded["texts"] == ["chunk-a"]
    assert context.document_path == "doc.md"


@pytest.mark.asyncio
async def test_ask_returns_final_response_and_updates_history(monkeypatch: object) -> None:
    """The ask helper should adapt Runner output into FinalResponse."""
    recorded: list[str] = []

    async def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        await asyncio.sleep(0)
        return SimpleNamespace(final_output="Grounded answer")

    monkeypatch.setattr(sample_agentic, "configure_agents_runtime", lambda: recorded.append("configured"))
    monkeypatch.setattr(sample_agentic, "trace", lambda name: nullcontext())
    monkeypatch.setattr(sample_agentic.Runner, "run", fake_run)

    context = sample_agentic.AssistantContext(
        vector_store=object(),
        last_intent="DOCUMENT_QUERY",
        last_retrieval=[{"metadata": {"source": "doc.md"}, "score": 0.9}],
    )

    response = await sample_agentic.ask(context, "What is DRY?")

    assert recorded == ["configured"]
    assert response.response == "Grounded answer"
    assert response.intent == "DOCUMENT_QUERY"
    assert response.sources_used == ["doc.md"]
    assert response.confidence == pytest.approx(0.9)
    assert context.conversation_history == [
        {"role": "user", "content": "What is DRY?"},
        {"role": "assistant", "content": "Grounded answer"},
    ]


def test_main_configures_runtime_before_running_demo(monkeypatch: object) -> None:
    """The agentic sample entrypoint should configure logging and SDK runtime explicitly."""
    calls: list[tuple[str, object]] = []

    def fake_asyncio_run(coroutine: object) -> None:
        calls.append(("asyncio.run", coroutine.cr_code.co_name))
        coroutine.close()

    monkeypatch.setattr(sample_agentic, "configure_logger", lambda **kwargs: calls.append(("configure_logger", kwargs)))
    monkeypatch.setattr(
        sample_agentic, "configure_agents_runtime", lambda: calls.append(("configure_agents_runtime", None))
    )
    monkeypatch.setattr(sample_agentic.asyncio, "run", fake_asyncio_run)

    sample_agentic.main()

    assert calls[0] == ("configure_logger", {"level": "DEBUG"})
    assert calls[1] == ("configure_agents_runtime", None)
    assert calls[2] == ("asyncio.run", "run_demo")
