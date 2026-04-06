"""
扩展的用户系统数据模型
基于现有数据库结构，添加用户角色、收藏、管理员等功能
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
import uuid
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, 
    String, Text, Float, JSON, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum

Base = declarative_base()


class UserRole(str, Enum):
    """用户角色枚举"""
    GUEST = "guest"        # 游客
    USER = "user"         # 普通用户
    ADMIN = "admin"       # 管理员
    SUPER_ADMIN = "super_admin"  # 超级管理员


class User(Base):
    """用户表（扩展版）"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # 用户角色和权限
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # 社交登录信息
    github_id = Column(String(100), nullable=True, unique=True, index=True)
    google_id = Column(String(100), nullable=True, unique=True, index=True)
    
    # 用户偏好设置
    preferences = Column(JSONB, default={}, nullable=False)  # 存储JSON格式的偏好设置
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关系
    watch_history = relationship("UserWatchHistory", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("UserRating", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("UserSearchHistory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 收藏属性
    is_liked = Column(Boolean, default=True, nullable=False)  # 是否喜欢（True=喜欢，False=不喜欢）
    tags = Column(JSONB, default=[], nullable=False)  # 用户自定义标签，如["想看", "科幻"]
    notes = Column(Text, nullable=True)  # 用户备注
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="favorites")
    
    # 复合索引，确保一个用户对同一电影只有一个收藏记录
    __table_args__ = (
        (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_favorite')),
    )
    
    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, movie_id={self.movie_id})>"


class UserWatchHistory(Base):
    """用户观看历史表（已存在，扩展版）"""
    __tablename__ = "user_watch_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 观看信息
    watch_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    watch_duration = Column(Integer, default=0, nullable=False)  # 观看时长（秒）
    progress = Column(Float, default=0.0, nullable=False)  # 观看进度（0.0-1.0）
    
    # 交互行为
    interaction_score = Column(Integer, default=1, nullable=False)  # 交互分数（浏览=1，观看详情=3，完整观看=5）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="watch_history")
    
    def __repr__(self):
        return f"<UserWatchHistory(user_id={self.user_id}, movie_id={self.movie_id}, watch_date={self.watch_date})>"


class UserRating(Base):
    """用户评分表（已存在，扩展版）"""
    __tablename__ = "user_ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 评分信息
    rating = Column(Float, nullable=False)  # 1-10分
    review = Column(Text, nullable=True)
    
    # 情感分析
    sentiment_score = Column(Float, nullable=True)  # -1.0到1.0，负数为负面，正数为正面
    keywords = Column(JSONB, default=[], nullable=False)  # 评论关键词
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="ratings")
    
    # 复合索引，确保一个用户对同一电影只有一个评分
    __table_args__ = (
        (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating')),
    )
    
    def __repr__(self):
        return f"<UserRating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"


class UserSearchHistory(Base):
    """用户搜索历史表"""
    __tablename__ = "user_search_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # nullable=True支持游客
    session_id = Column(String(100), nullable=True, index=True)  # 游客会话ID
    
    # 搜索信息
    query = Column(String(500), nullable=False)  # 搜索关键词
    search_type = Column(String(50), nullable=False)  # 搜索类型：keyword, hybrid, semantic, filter
    filters = Column(JSONB, default={}, nullable=False)  # 搜索过滤器
    
    # 搜索结果
    result_count = Column(Integer, default=0, nullable=False)  # 返回结果数量
    result_ids = Column(JSONB, default=[], nullable=False)  # 返回的电影ID列表
    
    # 用户行为
    click_count = Column(Integer, default=0, nullable=False)  # 用户点击次数
    is_successful = Column(Boolean, default=True, nullable=False)  # 是否成功找到内容
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = relationship("User", back_populates="search_history")
    
    def __repr__(self):
        return f"<UserSearchHistory(user_id={self.user_id}, query={self.query}, created_at={self.created_at})>"


class AdminAuditLog(Base):
    """管理员操作审计日志"""
    __tablename__ = "admin_audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 操作信息
    action_type = Column(String(100), nullable=False)  # 操作类型：create, update, delete, export, etc.
    resource_type = Column(String(100), nullable=False)  # 资源类型：movie, user, review, etc.
    resource_id = Column(String(100), nullable=True)  # 资源ID
    
    # 操作详情
    old_data = Column(JSONB, nullable=True)  # 操作前数据
    new_data = Column(JSONB, nullable=True)  # 操作后数据
    changes = Column(JSONB, nullable=True)  # 变更详情
    
    # IP和用户代理
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AdminAuditLog(admin_id={self.admin_id}, action_type={self.action_type}, created_at={self.created_at})>"


class SystemStatistic(Base):
    """系统统计数据表（用于数据大屏）"""
    __tablename__ = "system_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 统计维度
    stat_date = Column(DateTime, nullable=False, index=True)  # 统计日期
    stat_type = Column(String(100), nullable=False, index=True)  # 统计类型：daily_user_growth, daily_search, etc.
    
    # 统计数据
    metric_name = Column(String(100), nullable=False)  # 指标名称
    metric_value = Column(JSONB, nullable=False)  # 指标值（JSON格式）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 复合索引
    __table_args__ = (
        (db.UniqueConstraint('stat_date', 'stat_type', 'metric_name', name='unique_stat_metric')),
    )
    
    def __repr__(self):
        return f"<SystemStatistic(stat_date={self.stat_date}, stat_type={self.stat_type}, metric_name={self.metric_name})>"


class PopularSearchTerm(Base):
    """热门搜索词表"""
    __tablename__ = "popular_search_terms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 搜索词信息
    term = Column(String(200), nullable=False, index=True)
    search_count = Column(Integer, default=1, nullable=False)
    
    # 时间维度
    period_start = Column(DateTime, nullable=False, index=True)  # 统计周期开始
    period_end = Column(DateTime, nullable=False, index=True)  # 统计周期结束
    
    # 关联信息
    related_movie_ids = Column(JSONB, default=[], nullable=False)  # 关联的电影ID
    categories = Column(JSONB, default=[], nullable=False)  # 搜索词分类
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PopularSearchTerm(term={self.term}, search_count={self.search_count})>"


# 导入数据库对象（需要根据实际配置调整）
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库配置（从环境变量或配置文件读取）
DATABASE_URL = "postgresql://postgres:356921@localhost:5432/movie_recommendation"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 注意：这里需要从实际的SQLAlchemy配置中导入db对象
# 由于不知道当前项目的确切配置，这里使用一个占位符
db = None  # 需要从现有配置中导入实际的db对象

def init_db():
    """初始化数据库表（谨慎使用，会创建/更新表结构）"""
    Base.metadata.create_all(bind=engine)
    print("数据库表已初始化")


if __name__ == "__main__":
    # 测试数据库连接和表创建
    init_db()
    print("用户系统数据库架构已创建")