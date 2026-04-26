"""
Retriever module for indexing and querying documents using FAISS.
Author: Angel Martinez-Tenor, 2026.
"""

from __future__ import annotations

from typing import Any, Literal

from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import PrivateAttr

from ai_circus.core.logger import get_logger
from ai_circus.models import get_embeddings

logger = get_logger(__name__)


class Retriever(BaseRetriever):
    """Retriever class for indexing and querying documents using FAISS, with optional hybrid BM25 retrieval."""

    _embeddings: Embeddings = PrivateAttr()
    _hybrid: bool = PrivateAttr()
    _default_k: int = PrivateAttr()
    _vectorstore: FAISS = PrivateAttr()
    _documents: list[Document] = PrivateAttr(default_factory=list)

    @property
    def embeddings(self) -> Embeddings:
        """Return the embeddings instance."""
        return self._embeddings

    @property
    def hybrid(self) -> bool:
        """Return whether hybrid retrieval is enabled."""
        return self._hybrid

    @property
    def default_k(self) -> int:
        """Return the default number of documents to retrieve."""
        return self._default_k

    @property
    def vectorstore(self) -> FAISS:
        """Return the FAISS vectorstore."""
        return self._vectorstore

    @property
    def documents(self) -> list[Document]:
        """Return the list of documents for hybrid retrieval."""
        return self._documents

    def __init__(
        self,
        embeddings: Embeddings | None = None,
        model_choice: Literal["openai", "google"] = "openai",
        hybrid: bool = False,
        default_k: int = 4,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the retriever with embeddings and FAISS vector store.

        Args:
            embeddings (Embeddings, optional): Embeddings object to use. If None, created based on model_choice.
            model_choice (Literal["openai", "google"], optional): Model for embeddings if embeddings is None.
                Defaults to "openai".
            hybrid (bool, optional): Whether to use hybrid retrieval with BM25. Defaults to False.
            default_k (int, optional): Default number of documents to retrieve. Defaults to 4.
            **kwargs: Additional keyword arguments passed to BaseRetriever.
        """
        super().__init__(**kwargs)
        if embeddings is None:
            self._embeddings = get_embeddings(model_choice)
        else:
            self._embeddings = embeddings

        self._hybrid = hybrid
        self._default_k = default_k

        # Initialize empty FAISS index without texts
        self._vectorstore = FAISS.from_texts([""], self._embeddings)
        self._vectorstore.delete([self._vectorstore.index_to_docstore_id[0]])  # Remove dummy document

        if hybrid:
            self._documents = []

        logger.info(
            f"Retriever initialized with model: {model_choice if embeddings is None else 'custom'}, "
            f"vector_db: faiss, hybrid: {hybrid}"
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> None:
        """
        Add a list of texts to the FAISS vector store and, if hybrid, to the documents list.

        Args:
            texts (list[str]): List of text documents to add.
            metadatas (list[dict], optional): List of metadata dictionaries for each text.
        """
        if not texts:
            logger.warning("No texts provided to add_texts")
            return

        if metadatas is None:
            metadatas = [{}] * len(texts)
        if len(texts) != len(metadatas):
            raise ValueError(f"Length of texts ({len(texts)}) must match metadatas ({len(metadatas)})")

        documents = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas, strict=True)]
        self.vectorstore.add_documents(documents)
        if self.hybrid:
            self.documents.extend(documents)
        logger.info(f"Added {len(texts)} texts to the FAISS vector store")

    def retrieve(self, query: str, k: int = 4) -> list[Document]:
        """
        Retrieve the top k relevant documents for the given query.

        Args:
            query (str): The query string.
            k (int, optional): Number of documents to retrieve. Defaults to 4.

        Returns:
            list[Document]: List of relevant documents.
        """
        if not query.strip():
            logger.warning("Empty query provided")
            return []

        if self.hybrid:
            vector_retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})

            return vector_retriever.invoke(query)
        else:
            return self.vectorstore.as_retriever(search_kwargs={"k": k}).invoke(query)

    def get_relevant_documents(self, query: str) -> list[Document]:
        """Return relevant documents using the retriever's default configuration."""
        return self.retrieve(query, k=self.default_k)

    def _get_relevant_documents(self, query: str, *, run_manager: object | None = None) -> list[Document]:
        """
        Implement abstract retrieval method required by BaseRetriever.

        Args:
            query (str): The query string.
            run_manager (object, optional): Run manager for tracking. Defaults to None.

        Returns:
            list[Document]: List of relevant documents.
        """
        return self.get_relevant_documents(query)


if __name__ == "__main__":
    # Example usage for testing
    sample_texts = [
        "Python is a versatile programming language.",
        "Java is used for enterprise applications.",
    ]

    # Test with FAISS
    retriever_faiss = Retriever()
    retriever_faiss.add_texts(sample_texts)
    query = "programming language"
    results = retriever_faiss.retrieve(query)
    for i, doc in enumerate(results):
        logger.info(f"FAISS Result {i + 1}: {doc.page_content[:100]}...")

    # Test with hybrid retrieval (using FAISS)
    retriever_hybrid = Retriever(hybrid=True)
    retriever_hybrid.add_texts(sample_texts)
    results = retriever_hybrid.retrieve(query)
    for i, doc in enumerate(results):
        logger.info(f"Hybrid Result {i + 1}: {doc.page_content[:100]}...")
