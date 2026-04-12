import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，统一读取 .env/.env.local"""

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用基础配置
    app_name: str = Field(default="movie-recommender-backend", alias="APP_NAME")
    environment: Literal["dev", "prod", "test"] = Field(default="dev", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # 数据库配置
    database_url: str = Field(default="postgresql://postgres:356921@localhost:5432/movie_recommendation", alias="DATABASE_URL")
    
    # 数据库连接配置
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="movie_recommendation", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="356921", alias="DB_PASSWORD")

    # 向量数据库配置（优先使用 Qdrant，其次 Pinecone）
    qdrant_url: Optional[AnyHttpUrl] = Field(default=None, alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_index: Optional[str] = Field(default=None, alias="PINECONE_INDEX")
    pinecone_environment: Optional[str] = Field(default=None, alias="PINECONE_ENVIRONMENT")

    # LLM / Embedding 配置
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_api_base_url: Optional[AnyHttpUrl] = Field(default=None, alias="OPENAI_API_BASE_URL")

    # TMDB API 配置
    tmdb_api_key: Optional[str] = Field(default=None, alias="TMDB_API_KEY")
    tmdb_api_base: AnyHttpUrl = Field(
        default="https://api.themoviedb.org/3",
        alias="TMDB_API_BASE",
    )

    # JWT 配置
    jwt_secret_key: str = Field(default="movie-ai-secret-key-2024-change-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")  # 24小时

    # 后端服务器配置
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    backend_reload: bool = Field(default=True, alias="BACKEND_RELOAD")

    # 前端API地址
    frontend_api_url: str = Field(default="http://localhost:3000", alias="NEXT_PUBLIC_API_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

