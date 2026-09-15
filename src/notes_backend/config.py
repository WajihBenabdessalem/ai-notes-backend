"""Configuration centralisée, chargée depuis les variables d'environnement."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Literal["openai", "anthropic"] = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    database_url: str = Field(default="sqlite:///./data/notes.db", alias="DATABASE_URL")
    top_k: int = Field(default=3, alias="TOP_K")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")


@lru_cache
def get_settings() -> Settings:
    return Settings()
