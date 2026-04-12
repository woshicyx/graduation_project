"""
搜索API - 基于PostgreSQL的模糊搜索
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.core.db import Database
from app.schemas import (
    DatabaseMovie, 
    MovieListItem, 
    PaginatedMovies
)

router = APIRouter(prefix="/search", tags=["search"])


def search_movies(
    query: str,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedMovies:
    """搜索电影"""
    try:
        # 构建WHERE条件 - 使用%s占位符（psycopg2语法）
        conditions = []
        params = []
        
        if query:
            conditions.append("(title ILIKE %s OR original_title ILIKE %s OR overview ILIKE %s)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if genre:
            conditions.append("genres ILIKE %s")
            params.append(f"%{genre}%")
        
        if director:
            conditions.append("director ILIKE %s")
            params.append(f"%{director}%")
        
        if rating_min is not None:
            conditions.append("vote_average >= %s")
            params.append(rating_min)
        
        if rating_max is not None:
            conditions.append("vote_average <= %s")
            params.append(rating_max)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM movies WHERE {where_clause}"
        count_result = Database.fetchrow(count_query, *params)
        total = count_result['total'] if count_result else 0
        
        # 获取分页数据
        offset = (page - 1) * page_size
        params_paged = params.copy()
        params_paged.extend([page_size, offset])
        search_query = f"""
            SELECT * FROM movies 
            WHERE {where_clause}
            ORDER BY vote_average DESC, popularity DESC
            LIMIT %s OFFSET %s
        """
        
        rows = Database.fetch(search_query, *params_paged)
        
        items = []
        for row in rows:
            movie = DatabaseMovie(**row)
            items.append(MovieListItem(
                id=movie.id,
                title=movie.title or "未知",
                poster_path=movie.poster_path,
                vote_average=movie.vote_average,
                popularity=movie.popularity,
                release_date=movie.release_date,
                genres=movie.parse_genres() if movie.genres else [],
                director=movie.director
            ))
        
        return PaginatedMovies(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0
        )
    except Exception as e:
        print(f"搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return PaginatedMovies(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0
        )


@router.get(
    "/hybrid",
    response_model=PaginatedMovies,
    summary="搜索电影",
)
def hybrid_search(
    query: str = Query(..., description="自然语言搜索词"),
    genre: Optional[str] = None,
    director: Optional[str] = None,
    rating_min: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    rating_max: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedMovies:
    """搜索电影"""
    return search_movies(
        query=query,
        genre=genre,
        director=director,
        rating_min=rating_min,
        rating_max=rating_max,
        page=page,
        page_size=page_size,
    )


@router.get(
    "",
    response_model=PaginatedMovies,
    summary="电影列表",
)
def list_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedMovies:
    """获取电影列表"""
    return search_movies(
        query="",
        page=page,
        page_size=page_size,
    )