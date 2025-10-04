"""Document ingestion pipeline for turning URLs into Milvus embeddings."""

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.url_selenium import SeleniumURLLoader
from loguru import logger
from pydantic import HttpUrl
from pymilvus.model.dense import OpenAIEmbeddingFunction

from api.core.config import get_settings
from api.core.vector_store import DocumentStore


class DocumentIngestionService:
    """
    High-level ingestion flow service for documents.

    Load -> clean -> split -> embed -> store
    """

    def __init__(self, urls: list[HttpUrl]):
        self.settings = get_settings()
        self.loader = SeleniumURLLoader(urls=[str(url) for url in urls])
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.embedding_fn = OpenAIEmbeddingFunction(
            model_name=self.settings.openai_embeddings_model,
            api_key=self.settings.openai_api_key,
        )
        self.store = DocumentStore()

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

    def _embed_documents(self, chunks: list[Document]) -> list[list[float]]:
        texts = [chunk.page_content for chunk in chunks]
        vectors = self.embedding_fn.encode_documents(texts)
        logger.info(f"Generated {len(vectors)} embeddings")
        return vectors

    def _store_embeddings(self, chunks: list[Document], embeddings: list[list[float]]):
        metadatas = []
        for idx, chunk in enumerate(chunks):
            metadata = dict(chunk.metadata)
            metadata["chunk_id"] = metadata.get("chunk_id", idx)
            metadatas.append(metadata)
        self.store.upsert(embeddings=embeddings, metadatas=metadatas)

    def run_pipeline(self):
        raw_docs = self._load_raw_documents()
        cleaned_docs = self._clean_documents(raw_docs)
        chunks = self._split_documents(cleaned_docs)
        embeddings = self._embed_documents(chunks)
        self._store_embeddings(chunks, embeddings)
