"""
基于TMDB数据库的电影API
返回真实数据库数据
"""

from __future__ import annotations

from typing import Annotated, List, Optional
from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.sql import text

from ..core.db import get_db
from ..schemas_tmdb import (
    DatabaseMovie, 
    MovieListItem, 
    PaginatedMovies, 
    MovieSearchFilters,
    MovieStats
)

router = APIRouter(prefix="/movies", tags=["movies"])


async def get_movie_by_id(db: AsyncSession, movie_id: int) -> Optional[DatabaseMovie]:
    """根据ID获取电影"""
    query = text("""
        SELECT * FROM movies 
        WHERE id = :movie_id
    """)
    
    result = await db.execute(query, {"movie_id": movie_id})
    row = result.fetchone()
    
    if not row:
        return None
    
    # 将行转换为字典
    movie_dict = dict(row._mapping)
    return DatabaseMovie(**movie_dict)


async def search_movies(
    db: AsyncSession,
    filters: MovieSearchFilters,
    order_by: str = "popularity"
) -> tuple[List[DatabaseMovie], int]:
    """搜索电影"""
    # 构建基础查询
    base_query = """
        SELECT * FROM movies 
        WHERE 1=1
    """
    
    params = {}
    conditions = []
    
    # 关键字搜索
    if filters.q:
        conditions.append("""
            (title ILIKE :q OR 
             original_title ILIKE :q OR 
             overview ILIKE :q OR 
             director ILIKE :q)
        """)
        params["q"] = f"%{filters.q}%"
    
    # 导演筛选
    if filters.director:
        conditions.append("director ILIKE :director")
        params["director"] = f"%{filters.director}%"
    
    # 评分范围
    if filters.rating_min is not None:
        conditions.append("vote_average >= :rating_min")
        params["rating_min"] = filters.rating_min
    
    if filters.rating_max is not None:
        conditions.append("vote_average <= :rating_max")
        params["rating_max"] = filters.rating_max
    
    # 票房范围
    if filters.box_office_min is not None:
        conditions.append("revenue >= :box_office_min")
        params["box_office_min"] = filters.box_office_min
    
    if filters.box_office_max is not None:
        conditions.append("revenue <= :box_office_max")
        params["box_office_max"] = filters.box_office_max
    
    # 上映日期范围
    if filters.release_date_from:
        conditions.append("release_date >= :release_date_from")
        params["release_date_from"] = filters.release_date_from
    
    if filters.release_date_to:
        conditions.append("release_date <= :release_date_to")
        params["release_date_to"] = filters.release_date_to
    
    # 添加条件到查询
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    # 排序
    order_mapping = {
        "popularity": "popularity DESC",
        "rating": "vote_average DESC",
        "box_office": "revenue DESC",
        "release_date": "release_date DESC",
        "title": "title ASC"
    }
    order_clause = order_mapping.get(order_by, "popularity DESC")
    base_query += f" ORDER BY {order_clause}"
    
    # 分页
    offset = (filters.page - 1) * filters.page_size
    base_query += " LIMIT :limit OFFSET :offset"
    params["limit"] = filters.page_size
    params["offset"] = offset
    
    # 执行查询
    result = await db.execute(text(base_query), params)
    rows = result.fetchall()
    
    # 转换为DatabaseMovie对象
    movies = []
    for row in rows:
        movie_dict = dict(row._mapping)
        movies.append(DatabaseMovie(**movie_dict))
    
    # 获取总数
    count_query = """
        SELECT COUNT(*) as total FROM movies 
        WHERE 1=1
    """
    if conditions:
        count_query += " AND " + " AND ".join(conditions)
    
    # 移除分页参数
    count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
    count_result = await db.execute(text(count_query), count_params)
    total = count_result.scalar()
    
    return movies, total


