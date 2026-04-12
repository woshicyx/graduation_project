"""
统一Pydantic Schema - 基于当前数据库结构和API需求
包含所有API请求和响应模型
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum
import json
import re


# ==================== 枚举类 ====================

class UserRole(str, Enum):
    """用户角色枚举"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class FavoriteAction(str, Enum):
    """收藏操作枚举"""
    LIKE = "like"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"


# ==================== 用户相关Schema ====================

class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    
    @validator('email')
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('邮箱格式无效')
        return v


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('密码不匹配')
        return v


class UserUpdate(BaseModel):
    """更新用户信息"""
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserLogin(BaseModel):
    """用户登录请求"""
    identifier: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., min_length=6, description="密码")


class SocialLogin(BaseModel):
    """社交登录请求"""
    provider: str = Field(..., description="登录提供商: github, google")
    token: str = Field(..., description="OAuth令牌")
    email: Optional[str] = Field(None, description="邮箱（可选）")
    
    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('邮箱格式无效')
        return v


class UserResponse(UserBase):
    """用户响应"""
    id: int = Field(..., description="用户ID")
    role: str = Field(default="user", description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")
    is_verified: bool = Field(default=False, description="是否验证")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="用户偏好")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    """用户个人资料响应（包含统计信息）"""
    favorite_count: int = Field(0, description="收藏电影数")
    watch_history_count: int = Field(0, description="观看历史数")
    review_count: int = Field(0, description="影评数")
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌（可选）")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserResponse = Field(..., description="用户信息")


# ==================== 电影相关Schema ====================

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
    rag_text: Optional[str] = None  # RAG文本
    
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
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    
    def parse_keywords(self) -> List[str]:
        """解析keywords JSON字符串"""
        try:
            data = json.loads(self.keywords or '[]')
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                return [str(item) for item in data]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    
    def parse_production_companies(self) -> List[str]:
        """解析production_companies JSON字符串"""
        try:
            data = json.loads(self.production_companies or '[]')
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                return [str(item) for item in data]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    
    def parse_production_countries(self) -> List[str]:
        """解析production_countries JSON字符串"""
        try:
            data = json.loads(self.production_countries or '[]')
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                return [str(item) for item in data]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    
    def parse_spoken_languages(self) -> List[str]:
        """解析spoken_languages JSON字符串"""
        try:
            data = json.loads(self.spoken_languages or '[]')
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    return [item.get('name', '') for item in data if item.get('name')]
                return [str(item) for item in data]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    
    model_config = ConfigDict(from_attributes=True)


class MovieListItem(BaseModel):
    """电影列表项（用于列表展示）"""
    id: int
    title: str
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None
    popularity: Optional[float] = None
    release_date: Optional[date] = None
    genres: List[str] = Field(default_factory=list)
    director: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MovieDetailResponse(DatabaseMovie):
    """电影详情响应（包含解析后的字段）"""
    parsed_genres: List[str] = Field(default_factory=list, description="解析后的类型列表")
    parsed_keywords: List[str] = Field(default_factory=list, description="解析后的关键词列表")
    parsed_production_companies: List[str] = Field(default_factory=list, description="解析后的制作公司")
    parsed_production_countries: List[str] = Field(default_factory=list, description="解析后的制作国家")
    parsed_spoken_languages: List[str] = Field(default_factory=list, description="解析后的语言列表")
    
    @classmethod
    def from_db_movie(cls, movie: DatabaseMovie):
        """从DatabaseMovie创建MovieDetailResponse"""
        data = movie.model_dump()
        data['parsed_genres'] = movie.parse_genres()
        data['parsed_keywords'] = movie.parse_keywords()
        data['parsed_production_companies'] = movie.parse_production_companies()
        data['parsed_production_countries'] = movie.parse_production_countries()
        data['parsed_spoken_languages'] = movie.parse_spoken_languages()
        return cls(**data)


class PaginatedMovies(BaseModel):
    """分页电影列表响应"""
    items: List[MovieListItem] = Field(default_factory=list)
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")
    total_pages: int = Field(0, description="总页数")
    
    @classmethod
    def from_database_movies(cls, movies: List[DatabaseMovie], total: int, page: int, page_size: int) -> "PaginatedMovies":
        """从数据库电影列表创建分页响应"""
        items = []
        for movie in movies:
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
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0
        )


