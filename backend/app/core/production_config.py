import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProductionSettings(BaseSettings):
    """生产环境配置 - 读取环境变量"""

    model_config = SettingsConfigDict(
        env_file=(".env.production", ".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用基础配置
    app_name: str = Field(default="movie-recommender-backend", alias="APP_NAME")
    environment: Literal["dev", "prod", "test"] = Field(default="prod", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # 数据库配置
    database_url: str = Field(alias="DATABASE_URL")
    
    # 数据库连接配置
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="movie_recommendation", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")

    # 向量数据库配置
    qdrant_url: Optional[AnyHttpUrl] = Field(alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(alias="QDRANT_API_KEY")

    # 智谱 AI 配置
    zhipuai_api_key: Optional[str] = Field(alias="ZHIPUAI_API_KEY")
    zhipuai_api_base: str = Field(default="https://open.bigmodel.cn/api/paas/v4", alias="ZHIPUAI_API_BASE")

    # TMDB API 配置
    tmdb_api_key: Optional[str] = Field(alias="TMDB_API_KEY")
    tmdb_api_base: AnyHttpUrl = Field(
        default="https://api.themoviedb.org/3",
        alias="TMDB_API_BASE",
    )

    # JWT 配置
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # 前端API地址
    frontend_api_url: str = Field(alias="NEXT_PUBLIC_API_URL")

    # Railway 配置
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="PORT")
    backend_reload: bool = Field(default=False, alias="BACKEND_RELOAD")


@lru_cache(maxsize=1)
def get_production_settings() -> ProductionSettings:
    return ProductionSettings()


production_settings = get_production_settings()