@router.get(
    "",
    response_model=PaginatedMovies,
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
    order_by: str = Query(default="popularity", description="排序字段: popularity, rating, box_office, release_date, title"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """获取电影列表，支持搜索和筛选"""
    
    # 解析日期
    from_date = None
    to_date = None
    
    if release_date_from:
        try:
            from_date = date_type.fromisoformat(release_date_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="release_date_from格式错误，应为YYYY-MM-DD"
            )
    
    if release_date_to:
        try:
            to_date = date_type.fromisoformat(release_date_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="release_date_to格式错误，应为YYYY-MM-DD"
            )
    
    # 创建过滤器
    filters = MovieSearchFilters(
        q=q,
        director=director,
        genre=genre,  # 注意：当前数据库结构不支持类型筛选
        rating_min=rating_min,
        rating_max=rating_max,
        box_office_min=box_office_min,
        box_office_max=box_office_max,
        release_date_from=from_date,
        release_date_to=to_date,
        page=page,
        page_size=page_size,
    )
    
    # 搜索电影
    movies, total = await search_movies(db, filters, order_by)
    
    # 返回分页结果
    return PaginatedMovies.from_database_movies(movies, total, page, page_size)


@router.get(
    "/top-box-office",
    response_model=PaginatedMovies,
    summary="票房榜单 Top N",
)
async def top_box_office(
    limit: int = Query(default=50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """获取票房最高电影"""
    
    query = text("""
        SELECT * FROM movies 
        WHERE revenue > 0 
        ORDER BY revenue DESC 
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()
    
    movies = []
    for row in rows:
        movie_dict = dict(row._mapping)
        movies.append(DatabaseMovie(**movie_dict))
    
    # 获取总数
    count_query = text("SELECT COUNT(*) as total FROM movies WHERE revenue > 0")
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return PaginatedMovies.from_database_movies(movies, total, 1, limit)


@router.get(
    "/top-rated",
    response_model=PaginatedMovies,
    summary="评分榜单 Top N",
)
async def top_rated(
    limit: int = Query(default=50, ge=1, le=100),
    min_votes: int = Query(default=100, description="最小投票数，避免评分偏差"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """获取评分最高电影"""
    
    query = text("""
        SELECT * FROM movies 
        WHERE vote_count >= :min_votes AND vote_average > 0
        ORDER BY vote_average DESC 
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"limit": limit, "min_votes": min_votes})
    rows = result.fetchall()
    
    movies = []
    for row in rows:
        movie_dict = dict(row._mapping)
        movies.append(DatabaseMovie(**movie_dict))
    
    # 获取总数
    count_query = text("""
        SELECT COUNT(*) as total FROM movies 
        WHERE vote_count >= :min_votes AND vote_average > 0
    """)
    count_result = await db.execute(count_query, {"min_votes": min_votes})
    total = count_result.scalar()
    
    return PaginatedMovies.from_database_movies(movies, total, 1, limit)


@router.get(
    "/random",
    response_model=PaginatedMovies,
    summary="随机推荐电影",
)
async def random_movies(
    limit: int = Query(default=10, ge=1, le=50),
    min_rating: float = Query(default=6.0, description="最小评分"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """获取随机推荐电影"""
    
    query = text("""
        SELECT * FROM movies 
        WHERE vote_average >= :min_rating 
        ORDER BY RANDOM() 
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"limit": limit, "min_rating": min_rating})
    rows = result.fetchall()
    
    movies = []
    for row in rows:
        movie_dict = dict(row._mapping)
        movies.append(DatabaseMovie(**movie_dict))
    
    # 获取符合条件的总数
    count_query = text("""
        SELECT COUNT(*) as total FROM movies 
        WHERE vote_average >= :min_rating
    """)
    count_result = await db.execute(count_query, {"min_rating": min_rating})
    total = count_result.scalar()
    
    return PaginatedMovies.from_database_movies(movies, total, 1, limit)


@router.get(
    "/{movie_id}",
    response_model=DatabaseMovie,
    summary="电影详情",
)
async def get_movie_detail(
    movie_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> DatabaseMovie:
    """获取电影详情"""
    
    movie = await get_movie_by_id(db, movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"电影ID {movie_id} 不存在",
        )
    
    return movie


@router.get(
    "/stats/summary",
    response_model=MovieStats,
    summary="电影统计信息",
)
async def get_movie_stats(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> MovieStats:
    """获取电影库统计信息"""
    
    # 获取总数
    total_query = text("SELECT COUNT(*) as total FROM movies")
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 获取平均评分
    avg_rating_query = text("""
        SELECT AVG(vote_average) as avg_rating 
        FROM movies 
        WHERE vote_average > 0
    """)
    avg_rating_result = await db.execute(avg_rating_query)
    avg_rating = avg_rating_result.scalar() or 0
    
    # 获取总票房
    total_box_office_query = text("""
        SELECT SUM(revenue) as total_box_office 
        FROM movies 
        WHERE revenue > 0
    """)
    total_box_office_result = await db.execute(total_box_office_query)
    total_box_office = total_box_office_result.scalar() or 0
    
    # 获取类型分布（简化版本）
    genres_query = text("""
        SELECT COUNT(*) as count 
        FROM movies 
        WHERE genres IS NOT NULL AND genres != ''
    """)
    genres_result = await db.execute(genres_query)
    genres_count = genres_result.scalar() or 0
    
    # 获取年份分布
    year_query = text("""
        SELECT EXTRACT(YEAR FROM release_date) as year, COUNT(*) as count
        FROM movies 
        WHERE release_date IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM release_date)
        ORDER BY year DESC
        LIMIT 20
    """)
    year_result = await db.execute(year_query)
    by_year = {int(row.year): row.count for row in year_result.fetchall() if row.year}
    
    # 获取语言分布
    language_query = text("""
        SELECT original_language, COUNT(*) as count
        FROM movies 
        WHERE original_language IS NOT NULL
        GROUP BY original_language
        ORDER BY count DESC
        LIMIT 10
    """)
    language_result = await db.execute(language_query)
    by_language = {row.original_language: row.count for row in language_result.fetchall()}
    
    return MovieStats(
        total=total,
        average_rating=round(avg_rating, 2),
        total_box_office=total_box_office,
        genres={"total_with_genres": genres_count},  # 简化处理
        by_year=by_year,
        by_language=by_language,
    )