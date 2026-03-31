from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
import json

from pydantic import BaseModel, Field, validator


class MovieBase(BaseModel):
    """电影基础模型"""
    id: int
    title: str
    overview: Optional[str] = None
    tagline: Optional[str] = None
    budget: Optional[int] = 0
    revenue: Optional[int] = 0
    popularity: Optional[float] = 0.0
    release_date: Optional[date] = None
    runtime: Optional[int] = 0
    vote_average: Optional[float] = 0.0
    vote_count: Optional[int] = 0
    poster_path: Optional[str] = None
    status: Optional[str] = None
    genres: Optional[str] = "[]"  # JSON字符串
    director: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MovieListItem(BaseModel):
    """电影列表项"""
    id: int
    title: str
    poster_path: Optional[str] = None
    vote_average: Optional[float] = 0.0
    popularity: Optional[float] = 0.0
    release_date: Optional[date] = None
    genres: List[str] = Field(default_factory=list)
    director: Optional[str] = None
    revenue: Optional[int] = 0

    @validator("genres", pre=True)
    def parse_genres(cls, v):
        """解析JSON格式的类型字符串"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return []


class MovieDetail(MovieBase):
    """电影详情"""
    genres_list: List[str] = Field(default_factory=list)

    @validator("genres_list", pre=True, always=True)
    def parse_genres_list(cls, v, values):
        """从genres字段解析类型列表"""
        genres_str = values.get("genres", "[]")
        if isinstance(genres_str, str):
            try:
                return json.loads(genres_str)
            except:
                return []
        return []


class MovieSearchFilters(BaseModel):
    """电影搜索过滤器"""
    q: Optional[str] = Field(default=None, description="关键字（电影名/剧情模糊搜索）")
    director: Optional[str] = None
    genre: Optional[str] = None
    rating_min: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    rating_max: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    revenue_min: Optional[int] = Field(default=None, ge=0)
    revenue_max: Optional[int] = Field(default=None, ge=0)
    release_date_from: Optional[date] = None
    release_date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedMovies(BaseModel):
    """分页电影列表"""
    items: List[MovieListItem]
    total: int
    page: int
    page_size: int


class TopMoviesRequest(BaseModel):
    """热门电影请求"""
    limit: int = Field(default=50, ge=1, le=100)


class MovieStats(BaseModel):
    """电影统计信息"""
    total_movies: int
    movies_with_budget: int
    movies_with_revenue: int
    movies_with_rating: int
    avg_rating: Optional[float] = None
    avg_revenue: Optional[float] = None
    top_movies: List[MovieListItem] = Field(default_factory=list)


class GenreStats(BaseModel):
    """类型统计信息"""
    name: str
    count: int
    avg_rating: float
    avg_revenue: float


class DirectorStats(BaseModel):
    """导演统计信息"""
    name: str
    movie_count: int
    avg_rating: float
    total_revenue: int


class SystemStats(BaseModel):
    """系统统计信息"""
    movie_stats: MovieStats
    top_genres: List[GenreStats]
    top_directors: List[DirectorStats]
    last_updated: datetime