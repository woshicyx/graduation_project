"""
基于TMDB数据库的电影API
返回真实数据库数据（带fallback到模拟数据）
"""

from __future__ import annotations

from typing import List, Optional
from datetime import date as date_type, date, datetime
from fastapi import APIRouter, HTTPException, Query, status

from app.core.db import Database
from app.schemas import (
    DatabaseMovie, 
    MovieListItem, 
    PaginatedMovies, 
    MovieSearchFilters,
    MovieStats
)

router = APIRouter(prefix="/movies", tags=["movies"])

# 模拟电影数据
MOCK_MOVIES = [
    {
        "id": 11,
        "title": "Star Wars",
        "original_title": "Star Wars",
        "overview": "卢克·天行者加入了反抗军同盟，并协助他们从银河帝国手中偷取死星计划。",
        "tagline": "很久以前，在一个遥远的银河系……",
        "budget": 11000000,
        "revenue": 775398007,
        "popularity": 100.5,
        "release_date": date(1977, 5, 25),
        "runtime": 121,
        "vote_average": 8.1,
        "vote_count": 15000,
        "poster_path": "/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
        "homepage": "https://www.starwars.com/films/star-wars-episode-iv-a-new-hope",
        "status": "Released",
        "original_language": "en",
        "genres": '[{"id": 12, "name": "冒险"}, {"id": 28, "name": "动作"}, {"id": 878, "name": "科幻"}]',
        "keywords": '[{"id": 123, "name": "太空歌剧"}, {"id": 456, "name": "绝地武士"}]',
        "production_companies": '[{"name": "Lucasfilm"}]',
        "production_countries": '[{"iso_3166_1": "US", "name": "美国"}]',
        "spoken_languages": '[{"iso_639_1": "en", "name": "英语"}]',
        "director": "乔治·卢卡斯",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": 299534,
        "title": "复仇者联盟4：终局之战",
        "original_title": "Avengers: Endgame",
        "overview": "在灭霸使用无限手套消灭了宇宙中一半的生命后，剩余的复仇者必须找到一种方法来逆转他的行动，并为宇宙恢复平衡。",
        "tagline": "终局之战",
        "budget": 356000000,
        "revenue": 2799439100,
        "popularity": 200.8,
        "release_date": date(2019, 4, 24),
        "runtime": 181,
        "vote_average": 8.2,
        "vote_count": 25000,
        "poster_path": "/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
        "homepage": "https://www.marvel.com/movies/avengers-endgame",
        "status": "Released",
        "original_language": "en",
        "genres": '[{"id": 12, "name": "冒险"}, {"id": 28, "name": "动作"}, {"id": 878, "name": "科幻"}]',
        "keywords": '[{"id": 789, "name": "漫威"}, {"id": 101, "name": "超级英雄"}]',
        "production_companies": '[{"name": "Marvel Studios"}]',
        "production_countries": '[{"iso_3166_1": "US", "name": "美国"}]',
        "spoken_languages": '[{"iso_639_1": "en", "name": "英语"}]',
        "director": "安东尼·罗素, 乔·罗素",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": 13,
        "title": "阿甘正传",
        "original_title": "Forrest Gump",
        "overview": "一个智力有限但心地善良的阿拉巴马人见证并参与了一些20世纪最重要的历史事件。",
        "tagline": "世界永远不会是同一个，一旦你看到了它通过阿甘的眼睛",
        "budget": 55000000,
        "revenue": 677945399,
        "popularity": 95.2,
        "release_date": date(1994, 7, 6),
        "runtime": 142,
        "vote_average": 8.2,
        "vote_count": 22000,
        "poster_path": "/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "homepage": "https://www.paramount.com/movies/forrest-gump",
        "status": "Released",
        "original_language": "en",
        "genres": '[{"id": 18, "name": "剧情"}, {"id": 35, "name": "喜剧"}, {"id": 10749, "name": "爱情"}]',
        "keywords": '[{"id": 222, "name": "励志"}, {"id": 333, "name": "历史"}]',
        "production_companies": '[{"name": "Paramount Pictures"}]',
        "production_countries": '[{"iso_3166_1": "US", "name": "美国"}]',
        "spoken_languages": '[{"iso_639_1": "en", "name": "英语"}]',
        "director": "罗伯特·泽米吉斯",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": 550,
        "title": "搏击俱乐部",
        "original_title": "Fight Club",
        "overview": "一个失眠的办公室职员遇到了肥皂商泰勒·德顿，两人创建了一个地下搏击俱乐部。",
        "tagline": "你不是你自己的工作",
        "budget": 63000000,
        "revenue": 100853753,
        "popularity": 180.5,
        "release_date": date(1997, 10, 15),
        "runtime": 139,
        "vote_average": 8.4,
        "vote_count": 26000,
        "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "homepage": "",
        "status": "Released",
        "original_language": "en",
        "genres": '[{"id": 18, "name": "剧情"}, {"id": 53, "name": "惊悚"}]',
        "keywords": '[{"id": 100, "name": "反叛"}, {"id": 200, "name": "身份认同"}]',
        "production_companies": '[{"name": "Fox Searchlight Pictures"}]',
        "production_countries": '[{"iso_3166_1": "US", "name": "美国"}]',
        "spoken_languages": '[{"iso_639_1": "en", "name": "英语"}]',
        "director": "大卫·芬奇",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": 680,
        "title": "盗梦空间",
        "original_title": "Inception",
        "overview": "一个盗贼通过梦境共享技术来窃取公司机密，他的最新任务是在目标的梦中植入一个想法。",
        "tagline": "你的想法是他们的武器",
        "budget": 160000000,
        "revenue": 836848102,
        "popularity": 220.3,
        "release_date": date(2010, 7, 16),
        "runtime": 148,
        "vote_average": 8.4,
        "vote_count": 32000,
        "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Ber.jpg",
        "homepage": "https://www.warnerbros.com/movies/inception",
        "status": "Released",
        "original_language": "en",
        "genres": '[{"id": 28, "name": "动作"}, {"id": 878, "name": "科幻"}, {"id": 12, "name": "冒险"}]',
        "keywords": '[{"id": 300, "name": "梦境"}, {"id": 400, "name": "潜意识"}]',
        "production_companies": '[{"name": "Legendary Pictures"}]',
        "production_countries": '[{"iso_3166_1": "US", "name": "美国"}]',
        "spoken_languages": '[{"iso_639_1": "en", "name": "英语"}]',
        "director": "克里斯托弗·诺兰",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]


def get_mock_movie_by_id(movie_id: int) -> Optional[DatabaseMovie]:
    """获取模拟电影数据"""
    for movie in MOCK_MOVIES:
        if movie["id"] == movie_id:
            return DatabaseMovie(**movie)
    return None


def get_movie_by_id(movie_id: int) -> Optional[DatabaseMovie]:
    """根据ID获取电影"""
    try:
        query = "SELECT * FROM movies WHERE id = %s"
        row = Database.fetchrow(query, movie_id)
        
        if not row:
            return None
        
        return DatabaseMovie(**row)
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟数据")
        return get_mock_movie_by_id(movie_id)


def get_movies_from_db(limit: int, min_rating: float = 0) -> List[DatabaseMovie]:
    """从数据库获取电影，带fallback到模拟数据"""
    try:
        query = """
            SELECT * FROM movies 
            WHERE vote_average >= %s 
            ORDER BY RANDOM() 
            LIMIT %s
        """
        rows = Database.fetch(query, min_rating, limit)
        
        movies = []
        for row in rows:
            movies.append(DatabaseMovie(**row))
        return movies
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟数据")
        return [DatabaseMovie(**m) for m in MOCK_MOVIES[:limit]]


@router.get(
    "/random",
    response_model=PaginatedMovies,
    summary="随机推荐电影",
)
def random_movies(
    limit: int = Query(default=10, ge=1, le=50),
    min_rating: float = Query(default=6.0, description="最小评分"),
) -> PaginatedMovies:
    """获取随机推荐电影"""
    movies = get_movies_from_db(limit, min_rating)
    total = len(movies) if movies else 0
    return PaginatedMovies.from_database_movies(movies, total, 1, limit)


@router.get(
    "/{movie_id}",
    response_model=DatabaseMovie,
    summary="电影详情",
)
def get_movie_detail(
    movie_id: int,
) -> DatabaseMovie:
    """获取电影详情"""
    movie = get_movie_by_id(movie_id)
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"电影ID {movie_id} 不存在",
        )
    
    return movie


