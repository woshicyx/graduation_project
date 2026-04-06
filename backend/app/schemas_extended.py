"""
扩展的用户系统Pydantic模式
用于API请求和响应验证
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum


# 枚举类
class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class FavoriteAction(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"


# 基础模型
class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")


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
    display_name: Optional[str] = Field(None, max_length=100)
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
    email: Optional[EmailStr] = Field(None, description="邮箱（可选）")


class UserResponse(UserBase):
    """用户响应"""
    id: int = Field(..., description="用户ID")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")
    is_verified: bool = Field(default=False, description="是否验证")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="用户偏好")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    """用户个人资料响应（包含统计信息）"""
    watch_count: int = Field(0, description="观看电影数量")
    favorite_count: int = Field(0, description="收藏电影数量")
    rating_count: int = Field(0, description="评分数量")


class TokenResponse(BaseModel):
    """认证令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(3600, description="过期时间（秒）")
    user: UserResponse = Field(..., description="用户信息")


# 收藏相关模型
class FavoriteBase(BaseModel):
    """收藏基础信息"""
    movie_id: int = Field(..., description="电影ID")
    is_liked: bool = Field(default=True, description="是否喜欢")
    tags: List[str] = Field(default_factory=list, description="自定义标签")
    notes: Optional[str] = Field(None, description="备注")


class FavoriteCreate(FavoriteBase):
    """创建收藏请求"""
    pass


class FavoriteUpdate(BaseModel):
    """更新收藏请求"""
    is_liked: Optional[bool] = Field(None, description="是否喜欢")
    tags: Optional[List[str]] = Field(None, description="自定义标签")
    notes: Optional[str] = Field(None, description="备注")


class FavoriteResponse(FavoriteBase):
    """收藏响应"""
    id: int = Field(..., description="收藏ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


# 观看历史相关模型
class WatchHistoryBase(BaseModel):
    """观看历史基础信息"""
    movie_id: int = Field(..., description="电影ID")
    watch_duration: int = Field(default=0, description="观看时长（秒）")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="观看进度")
    interaction_score: int = Field(default=1, ge=1, le=5, description="交互分数")


class WatchHistoryCreate(WatchHistoryBase):
    """创建观看历史请求"""
    pass


class WatchHistoryResponse(WatchHistoryBase):
    """观看历史响应"""
    id: int = Field(..., description="历史记录ID")
    user_id: int = Field(..., description="用户ID")
    watch_date: datetime = Field(..., description="观看时间")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(from_attributes=True)


# 评分相关模型
class RatingBase(BaseModel):
    """评分基础信息"""
    movie_id: int = Field(..., description="电影ID")
    rating: float = Field(..., ge=1.0, le=10.0, description="评分(1-10)")
    review: Optional[str] = Field(None, description="评论")


class RatingCreate(RatingBase):
    """创建评分请求"""
    pass


class RatingUpdate(BaseModel):
    """更新评分请求"""
    rating: Optional[float] = Field(None, ge=1.0, le=10.0, description="评分")
    review: Optional[str] = Field(None, description="评论")


class RatingResponse(RatingBase):
    """评分响应"""
    id: int = Field(..., description="评分ID")
    user_id: int = Field(..., description="用户ID")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="情感分析分数")
    keywords: List[str] = Field(default_factory=list, description="评论关键词")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


# 搜索历史相关模型
class SearchHistoryBase(BaseModel):
    """搜索历史基础信息"""
    query: str = Field(..., max_length=500, description="搜索关键词")
    search_type: str = Field(default="keyword", description="搜索类型")
    filters: Dict[str, Any] = Field(default_factory=dict, description="搜索过滤器")
    result_count: int = Field(default=0, description="结果数量")
    result_ids: List[int] = Field(default_factory=list, description="结果ID列表")
    click_count: int = Field(default=0, description="点击次数")
    is_successful: bool = Field(default=True, description="是否成功")


class SearchHistoryCreate(SearchHistoryBase):
    """创建搜索历史请求"""
    session_id: Optional[str] = Field(None, description="会话ID（游客使用）")


class SearchHistoryResponse(SearchHistoryBase):
    """搜索历史响应"""
    id: int = Field(..., description="搜索记录ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(from_attributes=True)


# 管理员相关模型
class AdminUserUpdate(BaseModel):
    """管理员更新用户信息"""
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_verified: Optional[bool] = Field(None, description="是否验证")


class SystemStatisticResponse(BaseModel):
    """系统统计响应"""
    stat_date: datetime = Field(..., description="统计日期")
    stat_type: str = Field(..., description="统计类型")
    metric_name: str = Field(..., description="指标名称")
    metric_value: Dict[str, Any] = Field(..., description="指标值")
    
    model_config = ConfigDict(from_attributes=True)


class PopularSearchTermResponse(BaseModel):
    """热门搜索词响应"""
    term: str = Field(..., description="搜索词")
    search_count: int = Field(..., description="搜索次数")
    period_start: datetime = Field(..., description="周期开始")
    period_end: datetime = Field(..., description="周期结束")
    related_movie_ids: List[int] = Field(default_factory=list, description="相关电影ID")
    categories: List[str] = Field(default_factory=list, description="分类")
    
    model_config = ConfigDict(from_attributes=True)


# 分页响应模型
class PaginatedResponse(BaseModel):
    """分页响应基类"""
    items: List[Any] = Field(..., description="项目列表")
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页码")
    size: int = Field(20, description="每页大小")
    pages: int = Field(..., description="总页数")


class UsersPaginatedResponse(PaginatedResponse):
    """用户分页响应"""
    items: List[UserResponse]


class FavoritesPaginatedResponse(PaginatedResponse):
    """收藏分页响应"""
    items: List[FavoriteResponse]


class WatchHistoryPaginatedResponse(PaginatedResponse):
    """观看历史分页响应"""
    items: List[WatchHistoryResponse]


class RatingsPaginatedResponse(PaginatedResponse):
    """评分分页响应"""
    items: List[RatingResponse]


# 统计分析模型
class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_users: int = Field(0, description="总用户数")
    active_users_today: int = Field(0, description="今日活跃用户")
    new_users_today: int = Field(0, description="今日新用户")
    total_watches: int = Field(0, description="总观看次数")
    total_favorites: int = Field(0, description="总收藏数")
    total_ratings: int = Field(0, description="总评分数")
    popular_searches: List[PopularSearchTermResponse] = Field(default_factory=list, description="热门搜索词")
    user_growth: List[Dict[str, Any]] = Field(default_factory=list, description="用户增长趋势")


# 用户偏好模型
class UserPreferences(BaseModel):
    """用户偏好设置"""
    theme: str = Field(default="light", description="主题: light, dark, auto")
    language: str = Field(default="zh-CN", description="语言")
    notifications: Dict[str, bool] = Field(
        default_factory=lambda: {"email": True, "push": False},
        description="通知设置"
    )
    recommendation_frequency: int = Field(default=10, ge=1, le=50, description="推荐频率（电影数量）")
    default_search_type: str = Field(default="hybrid", description="默认搜索类型")
    movie_preferences: Dict[str, List[str]] = Field(
        default_factory=lambda: {"genres": [], "languages": [], "years": []},
        description="电影偏好"
    )
    
    model_config = ConfigDict(from_attributes=True)