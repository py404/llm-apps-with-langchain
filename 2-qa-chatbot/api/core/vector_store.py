"""Milvus Lite adapter used for storing and retrieving document embeddings"""

from collections.abc import Iterable
from typing import Any

from core.config import get_settings
from loguru import logger
from pymilvus import MilvusClient


class DocumentStore:
    """Milvus DB interface for collection management and inserting embeddings"""

    def __init__(self, collection_name: str | None = None):
        settings = get_settings()
        self.collection_name = collection_name or settings.milvus_collection
        self.client = MilvusClient(uri=settings.milvus_uri)

        if not self.client.has_collection(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=settings.milvus_vector_dim,
            )

    def upsert(
        self, *, embeddings: Iterable[list[float]], metadatas: list[dict[str, Any]]
    ):
        payload = []
        for idx, (vector, metadata) in enumerate(
            zip(embeddings, metadatas, strict=True)
        ):
            payload.append(
                {
                    "id": metadata.get("chunk_id", idx),
                    "vector": vector,
                    **metadata,
                }
            )

        result = self.client.insert(collection_name=self.collection_name, data=payload)
        logger.debug("Milvus insert result: {}", result)
        return result