class MovieSearchFilters(BaseModel):
    """电影搜索过滤器"""
    q: Optional[str] = Field(default=None, description="关键字（电影名/剧情模糊搜索）")
    genre: Optional[str] = Field(default=None, description="类型筛选")
    director: Optional[str] = Field(default=None, description="导演筛选")
    rating_min: Optional[float] = Field(default=None, ge=0, le=10, description="最低评分")
    rating_max: Optional[float] = Field(default=None, ge=0, le=10, description="最高评分")
    year_min: Optional[int] = Field(default=None, ge=1900, le=2100, description="最早年份")
    year_max: Optional[int] = Field(default=None, ge=1900, le=2100, description="最晚年份")
    runtime_min: Optional[int] = Field(default=None, ge=0, description="最短时长（分钟）")
    runtime_max: Optional[int] = Field(default=None, ge=0, description="最长时长（分钟）")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class MovieStats(BaseModel):
    """电影统计数据"""
    total_movies: int = Field(0, description="电影总数")
    total_revenue: Optional[float] = Field(None, description="总票房")
    average_rating: Optional[float] = Field(None, description="平均评分")
    latest_movie_date: Optional[date] = Field(None, description="最新电影日期")
    oldest_movie_date: Optional[date] = Field(None, description="最老电影日期")
    genre_distribution: Dict[str, int] = Field(default_factory=dict, description="类型分布")


# ==================== 用户行为相关Schema ====================

class FavoriteRequest(BaseModel):
    """收藏请求"""
    movie_id: int = Field(..., description="电影ID")
    is_liked: bool = Field(True, description="是否喜欢")
    tags: List[str] = Field(default_factory=list, description="标签")
    notes: Optional[str] = Field(None, description="备注")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: int = Field(..., description="收藏ID")
    user_id: int = Field(..., description="用户ID")
    movie_id: int = Field(..., description="电影ID")
    is_liked: bool = Field(True, description="是否喜欢")
    tags: List[str] = Field(default_factory=list, description="标签")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    movie: Optional[MovieListItem] = Field(None, description="电影信息")
    
    model_config = ConfigDict(from_attributes=True)


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    items: List[FavoriteResponse] = Field(default_factory=list)
    total: int = Field(0, description="总收藏数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")


class WatchHistoryResponse(BaseModel):
    """观看历史响应"""
    id: int = Field(..., description="历史ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    movie_id: int = Field(..., description="电影ID")
    watch_date: datetime = Field(..., description="观看时间")
    watch_duration: Optional[int] = Field(None, description="观看时长（秒）")
    progress: Optional[float] = Field(0.0, description="观看进度")
    interaction_score: Optional[int] = Field(1, description="交互分数")
    created_at: datetime = Field(..., description="创建时间")
    movie: Optional[MovieListItem] = Field(None, description="电影信息")
    
    model_config = ConfigDict(from_attributes=True)


class SearchHistoryCreate(BaseModel):
    """搜索历史创建请求"""
    query: str = Field(..., max_length=200, description="搜索词")
    search_type: str = Field("keyword", description="搜索类型")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="筛选条件")
    result_count: int = Field(0, description="结果数量")
    result_ids: List[int] = Field(default_factory=list, description="结果ID列表")


class SearchHistoryResponse(BaseModel):
    """搜索历史响应"""
    id: int = Field(..., description="历史ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    query: str = Field(..., description="搜索词")
    search_type: str = Field("keyword", description="搜索类型")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="筛选条件")
    result_count: int = Field(0, description="结果数量")
    result_ids: List[int] = Field(default_factory=list, description="结果ID列表")
    click_count: int = Field(0, description="点击次数")
    is_successful: bool = Field(True, description="是否成功")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(from_attributes=True)


