from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db import get_db
from ..core.vector import get_qdrant_client
from .. import schemas

router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "/hybrid",
    response_model=schemas.PaginatedMovies,
    summary="Hybrid Search：结构化过滤 + 语义检索",
)
async def hybrid_search(
    query: str = Query(..., description="自然语言搜索词"),
    genre: str | None = None,
    director: str | None = None,
    rating_min: float | None = Query(default=None, ge=0.0, le=10.0),
    rating_max: float | None = Query(default=None, ge=0.0, le=10.0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> schemas.PaginatedMovies:
    # TODO:
    # 1. 对 query 生成 embedding
    # 2. 使用 Qdrant/Pinecone 做向量检索召回 Top K movie_id
    # 3. 在 PostgreSQL 中结合结构化过滤（genre、director、rating 范围）
    # 4. 返回分页后的 MovieListItem 列表
    _ = get_qdrant_client()
    return schemas.PaginatedMovies(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )

