"""
Agentic Assistant for Intent Detection and Document Retrieval.
Rewritten using OpenAI Agents SDK (agents-as-tools + handoffs pattern).
Author: Angel Martinez-Tenor, 2026.

Architecture:
  - OrchestratorAgent  → routes queries, manages conversation
  - IntentAgent        → classifies user intent via tool call
  - RetrieverAgent     → semantic search over document chunks
  - ResponseAgent      → synthesizes final answer with citations
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    function_tool,
    set_default_openai_api,
    set_tracing_disabled,
    trace,
)
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from ai_circus import get_env_config
from ai_circus.core.logger import configure_logger, get_logger

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL: str = "gpt-4o-mini"
EMBEDDING_MODEL: str = "text-embedding-3-small"
TOP_K_RETRIEVAL: int = 3
CHUNK_SIZE: int = 2000
CHUNK_OVERLAP: int = 50
SAMPLE_FILE_PATH: str = "scenarios/python_development/documents/15_software_engineering_principles.md"

logger = get_logger(__name__)


def configure_agents_runtime() -> None:
    """Configure the Agents SDK runtime for local execution."""
    set_tracing_disabled(True)
    set_default_openai_api("chat_completions")


# ---------------------------------------------------------------------------
# Pydantic schemas (structured outputs)
# ---------------------------------------------------------------------------


class IntentResult(BaseModel):
    """Result of intent detection classification."""

    intent: str = Field(description="One of: DOCUMENT_QUERY, CHIT_CHAT, OUT_OF_SCOPE, FOLLOW_UP")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class RetrievalResult(BaseModel):
    """Result of document retrieval with relevance scores."""

    chunks: list[str]
    sources: list[str]
    relevance_scores: list[float]


class FinalResponse(BaseModel):
    """Final response from the assistant with sources and confidence."""

    response: str
    intent: str
    sources_used: list[str]
    confidence: float


# ---------------------------------------------------------------------------
# In-process vector store (no external dependency)
# ---------------------------------------------------------------------------


class SimpleVectorStore:
    """Lightweight in-process vector store backed by OpenAI embeddings."""

    def __init__(self, embedding_model: str = EMBEDDING_MODEL) -> None:
        """Initialize the vector store with OpenAI client."""
        config = get_env_config()
        self._embedding_model = embedding_model
        api_key = config.OPENAI_API_KEY
        self._client = AsyncOpenAI(
            api_key=api_key.get_secret_value() if api_key else None,
        )
        self._texts: list[str] = []
        self._metadatas: list[dict] = []
        self._embeddings: list[list[float]] = []

    async def add_texts(self, texts: list[str], metadatas: list[dict]) -> None:
        """Add texts to the vector store with their metadata."""
        resp = await self._client.embeddings.create(
            model=self._embedding_model,
            input=texts,  # type: ignore[bad-argument-type]
        )
        self._texts = texts
        self._metadatas = metadatas
        self._embeddings = [e.embedding for e in resp.data]

    async def similarity_search(self, query: str, k: int = TOP_K_RETRIEVAL) -> list[dict]:
        """Search for similar texts using cosine similarity."""
        resp = await self._client.embeddings.create(
            model=self._embedding_model,
            input=[query],  # type: ignore[bad-argument-type]
        )
        q_vec = resp.data[0].embedding

        def cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b, strict=True))
            na = sum(x * x for x in a) ** 0.5
            nb = sum(x * x for x in b) ** 0.5
            return dot / (na * nb + 1e-9)

        scores = [cosine(q_vec, e) for e in self._embeddings]
        top = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
        return [
            {
                "text": self._texts[i],
                "metadata": self._metadatas[i],
                "score": round(s, 4),
            }
            for i, s in top
        ]


# ---------------------------------------------------------------------------
# Document loader
# ---------------------------------------------------------------------------


def load_and_chunk(
    file_path: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """Read a markdown/text file and split into overlapping chunks."""
    text = Path(file_path).read_text(encoding="utf-8")
    chunks: list[dict] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "page_content": text[start:end],
            "metadata": {
                "source": file_path,
                "chunk_index": idx,
                "start_char": start,
                "end_char": end,
            },
        })
        start += chunk_size - chunk_overlap
        idx += 1
    return chunks


# ---------------------------------------------------------------------------
# Shared runtime context (injected into every agent)
# ---------------------------------------------------------------------------


class AssistantContext(BaseModel):
    """Mutable context shared across all agents in a run."""

    model_config = {"arbitrary_types_allowed": True}

    vector_store: Any  # SimpleVectorStore — not Pydantic-serialisable
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    document_path: str = SAMPLE_FILE_PATH
    last_intent: str = ""
    last_retrieval: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Tools (reusable across agents)
# ---------------------------------------------------------------------------


@function_tool
async def detect_intent(ctx: RunContextWrapper[AssistantContext], user_query: str) -> str:
    """Classify the user's intent.

    Returns a JSON IntentResult with keys: intent, confidence, reasoning.
    Intent is one of: DOCUMENT_QUERY, CHIT_CHAT, OUT_OF_SCOPE, FOLLOW_UP.
    """
    config = get_env_config()
    api_key = config.OPENAI_API_KEY
    client = AsyncOpenAI(
        api_key=api_key.get_secret_value() if api_key else None,
    )
    completion = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an intent classifier. Classify the user's query as one of: "
                    "DOCUMENT_QUERY (wants info from a document), "
                    "CHIT_CHAT (casual conversation), "
                    "OUT_OF_SCOPE (unrelated to any document), "
                    "FOLLOW_UP (follow-up to a previous answer)."
                ),
            },
            {"role": "user", "content": user_query},
        ],
        response_format=IntentResult,
    )
    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("Failed to parse intent result")
    ctx.context.last_intent = result.intent
    return result.model_dump_json()


@function_tool
async def retrieve_documents(
    ctx: RunContextWrapper[AssistantContext],
    query: str,
    k: int = TOP_K_RETRIEVAL,
) -> str:
    """Perform semantic search over the loaded document chunks.

    Returns a JSON list of the top-k most relevant passages with scores.
    """
    hits = await ctx.context.vector_store.similarity_search(query, k=k)
    ctx.context.last_retrieval = hits
    return json.dumps(
        [{"text": h["text"][:400], "score": h["score"]} for h in hits],
        indent=2,
    )


@function_tool
def get_conversation_history(ctx: RunContextWrapper[AssistantContext]) -> str:
    """Return the current conversation history as JSON."""
    return json.dumps(ctx.context.conversation_history, indent=2)


@function_tool
def append_to_history(ctx: RunContextWrapper[AssistantContext], role: str, content: str) -> str:
    """Append a message to the conversation history. role must be 'user' or 'assistant'."""
    ctx.context.conversation_history.append({"role": role, "content": content})
    return f"History updated. Total turns: {len(ctx.context.conversation_history)}"


# ---------------------------------------------------------------------------
# Specialist agents
# ---------------------------------------------------------------------------

intent_agent = Agent[AssistantContext](
    name="IntentAgent",
    model=MODEL,
    instructions=(
        "You are a specialist at understanding what a user wants. "
        "Always call detect_intent with the user's query and return the result verbatim."
    ),
    tools=[detect_intent],
)

retriever_agent = Agent[AssistantContext](
    name="RetrieverAgent",
    model=MODEL,
    instructions=(
        "You retrieve relevant document passages. "
        "Call retrieve_documents with the user's query. "
        "Return the raw chunks so the response agent can synthesise an answer."
    ),
    tools=[retrieve_documents],
)

response_agent = Agent[AssistantContext](
    name="ResponseAgent",
    model=MODEL,
    instructions=(
        "You are a precise, helpful assistant. "
        "You receive a user query, retrieved document passages, and the detected intent. "
        "Synthesise a clear, grounded answer. Cite specific passages where relevant. "
        "If intent is CHIT_CHAT, respond conversationally without referencing documents. "
        "If OUT_OF_SCOPE, politely explain you can only answer questions about the loaded documents."
    ),
    tools=[get_conversation_history, append_to_history],
)

# ---------------------------------------------------------------------------
# Orchestrator (top-level agent with handoffs)
# ---------------------------------------------------------------------------

orchestrator_agent = Agent[AssistantContext](
    name="OrchestratorAgent",
    model=MODEL,
    instructions=(
        "You are the central coordinator. For every user query you MUST:\n"
        "1. Hand off to IntentAgent to classify the query.\n"
        "2. If intent is DOCUMENT_QUERY or FOLLOW_UP → hand off to RetrieverAgent.\n"
        "3. Hand off to ResponseAgent with full context (query + intent + retrieved chunks).\n"
        "4. Return the final answer from ResponseAgent to the user.\n"
        "Never answer directly without going through this pipeline."
    ),
    tools=[detect_intent, retrieve_documents, get_conversation_history, append_to_history],
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def build_assistant(
    file_path: str = SAMPLE_FILE_PATH,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    embedding_model: str = EMBEDDING_MODEL,
) -> AssistantContext:
    """Load documents, embed them, and return a ready AssistantContext.

    Args:
        file_path: Path to the markdown/text document to load.
        chunk_size: Character length of each chunk.
        chunk_overlap: Overlap between consecutive chunks.
        embedding_model: OpenAI embedding model to use.

    Returns:
        A populated AssistantContext ready for querying.
    """
    configure_agents_runtime()
    # NOTE: Do NOT set os.environ["OPENAI_API_KEY"] — SecretStr is passed directly to each client.

    try:
        logger.info(f"Loading document: {file_path}")
        chunks = load_and_chunk(file_path, chunk_size, chunk_overlap)
        logger.info(f"Extracted {len(chunks)} chunks from {file_path}")

        store = SimpleVectorStore(embedding_model=embedding_model)
        await store.add_texts(
            texts=[c["page_content"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
        )
        logger.info("Vector store populated with document chunks")
        return AssistantContext(vector_store=store, document_path=file_path)
    except Exception as e:
        logger.error(f"Failed to build assistant context from {file_path}: {e}")
        raise


async def ask(
    ctx: AssistantContext,
    query: str,
) -> FinalResponse:
    """Run a single query through the agentic pipeline.

    Args:
        ctx: The shared assistant context (holds vector store + history).
        query: The user's natural-language question.

    Returns:
        FinalResponse with response text, intent, sources, and confidence.
    """
    try:
        configure_agents_runtime()
        logger.debug(f"Processing query: {query[:50]}...")

        with trace("document-assistant"):
            result = await Runner.run(
                orchestrator_agent,
                input=query,
                context=ctx,
            )

        ctx.conversation_history.append({"role": "user", "content": query})
        ctx.conversation_history.append({"role": "assistant", "content": result.final_output})

        response = FinalResponse(
            response=result.final_output,
            intent=ctx.last_intent or "UNKNOWN",
            sources_used=[h["metadata"].get("source", "") for h in ctx.last_retrieval],
            confidence=max((h["score"] for h in ctx.last_retrieval), default=0.0),
        )

        logger.debug(f"Query processed successfully with intent: {response.intent}")
        return response

    except Exception as e:
        logger.error(f"Failed to process query '{query[:50]}...': {e}")
        raise


# ---------------------------------------------------------------------------
# Demo workflow
# ---------------------------------------------------------------------------


async def run_demo() -> None:
    """Run a multi-turn demo conversation."""
    logger.info("Starting agentic assistant demo")

    try:
        ctx = await build_assistant(SAMPLE_FILE_PATH)
        logger.info("Assistant context built successfully")

        conversations = [
            [
                "What is the DRY principle in software engineering?",
                "Give an example of violating DRY.",
            ],
            [
                "Hello! How are you today?",  # CHIT_CHAT
                "What about the SOLID principles?",  # DOCUMENT_QUERY
            ],
        ]

        for conv_idx, queries in enumerate(conversations, 1):
            logger.info(f"Starting conversation {conv_idx} with {len(queries)} queries")
            logger.info(f"Conversation {conv_idx}")
            ctx.conversation_history = []
            ctx.last_intent = ""
            ctx.last_retrieval = []

            for query_idx, query in enumerate(queries, 1):
                logger.debug(f"Conversation {conv_idx}, Query {query_idx}: Processing '{query[:50]}...'")
                logger.info(f"USER: {query}")
                response = await ask(ctx, query)
                logger.info(f"BOT: {response.response}")
                logger.info(
                    f"[intent={response.intent}  "
                    f"confidence={response.confidence:.2f}  "
                    f"sources={len(set(response.sources_used))}]"
                )

            logger.info(f"Completed conversation {conv_idx}")

        logger.info("All demo conversations completed successfully")

    except Exception as e:
        logger.critical(f"Demo failed: {e}")
        raise


def main() -> None:
    """Main entry point for the agentic assistant demo."""
    configure_logger(level="DEBUG")
    configure_agents_runtime()
    logger.info("Starting agentic assistant workflow")
    try:
        asyncio.run(run_demo())
        logger.info("Agentic assistant workflow completed successfully")
    except Exception as e:
        logger.critical(f"Agentic assistant workflow failed: {e}")
        raise


if __name__ == "__main__":
    main()
