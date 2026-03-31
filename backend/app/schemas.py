from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Review(BaseModel):
    id: UUID
    movie_id: UUID
    author: str
    content: str
    rating: float


class Movie(BaseModel):
    id: UUID
    title: str
    director: str
    genres: List[str]
    rating: float
    box_office: int
    release_date: date
    poster_url: str
    popularity: float
    synopsis: str


class MovieWithReviews(Movie):
    reviews: List[Review] = Field(default_factory=list)


class MovieListItem(BaseModel):
    id: UUID
    title: str
    poster_url: str
    rating: float
    popularity: float
    release_date: date
    genres: List[str]


class MovieSearchFilters(BaseModel):
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


class PaginatedMovies(BaseModel):
    items: List[MovieListItem]
    total: int
    page: int
    page_size: int


class RecommendRequest(BaseModel):
    query: str = Field(description="用户的自然语言需求，例如“想看类似星际穿越的硬科幻烧脑片”")
    limit: int = Field(default=10, le=50)


class RecommendedMovie(BaseModel):
    movie: MovieListItem
    reason: str


class RecommendResponse(BaseModel):
    query: str
    items: List[RecommendedMovie]

