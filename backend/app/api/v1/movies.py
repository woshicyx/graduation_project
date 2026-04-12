from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app import schemas

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get(
    "",
    response_model=schemas.PaginatedMovies,
    summary="电影列表 / 结构化搜索",
)
async def list_movies(
    q: str | None = Query(default=None, description="关键字（电影名、导演等）"),
    director: str | None = None,
    genre: str | None = None,
    rating_min: float | None = Query(default=None, ge=0.0, le=10.0),
    rating_max: float | None = Query(default=None, ge=0.0, le=10.0),
    box_office_min: int | None = Query(default=None, ge=0),
    box_office_max: int | None = Query(default=None, ge=0),
    release_date_from: str | None = None,
    release_date_to: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> schemas.PaginatedMovies:
    # TODO: 使用 SQLAlchemy + PostgreSQL 实现真实查询，这里先返回占位数据
    return schemas.PaginatedMovies(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/top-box-office",
    response_model=schemas.PaginatedMovies,
    summary="票房榜单 Top N",
)
async def top_box_office(
    limit: int = Query(default=50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> schemas.PaginatedMovies:
    # TODO: SQL 排序 box_office desc
    return schemas.PaginatedMovies(items=[], total=0, page=1, page_size=limit)


@router.get(
    "/top-rated",
    response_model=schemas.PaginatedMovies,
    summary="评分榜单 Top N",
)
async def top_rated(
    limit: int = Query(default=50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> schemas.PaginatedMovies:
    # TODO: SQL 排序 rating desc
    return schemas.PaginatedMovies(items=[], total=0, page=1, page_size=limit)


@router.get(
    "/{movie_id}",
    response_model=schemas.MovieWithReviews,
    summary="电影详情（含影评）",
)
async def get_movie_detail(
    movie_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> schemas.MovieWithReviews:
    # TODO: 真实查询数据库；暂时返回 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Movie not found (not implemented yet)",
    )

