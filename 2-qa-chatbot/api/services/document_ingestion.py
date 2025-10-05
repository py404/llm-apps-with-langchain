"""Document ingestion pipeline for turning URLs into Milvus embeddings."""

from __future__ import annotations

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.url_selenium import SeleniumURLLoader
from langchain_milvus import Milvus
from langchain_openai.embeddings import OpenAIEmbeddings
from loguru import logger
from pydantic import HttpUrl

from api.core.config import get_settings


class DocumentIngestionService:
    """Ingestion flow service for documents."""

    def __init__(self, urls: list[HttpUrl]):
        self.settings = get_settings()
        self.loader = SeleniumURLLoader(urls=[str(url) for url in urls])
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.embeddings = OpenAIEmbeddings(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_embeddings_model,
        )
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=self.settings.milvus_collection,
            connection_args={"uri": self.settings.milvus_uri},
            auto_id=True,
        )

    def _load_raw_documents(self) -> list[Document]:
        docs = self.loader.load()
        logger.info(f"Loaded {len(docs)} documents from {len(self.loader.urls)} URLs")
        return docs

    def _clean_documents(self, docs: list[Document]) -> list[Document]:
        # TODO: perform HTML cleanup / boilerplate removal / dedupe.
        return docs

    def _split_documents(self, docs: list[Document]) -> list[Document]:
        chunks = self.text_splitter.split_documents(docs)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks

    def _persist_chunks(self, chunks: list[Document]) -> None:
        if not chunks:
            return

        prepared_chunks: list[Document] = []
        for idx, chunk in enumerate(chunks):
            metadata = dict(chunk.metadata)
            metadata.setdefault("chunk_id", idx)
            metadata.setdefault("source", metadata.get("url"))
            chunk.metadata = metadata
            prepared_chunks.append(chunk)

        self.vector_store.add_documents(prepared_chunks)
        logger.info(f"Persisted {len(prepared_chunks)} chunks to Milvus")

    def run_pipeline(self) -> None:
        raw_docs = self._load_raw_documents()
        cleaned_docs = self._clean_documents(raw_docs)
        chunks = self._split_documents(cleaned_docs)
        self._persist_chunks(chunks)
