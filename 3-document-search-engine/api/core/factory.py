"""
Factory for vector store, retriever, and embeddings.

Implements a Milvus Lite vector store via LangChain community integrations
and OpenAI embeddings. Keeps construction concerns centralized.
"""

from abc import ABC, abstractmethod
from typing import Any

import structlog
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings

from api.core.config import EnvSettings

logger = structlog.get_logger(__name__)


class VectorStoreFactory(ABC):
    """Abstract factory interface for creating vector stores, retrievers and embeddings."""

    @abstractmethod
    def create_vector_store(self, collection_name: str) -> Any:
        """Create a vector store instance (with Milvus).

        Args:
            collection_name (str): The name of the collection to use for vector storage.

        Returns:
            Any: The created vector store instance.
        """
        raise NotImplementedError

    @abstractmethod
    def create_retriever(self, vector_store: Any, k: int = 5) -> Any:
        """Create a retriever for querying the vector store.

        Args:
            vector_store: Milvus vector store instance.
            k: Number of top results to retrieve.

        Returns:
            Any: Configured retriever instance.
        """
        raise NotImplementedError

    @abstractmethod
    def create_embeddings(self) -> OpenAIEmbeddings:
        """Create an embeddings instance for semantic vectorization.

        Returns:
            OpenAIEmbeddings: Configured embeddings instance (e.g., text-embedding-3-small).
        """
        raise NotImplementedError


class MilvusVectorStoreFactory(VectorStoreFactory):
    """Concrete factory for Milvus-based vector stores, retrievers, and embeddings."""

    def __init__(self, settings: EnvSettings):
        """Initialize factory with app settings.

        Args:
            settings: Application settings (e.g., API keys, Milvus URI) from Singleton config.
        """
        self.settings = settings
        logger.info("factory.init", provider="milvus", uri=self.settings.MILVUS_URI)

    def create_vector_store(self, collection_name: str) -> Milvus:
        """Create a Milvus Lite vector store instance for indexing document embeddings."""
        logger.info(
            "factory.vector_store.create", collection=collection_name, uri=self.settings.MILVUS_URI
        )
        try:
            embeddings = self.create_embeddings()
            vector_store = Milvus(
                embedding_function=embeddings,
                connection_args={"uri": self.settings.MILVUS_URI},
                collection_name=collection_name,
            )
            logger.info("factory.vector_store.ready", collection=collection_name)
            return vector_store
        except Exception as e:
            logger.exception("factory.vector_store.error", err=str(e))
            raise

    def create_retriever(self, vector_store: Any, k: int = 5) -> Any:
        """Create a retriever for querying document embeddings."""
        logger.info("factory.retriever.create", k=k)
        try:
            retriever = vector_store.as_retriever(search_kwargs={"k": k})
            logger.info("factory.retriever.ready", k=k)
            return retriever
        except Exception as e:
            logger.exception("factory.retriever.error", err=str(e))
            raise

    def create_embeddings(self) -> OpenAIEmbeddings:
        """Create an OpenAI embeddings instance for semantic vectorization."""
        logger.info("factory.embeddings.create", model=self.settings.OPENAI_EMBEDDING_MODEL)
        try:
            embeddings = OpenAIEmbeddings(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_EMBEDDING_MODEL,
            )
            logger.info("factory.embeddings.ready", model=self.settings.OPENAI_EMBEDDING_MODEL)
            return embeddings
        except Exception as e:
            logger.exception("factory.embeddings.error", err=str(e))
            raise


def get_vector_store_factory(settings: EnvSettings) -> VectorStoreFactory:
    """Factory method to create a vector store factory instance.

    Args:
        settings: Optional settings; defaults to singleton Settings instance.

    Returns:
        VectorStoreFactory: Configured factory instance for Milvus components.
    """
    return MilvusVectorStoreFactory(settings)
