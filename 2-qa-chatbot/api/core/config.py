"""Configuration helpers for the QA chatbot services layer."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """Environment-driven configuration for pipelines and adapters."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI
    openai_api_key: str
    openai_embeddings_model: str = "text-embedding-3-small"

    # Document splitting
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Milvus Lite
    milvus_uri: str = "milvus.db"
    milvus_collection: str = "qa_chunks"
    milvus_vector_dim: int = 1536  # match embedding model output


@lru_cache
def get_settings() -> EnvSettings:
    """Return cached settings instance to avoid repeated env parsing."""

    return EnvSettings()