class UserRatingResponse(BaseModel):
    """用户评分响应"""
    id: int = Field(..., description="评分ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    movie_id: int = Field(..., description="电影ID")
    rating: Optional[float] = Field(None, description="评分（1-10）")
    review: Optional[str] = Field(None, description="影评内容")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    sentiment_score: Optional[float] = Field(None, description="情感分析分数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    movie: Optional[MovieListItem] = Field(None, description="电影信息")
    
    model_config = ConfigDict(from_attributes=True)


class UserStatsResponse(BaseModel):
    """用户统计数据响应"""
    user_id: int = Field(..., description="用户ID")
    favorite_count: int = Field(0, description="收藏数")
    watch_history_count: int = Field(0, description="观看历史数")
    review_count: int = Field(0, description="影评数")
    average_rating: Optional[float] = Field(None, description="平均评分")
    top_genres: List[str] = Field(default_factory=list, description="最常观看的类型")
    total_watch_time: Optional[int] = Field(None, description="总观看时长（秒）")


# ==================== 影评相关Schema ====================

from enum import Enum

class ReviewSortBy(str, Enum):
    """影评排序方式枚举"""
    NEWEST = "newest"
    MOST_HELPFUL = "most_helpful"
    HIGHEST_RATING = "highest_rating"
    LOWEST_RATING = "lowest_rating"


class ReviewFilters(BaseModel):
    """影评筛选条件"""
    movie_id: Optional[int] = Field(None, description="电影ID")
    min_rating: Optional[float] = Field(None, ge=0, le=10, description="最低评分")
    max_rating: Optional[float] = Field(None, ge=0, le=10, description="最高评分")
    min_helpful_count: Optional[int] = Field(None, ge=0, description="最小有帮助数")
    author: Optional[str] = Field(None, description="作者")
    search_query: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class ReviewCreate(BaseModel):
    """创建影评请求"""
    movie_id: int = Field(..., description="电影ID")
    rating: float = Field(..., ge=0, le=10, description="评分（0-10）")
    title: str = Field(..., max_length=200, description="影评标题")
    content: str = Field(..., description="影评内容")
    author: str = Field("匿名用户", max_length=100, description="作者")


class ReviewUpdate(BaseModel):
    """更新影评请求"""
    rating: Optional[float] = Field(None, ge=0, le=10, description="评分（0-10）")
    title: Optional[str] = Field(None, max_length=200, description="影评标题")
    content: Optional[str] = Field(None, description="影评内容")


class VoteReviewRequest(BaseModel):
    """投票影评请求"""
    is_helpful: bool = Field(True, description="是否有帮助")


class ReviewResponse(BaseModel):
    """影评响应"""
    id: int = Field(..., description="影评ID")
    movie_id: int = Field(..., description="电影ID")
    rating: float = Field(..., description="评分（0-10）")
    title: str = Field(..., description="影评标题")
    content: str = Field(..., description="影评内容")
    author: str = Field(..., description="作者")
    helpful_count: int = Field(0, description="有帮助数")
    not_helpful_count: int = Field(0, description="无帮助数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    movie_title: Optional[str] = Field(None, description="电影标题")
    poster_path: Optional[str] = Field(None, description="电影海报路径")
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedReviews(BaseModel):
    """分页影评列表响应"""
    items: List[ReviewResponse] = Field(default_factory=list)
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")
    total_pages: int = Field(0, description="总页数")
    
    @classmethod
    def from_reviews(cls, reviews: List[ReviewResponse], total: int, page: int, page_size: int) -> "PaginatedReviews":
        return cls(
            items=reviews,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )


class ReviewStats(BaseModel):
    """影评统计数据"""
    movie_id: int = Field(..., description="电影ID")
    average_rating: Optional[float] = Field(None, description="平均评分")
    total_reviews: int = Field(0, description="影评总数")
    rating_distribution: Dict[int, int] = Field(default_factory=dict, description="评分分布（评分->数量）")
    helpful_percentage: Optional[float] = Field(None, description="有帮助百分比")


# ==================== AI推荐相关Schema ====================

class RecommendRequest(BaseModel):
    """AI推荐请求"""
    query: str = Field(..., description="自然语言查询，例如'想看一部浪漫的科幻片'")
    user_id: Optional[int] = Field(None, description="用户ID")
    max_results: int = Field(10, description="最大推荐数量")
    include_reasons: bool = Field(True, description="是否包含推荐理由")


class RecommendItem(BaseModel):
    """推荐项目"""
    movie_id: int = Field(..., description="电影ID")
    title: str = Field(..., description="电影标题")
    relevance_score: float = Field(..., description="相关性得分（0-1）")
    reason: Optional[str] = Field(None, description="推荐理由")


class RecommendResponse(BaseModel):
    """AI推荐响应"""
    query: str = Field(..., description="原始查询")
    items: List[RecommendItem] = Field(default_factory=list, description="推荐电影列表")
    total_time_ms: Optional[int] = Field(None, description="处理时间（毫秒）")


class MovieWithReviews(BaseModel):
    """电影详情（含影评）"""
    movie: MovieDetailResponse
    reviews: List[ReviewResponse] = Field(default_factory=list)
    total_reviews: int = 0
    average_rating: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 导出所有Schema ====================

__all__ = [
    # 枚举
    "UserRole",
    "FavoriteAction",
    "ReviewSortBy",
    
    # 用户相关
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "SocialLogin",
    "UserResponse",
    "UserProfileResponse",
    "TokenResponse",
    
    # 电影相关
    "DatabaseMovie",
    "MovieListItem",
    "MovieDetailResponse",
    "PaginatedMovies",
    "MovieSearchFilters",
    "MovieStats",
    "MovieWithReviews",
    
    # 用户行为相关
    "FavoriteRequest",
    "FavoriteResponse",
    "FavoriteListResponse",
    "WatchHistoryResponse",
    "SearchHistoryCreate",
    "SearchHistoryResponse",
    "UserRatingResponse",
    "UserStatsResponse",
    
    # 影评相关
    "ReviewFilters",
    "ReviewCreate",
    "ReviewUpdate",
    "VoteReviewRequest",
    "ReviewResponse",
    "PaginatedReviews",
    "ReviewStats",
    
    # AI推荐相关
    "RecommendRequest",
    "RecommendItem",
    "RecommendResponse",
]
