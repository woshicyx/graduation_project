"""
API模块入口 - 支持版本化管理
"""

from .v1 import (
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