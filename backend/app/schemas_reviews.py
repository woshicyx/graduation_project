"""
影评系统Pydantic模型
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class ReviewSortBy(str, Enum):
    """影评排序方式"""
    NEWEST = "newest"
    MOST_HELPFUL = "most_helpful"
    HIGHEST_RATING = "highest_rating"
    LOWEST_RATING = "lowest_rating"


class ReviewBase(BaseModel):
    """影评基础模型"""
    movie_id: int = Field(..., description="电影ID")
    rating: float = Field(..., ge=0.0, le=10.0, description="评分（0-10分）")
    title: str = Field(..., min_length=1, max_length=200, description="影评标题")
    content: str = Field(..., min_length=10, max_length=5000, description="影评内容")
    author: str = Field(default="匿名用户", max_length=100, description="作者名称")
    helpful_count: int = Field(default=0, description="有用票数")
    not_helpful_count: int = Field(default=0, description="无用票数")
    
    @validator('rating')
    def validate_rating(cls, v):
        """验证评分格式"""
        return round(v, 1)  # 保留一位小数


class ReviewCreate(ReviewBase):
    """创建影评请求模型"""
    pass


class ReviewUpdate(BaseModel):
    """更新影评请求模型"""
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    helpful_count: Optional[int] = Field(None, ge=0)
    not_helpful_count: Optional[int] = Field(None, ge=0)


class ReviewInDB(ReviewBase):
    """数据库中的影评模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewResponse(ReviewInDB):
    """影评响应模型"""
    movie_title: Optional[str] = None
    movie_poster_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReviewStats(BaseModel):
    """影评统计信息"""
    movie_id: int
    total_reviews: int
    average_rating: float
    rating_distribution: dict[str, int]  # 评分分布
    recent_reviews_count: int = Field(default=0, description="最近30天影评数")


class ReviewFilters(BaseModel):
    """影评筛选器"""
    movie_id: Optional[int] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    max_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    author: Optional[str] = None
    sort_by: ReviewSortBy = ReviewSortBy.NEWEST
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedReviews(BaseModel):
    """分页影评列表响应"""
    items: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int = 0
    
    @classmethod
    def from_reviews(
        cls,
        reviews: List[ReviewResponse],
        total: int,
        page: int,
        page_size: int
    ) -> PaginatedReviews:
        """从影评列表创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return cls(
            items=reviews,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class VoteReviewRequest(BaseModel):
    """投票影评请求"""
    helpful: bool = Field(..., description="true表示有用，false表示无用")