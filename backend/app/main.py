from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import health, movies_tmdb, search, recommend


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

    # CORS：前端 Next.js 默认跑在 3000 端口
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(health.router)
    app.include_router(movies_tmdb.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(recommend.router, prefix="/api")

    return app


app = create_app()