"""
API v1 版本 - 主要功能API
"""

from . import (
    auth,
    health,
    movies_tmdb,
    movies,
    recommend,
    reviews,
    search,
    user,
)

__all__ = [
    "auth",
    "health", 
    "movies_tmdb",
    "movies",
    "recommend",
    "reviews",
    "search",
    "user",
]