@router.get(
    "/top/rated",
    response_model=PaginatedMovies,
    summary="评分TOP电影",
)
def top_rated_movies(
    limit: int = Query(default=20, ge=1, le=50),
) -> PaginatedMovies:
    """获取评分最高的电影"""
    try:
        query = """
            SELECT * FROM movies 
            WHERE vote_average > 0 AND vote_count >= 100
            ORDER BY vote_average DESC, vote_count DESC
            LIMIT %s
        """
        rows = Database.fetch(query, limit)
        
        movies = []
        for row in rows:
            movies.append(DatabaseMovie(**row))
        
        total = len(movies) if movies else 0
        return PaginatedMovies.from_database_movies(movies, total, 1, limit)
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟数据")
        return PaginatedMovies.from_database_movies([], 0, 1, limit)


@router.get(
    "/top/popular",
    response_model=PaginatedMovies,
    summary="热度TOP电影",
)
def top_popular_movies(
    limit: int = Query(default=20, ge=1, le=50),
) -> PaginatedMovies:
    """获取热度最高的电影"""
    try:
        query = """
            SELECT * FROM movies 
            WHERE popularity > 0
            ORDER BY popularity DESC
            LIMIT %s
        """
        rows = Database.fetch(query, limit)
        
        movies = []
        for row in rows:
            movies.append(DatabaseMovie(**row))
        
        total = len(movies) if movies else 0
        return PaginatedMovies.from_database_movies(movies, total, 1, limit)
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟数据")
        return PaginatedMovies.from_database_movies([], 0, 1, limit)


