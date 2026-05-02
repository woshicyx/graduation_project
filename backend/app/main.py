from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.v1 import health, movies_tmdb, search, recommend, reviews, auth, user, personalized


def create_app() -> FastAPI:
    app = FastAPI(
        title="智能电影推荐平台 - 后端 API",
        description=(
            "基于 FastAPI 的后端服务，负责电影元数据查询、Hybrid Search、"
            "以及基于 LLM + RAG 的智能推荐。"
        ),
        version="0.1.0",
        debug=settings.debug,
    )

    # CORS 配置 - 根据环境动态设置
    environment = os.getenv("ENVIRONMENT", "dev")
    
    if environment == "prod":
        # 生产环境：只允许前端域名
        allowed_origins = [
            "https://movieai.vercel.app",
            "https://movieai-*.vercel.app",
        ]
    else:
        # 开发环境：允许本地和所有来源
        allowed_origins = [
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "*"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(user.router, prefix="/api")
    app.include_router(movies_tmdb.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(recommend.router, prefix="/api")
    app.include_router(reviews.router, prefix="/api")
    app.include_router(personalized.router, prefix="/api")

    return app


app = create_app()