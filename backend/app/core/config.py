from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，统一读取 .env/.env.local."""

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="movie-recommender-backend", alias="APP_NAME")
    environment: Literal["dev", "prod", "test"] = Field(default="dev", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # 数据库
    database_url: str = Field(default="postgresql://user:password@localhost:5432/movie_db", alias="DATABASE_URL")

    # 向量库（优先使用 Qdrant，其次 Pinecone）
    qdrant_url: Optional[AnyHttpUrl] = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")

    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_index: Optional[str] = Field(default=None, alias="PINECONE_INDEX")
    pinecone_environment: Optional[str] = Field(default=None, alias="PINECONE_ENVIRONMENT")

    # LLM / Embedding
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_api_base_url: Optional[AnyHttpUrl] = Field(default=None, alias="OPENAI_API_BASE_URL")

    # TMDB
    tmdb_api_key: Optional[str] = Field(default=None, alias="TMDB_API_KEY")
    tmdb_api_base: AnyHttpUrl = Field(
        default="https://api.themoviedb.org/3",
        alias="TMDB_API_BASE",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

