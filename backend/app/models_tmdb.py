from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, Float, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Movie(Base):
    """电影表模型 - 对应TMDB数据集"""
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
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
    status: Mapped[Optional[str]] = mapped_column(String(50))
    genres: Mapped[Optional[str]] = mapped_column(Text)  # JSON格式存储
    director: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
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
            "status": self.status,
            "genres": self.genres,
            "director": self.director,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Genre(Base):
    """电影类型表"""
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class MovieGenre(Base):
    """电影-类型关联表"""
    __tablename__ = "movie_genres"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Actor(Base):
    """演员表"""
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class MovieActor(Base):
    """电影-演员关联表"""
    __tablename__ = "movie_actors"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character: Mapped[Optional[str]] = mapped_column(String(500))
    cast_order: Mapped[Optional[int]] = mapped_column(Integer)


class Director(Base):
    """导演表"""
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class MovieDirector(Base):
    """电影-导演关联表"""
    __tablename__ = "movie_directors"

    movie_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    director_id: Mapped[int] = mapped_column(Integer, primary_key=True)