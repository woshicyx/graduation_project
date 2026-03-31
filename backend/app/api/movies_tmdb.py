from __future__ import annotations

from typing import Annotated, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.db import get_db
from ..models_tmdb import Movie
from ..schemas_tmdb import (
    MovieDetail,
    MovieListItem,
    MovieSearchFilters,
    PaginatedMovies,
    TopMoviesRequest,
    MovieStats,
    SystemStats,
    GenreStats,
    DirectorStats
)
import json

router = APIRouter(prefix="/movies", tags=["movies"])


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
    revenue_min: int | None = Query(default=None, ge=0),
    revenue_max: int | None = Query(default=None, ge=0),
    release_date_from: str | None = None,
    release_date_to: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """
    获取电影列表，支持多种筛选条件
    """
    try:
        # 构建查询
        query = select(Movie)
        
        # 关键字搜索
        if q:
            query = query.where(
                or_(
                    Movie.title.ilike(f"%{q}%"),
                    Movie.overview.ilike(f"%{q}%"),
                    Movie.director.ilike(f"%{q}%")
                )
            )
        
        # 导演筛选
        if director:
            query = query.where(Movie.director.ilike(f"%{director}%"))
        
        # 类型筛选
        if genre:
            query = query.where(Movie.genres.ilike(f'%"{genre}"%'))
        
        # 评分范围筛选
        if rating_min is not None:
            query = query.where(Movie.vote_average >= rating_min)
        if rating_max is not None:
            query = query.where(Movie.vote_average <= rating_max)
        
        # 票房范围筛选
        if revenue_min is not None:
            query = query.where(Movie.revenue >= revenue_min)
        if revenue_max is not None:
            query = query.where(Movie.revenue <= revenue_max)
        
        # 上映日期范围筛选
        if release_date_from:
            query = query.where(Movie.release_date >= release_date_from)
        if release_date_to:
            query = query.where(Movie.release_date <= release_date_to)
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.order_by(desc(Movie.popularity)).offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        movies = result.scalars().all()
        
        # 转换为响应模型
        items = []
        for movie in movies:
            # 解析类型
            genres = []
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                except:
                    genres = []
            
            items.append(MovieListItem(
                id=movie.id,
                title=movie.title,
                poster_path=movie.poster_path,
                vote_average=movie.vote_average,
                popularity=movie.popularity,
                release_date=movie.release_date,
                genres=genres,
                director=movie.director,
                revenue=movie.revenue
            ))
        
        return PaginatedMovies(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get(
    "/top-box-office",
    response_model=PaginatedMovies,
    summary="票房榜单 Top N",
)
async def top_box_office(
    limit: int = Query(default=50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """
    获取票房最高的电影
    """
    try:
        query = (
            select(Movie)
            .where(Movie.revenue > 0)
            .order_by(desc(Movie.revenue))
            .limit(limit)
        )
        
        result = await db.execute(query)
        movies = result.scalars().all()
        
        items = []
        for movie in movies:
            genres = []
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                except:
                    genres = []
            
            items.append(MovieListItem(
                id=movie.id,
                title=movie.title,
                poster_path=movie.poster_path,
                vote_average=movie.vote_average,
                popularity=movie.popularity,
                release_date=movie.release_date,
                genres=genres,
                director=movie.director,
                revenue=movie.revenue
            ))
        
        return PaginatedMovies(
            items=items,
            total=len(items),
            page=1,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get(
    "/top-rated",
    response_model=PaginatedMovies,
    summary="评分榜单 Top N",
)
async def top_rated(
    limit: int = Query(default=50, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedMovies:
    """
    获取评分最高的电影
    """
    try:
        query = (
            select(Movie)
            .where(Movie.vote_average > 0)
            .order_by(desc(Movie.vote_average))
            .limit(limit)
        )
        
        result = await db.execute(query)
        movies = result.scalars().all()
        
        items = []
        for movie in movies:
            genres = []
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                except:
                    genres = []
            
            items.append(MovieListItem(
                id=movie.id,
                title=movie.title,
                poster_path=movie.poster_path,
                vote_average=movie.vote_average,
                popularity=movie.popularity,
                release_date=movie.release_date,
                genres=genres,
                director=movie.director,
                revenue=movie.revenue
            ))
        
        return PaginatedMovies(
            items=items,
            total=len(items),
            page=1,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get(
    "/{movie_id}",
    response_model=MovieDetail,
    summary="电影详情",
)
async def get_movie_detail(
    movie_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> MovieDetail:
    """
    获取电影详情
    """
    try:
        query = select(Movie).where(Movie.id == movie_id)
        result = await db.execute(query)
        movie = result.scalar_one_or_none()
        
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"电影ID {movie_id} 不存在"
            )
        
        # 解析类型
        genres_list = []
        if movie.genres:
            try:
                genres_list = json.loads(movie.genres)
            except:
                genres_list = []
        
        return MovieDetail(
            id=movie.id,
            title=movie.title,
            overview=movie.overview,
            tagline=movie.tagline,
            budget=movie.budget,
            revenue=movie.revenue,
            popularity=movie.popularity,
            release_date=movie.release_date,
            runtime=movie.runtime,
            vote_average=movie.vote_average,
            vote_count=movie.vote_count,
            poster_path=movie.poster_path,
            status=movie.status,
            genres=movie.genres,
            director=movie.director,
            created_at=movie.created_at,
            updated_at=movie.updated_at,
            genres_list=genres_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=MovieStats,
    summary="电影统计摘要",
)
async def get_movie_stats(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> MovieStats:
    """
    获取电影统计信息
    """
    try:
        # 总电影数
        total_query = select(func.count()).select_from(Movie)
        total_result = await db.execute(total_query)
        total_movies = total_result.scalar()
        
        # 有预算的电影数
        budget_query = select(func.count()).where(Movie.budget > 0)
        budget_result = await db.execute(budget_query)
        movies_with_budget = budget_result.scalar()
        
        # 有票房的电影数
        revenue_query = select(func.count()).where(Movie.revenue > 0)
        revenue_result = await db.execute(revenue_query)
        movies_with_revenue = revenue_result.scalar()
        
        # 有评分的电影数
        rating_query = select(func.count()).where(Movie.vote_average > 0)
        rating_result = await db.execute(rating_query)
        movies_with_rating = rating_result.scalar()
        
        # 平均评分
        avg_rating_query = select(func.avg(Movie.vote_average)).where(Movie.vote_average > 0)
        avg_rating_result = await db.execute(avg_rating_query)
        avg_rating = avg_rating_result.scalar()
        
        # 平均票房
        avg_revenue_query = select(func.avg(Movie.revenue)).where(Movie.revenue > 0)
        avg_revenue_result = await db.execute(avg_revenue_query)
        avg_revenue = avg_revenue_result.scalar()
        
        # 评分最高的5部电影
        top_movies_query = (
            select(Movie)
            .where(Movie.vote_average > 0)
            .order_by(desc(Movie.vote_average))
            .limit(5)
        )
        top_movies_result = await db.execute(top_movies_query)
        top_movies = top_movies_result.scalars().all()
        
        top_movies_list = []
        for movie in top_movies:
            genres = []
            if movie.genres:
                try:
                    genres = json.loads(movie.genres)
                except:
                    genres = []
            
            top_movies_list.append(MovieListItem(
                id=movie.id,
                title=movie.title,
                poster_path=movie.poster_path,
                vote_average=movie.vote_average,
                popularity=movie.popularity,
                release_date=movie.release_date,
                genres=genres,
                director=movie.director,
                revenue=movie.revenue
            ))
        
        return MovieStats(
            total_movies=total_movies,
            movies_with_budget=movies_with_budget,
            movies_with_revenue=movies_with_revenue,
            movies_with_rating=movies_with_rating,
            avg_rating=avg_rating,
            avg_revenue=avg_revenue,
            top_movies=top_movies_list
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"统计查询失败: {str(e)}"
        )


@router.get(
    "/random",
    response_model=MovieListItem,
    summary="随机获取一部电影",
)
async def get_random_movie(
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> MovieListItem:
    """
    随机获取一部电影
    """
    try:
        # 使用数据库的随机函数
        query = select(Movie).order_by(func.random()).limit(1)
        result = await db.execute(query)
        movie = result.scalar_one_or_none()
        
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有找到电影"
            )
        
        # 解析类型
        genres = []
        if movie.genres:
            try:
                genres = json.loads(movie.genres)
            except:
                genres = []
        
        return MovieListItem(
            id=movie.id,
            title=movie.title,
            poster_path=movie.poster_path,
            vote_average=movie.vote_average,
            popularity=movie.popularity,
            release_date=movie.release_date,
            genres=genres,
            director=movie.director,
            revenue=movie.revenue
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"随机查询失败: {str(e)}"
        )