from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """Pydantic settings model to manage environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    openai_api_key: str
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> EnvSettings:
    return EnvSettings()