@router.get(
    "/top/box-office",
    response_model=PaginatedMovies,
    summary="票房TOP电影",
)
def top_box_office_movies(
    limit: int = Query(default=20, ge=1, le=50),
) -> PaginatedMovies:
    """获取票房最高的电影"""
    try:
        query = """
            SELECT * FROM movies 
            WHERE revenue > 0
            ORDER BY revenue DESC
            LIMIT %s
        """
        rows = Database.fetch(query, limit)
        
        movies = []
        for row in rows:
            movies.append(DatabaseMovie(**row))
        
        total = len(movies) if movies else 0
        return PaginatedMovies.from_database_movies(movies, total, 1, limit)
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟数据")
        return PaginatedMovies.from_database_movies([], 0, 1, limit)


@router.get(
    "/stats/summary",
    response_model=MovieStats,
    summary="电影统计信息",
)
def get_movie_stats() -> MovieStats:
    """获取电影库统计信息"""
    try:
        total_result = Database.fetchrow("SELECT COUNT(*) as total FROM movies")
        total = total_result['total'] if total_result else 0
        
        avg_rating_result = Database.fetchrow("""
            SELECT AVG(vote_average) as avg_rating FROM movies WHERE vote_average > 0
        """)
        avg_rating = avg_rating_result['avg_rating'] if avg_rating_result else 0
        
        box_office_result = Database.fetchrow("""
            SELECT SUM(revenue) as total_box_office FROM movies WHERE revenue > 0
        """)
        total_box_office = box_office_result['total_box_office'] if box_office_result else 0
        
        year_rows = Database.fetch("""
            SELECT EXTRACT(YEAR FROM release_date) as year, COUNT(*) as count
            FROM movies WHERE release_date IS NOT NULL
            GROUP BY EXTRACT(YEAR FROM release_date)
            ORDER BY year DESC LIMIT 20
        """)
        by_year = {int(row['year']): row['count'] for row in year_rows if row['year']}
        
        language_rows = Database.fetch("""
            SELECT original_language, COUNT(*) as count
            FROM movies WHERE original_language IS NOT NULL
            GROUP BY original_language ORDER BY count DESC LIMIT 10
        """)
        by_language = {row['original_language']: row['count'] for row in language_rows}
        
        return MovieStats(
            total=total,
            average_rating=round(float(avg_rating) if avg_rating else 0, 2),
            total_box_office=int(total_box_office) if total_box_office else 0,
            genres={"total_with_genres": 0},
            by_year=by_year,
            by_language=by_language,
        )
    except Exception as e:
        print(f"数据库查询失败: {e}，返回模拟统计")
        return MovieStats(
            total=len(MOCK_MOVIES),
            average_rating=8.2,
            total_box_office=5000000000,
            genres={"total_with_genres": len(MOCK_MOVIES)},
            by_year={2019: 1, 2010: 1, 1997: 1, 1994: 1, 1977: 1},
            by_language={"en": len(MOCK_MOVIES)},
        )


@router.get(
    "",
    response_model=PaginatedMovies,
    summary="电影列表",
)
def list_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedMovies:
    """获取电影列表"""
    movies = get_movies_from_db(page_size)
    return PaginatedMovies.from_database_movies(movies, len(movies), page, page_size)