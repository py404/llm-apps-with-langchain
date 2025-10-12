"""
Load and validate application configuration from environment variables.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Fill in defaults only for non-sensitive values. Secrets should be required (no default)
    so missing env vars fail fast.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Required (no default) - treated as a secret in production
    OPENAI_API_KEY: str = Field(
        ..., description="OpenAI API key used for embeddings/LLM"
    )

    # Embeddings
    OPENAI_EMBEDDING_MODEL: str = Field(
        "text-embedding-3-small",
        description="Default embedding model name (OpenAI or provider-specific)",
    )
    EMBEDDING_BATCH_SIZE: int = Field(
        128, description="Batch size when calling embed_documents"
    )

    # Milvus Lite (vector store)
    MILVUS_URI: str = Field("milvus.db", description="Milvus URI for local Milvus Lite")
    MILVUS_COLLECTION: str = Field(
        "search_doc_chunks",
        description="Milvus collection name to use for chunk vectors",
    )
    MILVUS_VECTOR_DIM: int = Field(1536, description="Milvus vector dimension")

    # Log level
    LOG_LEVEL: str = Field("INFO", description="Logging level for the application")


@lru_cache(maxsize=1)
def get_settings() -> EnvSettings:
    """Return cached settings instance to avoid repeated env parsing."""

    return EnvSettings()
