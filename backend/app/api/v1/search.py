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
    genres: Optional[str] = None,  # 支持多选，用逗号分隔
    director: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    years: Optional[str] = None,  # 支持多选年份，用逗号分隔
    sort: Optional[str] = None,  # 排序方式: rating, popular, boxoffice
    page: int = 1,
    page_size: int = 20,
) -> PaginatedMovies:
    """搜索电影"""
    try:
        # 构建WHERE条件 - 使用%s占位符（psycopg2语法）
        conditions = []
        params = []
        
        # 当 query 为空或 '*' 时，不添加搜索条件（返回全部电影）
        if query and query != '*':
            conditions.append("(title ILIKE %s OR original_title ILIKE %s OR overview ILIKE %s)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        # 类型筛选（多选，使用OR逻辑）
        if genres:
            genre_list = [g.strip() for g in genres.split(',') if g.strip()]
            if genre_list:
                genre_conditions = [f"genres ILIKE %s" for _ in genre_list]
                conditions.append(f"({' OR '.join(genre_conditions)})")
                params.extend([f"%{g}%" for g in genre_list])
        
        if director:
            conditions.append("director ILIKE %s")
            params.append(f"%{director}%")
        
        if rating_min is not None:
            conditions.append("vote_average >= %s")
            params.append(rating_min)
        
        if rating_max is not None:
            conditions.append("vote_average <= %s")
            params.append(rating_max)
        
        # 年份筛选：release_date 格式为 YYYY-MM-DD
        if years:
            # 多选年份筛选，使用OR逻辑
            year_list = [y.strip() for y in years.split(',') if y.strip()]
            if year_list:
                year_conditions = []
                for y in year_list:
                    if y == "1980":  # "更早" 表示1980年之前
                        year_conditions.append("(release_date < '1980-01-01' OR release_date IS NULL)")
                    else:
                        year_conditions.append(f"(release_date >= '{y}-01-01' AND release_date <= '{y}-12-31')")
                if year_conditions:
                    conditions.append(f"({' OR '.join(year_conditions)})")
        else:
            # 单一年份筛选
            if year_min is not None:
                conditions.append("release_date >= %s")
                params.append(f"{year_min}-01-01")
            
            if year_max is not None:
                conditions.append("release_date <= %s")
                params.append(f"{year_max}-12-31")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 排序方式
        order_clause = "vote_average DESC, popularity DESC"
        if sort == "rating":
            order_clause = "vote_average DESC"
        elif sort == "popular":
            order_clause = "popularity DESC"
        elif sort == "boxoffice":
            order_clause = "vote_average DESC, popularity DESC"  # 票房暂无单独字段，使用评分+人气
        
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
            ORDER BY {order_clause}
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
    summary="搜索电影（支持多选筛选）",
)
def hybrid_search(
    query: str = Query(default="*", description="搜索词，*表示全部"),
    genres: Optional[str] = Query(default=None, description="多选类型，用逗号分隔"),
    director: Optional[str] = Query(default=None, description="导演搜索"),
    rating_min: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    rating_max: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    year_min: Optional[int] = Query(default=None, ge=1900, le=2100),
    year_max: Optional[int] = Query(default=None, ge=1900, le=2100),
    years: Optional[str] = Query(default=None, description="多选年代，用逗号分隔"),
    sort: Optional[str] = Query(default=None, description="排序: rating, popular, boxoffice"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedMovies:
    """搜索电影（支持多选筛选）"""
    return search_movies(
        query=query,
        genres=genres,
        director=director,
        rating_min=rating_min,
        rating_max=rating_max,
        year_min=year_min,
        year_max=year_max,
        years=years,
        sort=sort,
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


@router.get(
    "/semantic",
    response_model=PaginatedMovies,
    summary="向量语义搜索（测试用）",
)
def semantic_search(
    q: str = Query(..., description="搜索查询"),
    strategy: str = Query(default="auto", description="搜索策略: auto/filter_first/search_first/hybrid"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """
    向量语义搜索接口 - 使用修复后的 RAG 服务
    
    支持三种搜索策略：
    - auto: 自动选择（根据过滤条件判断）
    - filter_first: 先过滤后向量搜索（适用于有明确硬性条件的查询）
    - search_first: 先向量搜索后过滤（适用于模糊/相关性优先的查询）
    - hybrid: 扩大召回池后过滤（平衡策略）
    """
    try:
        from app.services.rag_service_fixed import hybrid_search as vector_hybrid_search
        
        # 执行向量混合搜索
        movies = vector_hybrid_search(
            query=q,
            strategy=strategy,
            limit=limit
        )
        
        # 转换为 PaginatedMovies 格式
        items = []
        for movie in movies:
            items.append(MovieListItem(
                id=movie.get("id"),
                title=movie.get("title", "未知"),
                poster_path=movie.get("poster_path"),
                vote_average=movie.get("vote_average"),
                popularity=movie.get("popularity"),
                release_date=movie.get("release_date"),
                genres=[],
                director=movie.get("director")
            ))
        
        return PaginatedMovies(
            items=items,
            total=len(items),
            page=1,
            page_size=limit,
            total_pages=1
        )
        
    except Exception as e:
        print(f"语义搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return PaginatedMovies(
            items=[],
            total=0,
            page=1,
            page_size=limit,
            total_pages=0
        )
