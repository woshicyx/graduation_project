"""
TMDB数据库适配的Pydantic模型
用于匹配实际数据库表结构
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field
import json


class DatabaseMovie(BaseModel):
    """数据库中的电影数据模型（匹配实际表结构）"""
    id: int
    title: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    popularity: Optional[float] = None
    release_date: Optional[date] = None
    runtime: Optional[int] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    poster_path: Optional[str] = None
    homepage: Optional[str] = None
    status: Optional[str] = None
    original_language: Optional[str] = None
    genres: Optional[str] = None  # JSON字符串
    keywords: Optional[str] = None  # JSON字符串
    production_companies: Optional[str] = None  # JSON字符串
    production_countries: Optional[str] = None  # JSON字符串
    spoken_languages: Optional[str] = None  # JSON字符串
    director: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def parse_genres(self) -> List[str]:
        """解析genres JSON字符串"""
        try:
            data = json.loads(self.genres or '[]')
            if isinstance(data, list):
                # 如果是对象列表，提取name字段
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                # 如果是字符串列表
                return [str(item) for item in data]
            return []
        except:
            return []
    
    def parse_keywords(self) -> List[str]:
        """解析keywords JSON字符串"""
        try:
            data = json.loads(self.keywords or '[]')
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                return [str(item) for item in data]
            return []
        except:
            return []
    
    def get_poster_url(self, size: str = 'w500') -> str:
        """获取海报URL"""
        if self.poster_path:
            return f'https://image.tmdb.org/t/p/{size}{self.poster_path}'
        return ''


class MovieListItem(BaseModel):
    """前端使用的电影列表项"""
    id: int
    title: str
    poster_url: str
    rating: float = Field(alias='vote_average')
    popularity: float
    release_date: Optional[date] = None
    genres: List[str]
    director: str
    box_office: int = Field(alias='revenue')
    
    class Config:
        populate_by_name = True


class MovieDetail(MovieListItem):
    """电影详情"""
    original_title: str
    overview: str
    tagline: str
    budget: int
    runtime: int
    vote_count: int
    homepage: Optional[str] = None
    status: str
    original_language: str
    keywords: List[str]
    production_companies: List[str]
    production_countries: List[str]
    spoken_languages: List[str]
    created_at: datetime
    updated_at: datetime


class PaginatedMovies(BaseModel):
    """分页电影列表响应"""
    items: List[MovieListItem]
    total: int
    page: int
    page_size: int
    total_pages: int = 0
    
    @classmethod
    def from_database_movies(
        cls, 
        db_movies: List[DatabaseMovie], 
        total: int, 
        page: int, 
        page_size: int
    ) -> PaginatedMovies:
        """从数据库电影列表创建分页响应"""
        items = []
        for db_movie in db_movies:
            # 转换为前端格式
            item = MovieListItem(
                id=db_movie.id,
                title=db_movie.title or db_movie.original_title or '未知电影',
                poster_url=db_movie.get_poster_url(),
                vote_average=db_movie.vote_average or 0,
                popularity=db_movie.popularity or 0,
                release_date=db_movie.release_date,
                genres=db_movie.parse_genres(),
                director=db_movie.director or '未知导演',
                revenue=db_movie.revenue or 0,
            )
            items.append(item)
        
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class MovieSearchFilters(BaseModel):
    """电影搜索过滤器"""
    q: Optional[str] = Field(default=None, description="关键字（电影名/剧情模糊搜索）")
    director: Optional[str] = None
    genre: Optional[str] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    box_office_min: Optional[int] = None
    box_office_max: Optional[int] = None
    release_date_from: Optional[date] = None
    release_date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20


class MovieStats(BaseModel):
    """电影统计信息"""
    total: int
    average_rating: float
    total_box_office: int
    genres: dict[str, int]
    by_year: dict[int, int]
    by_language: dict[str, int]