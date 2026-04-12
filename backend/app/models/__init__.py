"""
统一数据模型 - 基于当前数据库结构
包含电影、用户、影评等所有数据模型
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List
import uuid
from enum import Enum

from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, Enum as SQLAlchemyEnum, 
    Float, ForeignKey, Integer, String, Text, TIMESTAMP, JSON, Index
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ==================== 用户系统相关模型 ====================

class UserRole(str, Enum):
    """用户角色枚举"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """用户表 - 对应数据库中的users表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 个人信息
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    role: Mapped[Optional[str]] = mapped_column(String(20), default="user")
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # 社交登录
    github_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    
    # 偏好设置
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 关系
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    watch_history = relationship("UserWatchHistory", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("UserRating", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("UserSearchHistory", back_populates="user", cascade="all, delete-orphan")


class UserFavorite(Base):
    """用户收藏表 - 对应数据库中的user_favorites表"""
    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 收藏属性
    is_liked: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="favorites")
    movie = relationship("Movie", backref="favorites")


class UserWatchHistory(Base):
    """用户观看历史表 - 对应数据库中的user_watch_history表"""
    __tablename__ = "user_watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), index=True)
    
    # 观看信息
    watch_date: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    watch_duration: Mapped[Optional[int]] = mapped_column(Integer)  # 观看时长（秒）
    progress: Mapped[Optional[float]] = mapped_column(Float, default=0.0)  # 观看进度（0-1）
    interaction_score: Mapped[Optional[int]] = mapped_column(Integer, default=1)  # 交互分数
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="watch_history")
    movie = relationship("Movie", backref="watch_history")


class UserRating(Base):
    """用户评分表 - 对应数据库中的user_ratings表"""
    __tablename__ = "user_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), index=True)
    
    # 评分信息
    rating: Mapped[Optional[float]] = mapped_column(Float)  # 评分（1-10）
    review: Mapped[Optional[str]] = mapped_column(Text)  # 影评内容
    keywords: Mapped[Optional[list]] = mapped_column(JSONB, default=list)  # 关键词
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)  # 情感分析分数
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", backref="ratings")


class UserSearchHistory(Base):
    """用户搜索历史表 - 对应数据库中的user_search_history表"""
    __tablename__ = "user_search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # 会话ID（用于游客）
    
    # 搜索信息
    query: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    search_type: Mapped[Optional[str]] = mapped_column(String(50), default="keyword")
    filters: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # 搜索结果
    result_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    result_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    click_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    is_successful: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="search_history")


# ==================== 电影系统相关模型 ====================

class Movie(Base):
    """电影表模型 - 对应TMDB数据集和数据库中的movies表"""
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(500))
    overview: Mapped[Optional[str]] = mapped_column(Text)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    budget: Mapped[Optional[int]] = mapped_column(BigInteger, default=0)
    revenue: Mapped[Optional[int]] = mapped_column(BigInteger, default=0)
    popularity: Mapped[Optional[float]] = mapped_column(Float, default=0.0, index=True)
    release_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    runtime: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    vote_average: Mapped[Optional[float]] = mapped_column(Float, default=0.0, index=True)
    vote_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    poster_path: Mapped[Optional[str]] = mapped_column(String(500))
    homepage: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    original_language: Mapped[Optional[str]] = mapped_column(String(10))
    
    # JSON格式存储的字段
    genres: Mapped[Optional[str]] = mapped_column(Text)  # 存储为JSON字符串
    keywords: Mapped[Optional[str]] = mapped_column(Text)
    production_companies: Mapped[Optional[str]] = mapped_column(Text)
    production_countries: Mapped[Optional[str]] = mapped_column(Text)
    spoken_languages: Mapped[Optional[str]] = mapped_column(Text)
    
    # 导演信息（为了兼容性保留）
    director: Mapped[Optional[str]] = mapped_column(String(500))
    
    # RAG相关
    rag_text: Mapped[Optional[str]] = mapped_column(Text)  # 用于RAG的文本
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "original_title": self.original_title,
            "overview": self.overview,
            "tagline": self.tagline,
            "budget": self.budget,
            "revenue": self.revenue,
            "popularity": self.popularity,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "runtime": self.runtime,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "poster_path": self.poster_path,
            "homepage": self.homepage,
            "status": self.status,
            "original_language": self.original_language,
            "genres": self.genres,
            "keywords": self.keywords,
            "production_companies": self.production_companies,
            "production_countries": self.production_countries,
            "spoken_languages": self.spoken_languages,
            "director": self.director,
            "rag_text": self.rag_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Actor(Base):
    """演员表 - 对应数据库中的actors表"""
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    gender: Mapped[Optional[int]] = mapped_column(Integer)  # 0=未知, 1=女性, 2=男性
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MovieActor(Base):
    """电影-演员关联表 - 对应数据库中的movie_actors表"""
    __tablename__ = "movie_actors"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True)
    character: Mapped[str] = mapped_column(String(500), nullable=False)
    cast_order: Mapped[Optional[int]] = mapped_column(Integer)


class Director(Base):
    """导演表 - 对应数据库中的directors表"""
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MovieDirector(Base):
    """电影-导演关联表 - 对应数据库中的movie_directors表"""
    __tablename__ = "movie_directors"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    director_id: Mapped[int] = mapped_column(Integer, ForeignKey("directors.id", ondelete="CASCADE"), primary_key=True)


class Genre(Base):
    """电影类型表 - 对应数据库中的genres表"""
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MovieGenre(Base):
    """电影-类型关联表 - 对应数据库中的movie_genres表"""
    __tablename__ = "movie_genres"

    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)


# ==================== 系统管理相关模型 ====================

class AdminAuditLog(Base):
    """管理员审计日志表 - 对应数据库中的admin_audit_logs表"""
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    # 操作信息
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 数据变更
    old_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    changes: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # 访问信息
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class SystemStatistic(Base):
    """系统统计数据表 - 对应数据库中的system_statistics表"""
    __tablename__ = "system_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 统计维度
    stat_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    stat_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # 统计数据
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 复合约束
    __table_args__ = (
        Index('idx_unique_stat_metric', 'stat_date', 'stat_type', 'metric_name', unique=True),
    )


class PopularSearchTerm(Base):
    """热门搜索词表 - 对应数据库中的popular_search_terms表"""
    __tablename__ = "popular_search_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 搜索词信息
    term: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    search_count: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    
    # 时间维度
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # 关联信息
    related_movie_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    categories: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class TotalUser(Base):
    """总用户数表 - 对应数据库中的total_users表"""
    __tablename__ = "total_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    count: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# 导出所有模型
__all__ = [
    "Base",
    "UserRole",
    "User",
    "UserFavorite",
    "UserWatchHistory", 
    "UserRating",
    "UserSearchHistory",
    "Movie",
    "Actor",
    "MovieActor",
    "Director",
    "MovieDirector",
    "Genre",
    "MovieGenre",
    "AdminAuditLog",
    "SystemStatistic",
    "PopularSearchTerm",
    "TotalUser",
]