"""
影评系统API
"""

from __future__ import annotations

from typing import Annotated, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, text
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewStats,
    ReviewFilters,
    PaginatedReviews,
    ReviewSortBy,
    VoteReviewRequest,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


# 创建reviews表的SQL语句
CREATE_REVIEWS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    rating DECIMAL(3,1) NOT NULL CHECK (rating >= 0 AND rating <= 10),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(100) DEFAULT '匿名用户',
    helpful_count INTEGER DEFAULT 0 CHECK (helpful_count >= 0),
    not_helpful_count INTEGER DEFAULT 0 CHECK (not_helpful_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_reviews_movie_id (movie_id),
    INDEX idx_reviews_rating (rating),
    INDEX idx_reviews_created_at (created_at),
    INDEX idx_reviews_helpful (helpful_count)
);
"""


async def ensure_reviews_table_exists(db: AsyncSession):
    """确保reviews表存在"""
    try:
        await db.execute(text(CREATE_REVIEWS_TABLE_SQL))
        await db.commit()
    except Exception as e:
        # 表可能已经存在
        await db.rollback()


async def get_review_by_id(db: AsyncSession, review_id: int) -> Optional[dict]:
    """根据ID获取影评"""
    query = text("""
        SELECT r.*, m.title as movie_title, m.poster_path
        FROM reviews r
        LEFT JOIN movies m ON r.movie_id = m.id
        WHERE r.id = :review_id
    """)
    
    result = await db.execute(query, {"review_id": review_id})
    row = result.fetchone()
    
    if not row:
        return None
    
    return dict(row._mapping)


async def search_reviews(
    db: AsyncSession,
    filters: ReviewFilters,
) -> tuple[List[dict], int]:
    """搜索影评"""
    # 构建基础查询
    base_query = """
        SELECT r.*, m.title as movie_title, m.poster_path
        FROM reviews r
        LEFT JOIN movies m ON r.movie_id = m.id
        WHERE 1=1
    """
    
    params = {}
    conditions = []
    
    # 电影ID筛选
    if filters.movie_id:
        conditions.append("r.movie_id = :movie_id")
        params["movie_id"] = filters.movie_id
    
    # 评分范围
    if filters.min_rating is not None:
        conditions.append("r.rating >= :min_rating")
        params["min_rating"] = filters.min_rating
    
    if filters.max_rating is not None:
        conditions.append("r.rating <= :max_rating")
        params["max_rating"] = filters.max_rating
    
    # 作者筛选
    if filters.author:
        conditions.append("r.author ILIKE :author")
        params["author"] = f"%{filters.author}%"
    
    # 添加条件到查询
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    # 排序
    order_mapping = {
        ReviewSortBy.NEWEST: "r.created_at DESC",
        ReviewSortBy.MOST_HELPFUL: "r.helpful_count DESC, r.created_at DESC",
        ReviewSortBy.HIGHEST_RATING: "r.rating DESC, r.created_at DESC",
        ReviewSortBy.LOWEST_RATING: "r.rating ASC, r.created_at DESC",
    }
    order_clause = order_mapping.get(filters.sort_by, "r.created_at DESC")
    base_query += f" ORDER BY {order_clause}"
    
    # 分页
    offset = (filters.page - 1) * filters.page_size
    base_query += " LIMIT :limit OFFSET :offset"
    params["limit"] = filters.page_size
    params["offset"] = offset
    
    # 执行查询
    result = await db.execute(text(base_query), params)
    rows = result.fetchall()
    
    # 转换为字典列表
    reviews = []
    for row in rows:
        reviews.append(dict(row._mapping))
    
    # 获取总数
    count_query = """
        SELECT COUNT(*) as total FROM reviews r
        WHERE 1=1
    """
    if conditions:
        count_query += " AND " + " AND ".join(conditions)
    
    # 移除分页参数
    count_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}
    count_result = await db.execute(text(count_query), count_params)
    total = count_result.scalar()
    
    return reviews, total


async def get_review_stats(db: AsyncSession, movie_id: int) -> ReviewStats:
    """获取影评统计信息"""
    # 确保表存在
    await ensure_reviews_table_exists(db)
    
    # 基础统计
    stats_query = text("""
        SELECT 
            COUNT(*) as total_reviews,
            AVG(rating) as average_rating,
            SUM(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END) as recent_reviews_count
        FROM reviews
        WHERE movie_id = :movie_id
    """)
    
    result = await db.execute(stats_query, {"movie_id": movie_id})
    row = result.fetchone()
    
    if not row:
        return ReviewStats(
            movie_id=movie_id,
            total_reviews=0,
            average_rating=0.0,
            rating_distribution={},
            recent_reviews_count=0,
        )
    
    total_reviews = row.total_reviews or 0
    average_rating = float(row.average_rating or 0.0)
    recent_reviews_count = row.recent_reviews_count or 0
    
    # 评分分布
    distribution_query = text("""
        SELECT 
            CASE 
                WHEN rating >= 9 THEN '9-10'
                WHEN rating >= 8 THEN '8-9'
                WHEN rating >= 7 THEN '7-8'
                WHEN rating >= 6 THEN '6-7'
                WHEN rating >= 5 THEN '5-6'
                ELSE '0-5'
            END as rating_range,
            COUNT(*) as count
        FROM reviews
        WHERE movie_id = :movie_id
        GROUP BY rating_range
        ORDER BY rating_range DESC
    """)
    
    result = await db.execute(distribution_query, {"movie_id": movie_id})
    rows = result.fetchall()
    
    rating_distribution = {}
    for row in rows:
        rating_distribution[row.rating_range] = row.count
    
    return ReviewStats(
        movie_id=movie_id,
        total_reviews=total_reviews,
        average_rating=round(average_rating, 1),
        rating_distribution=rating_distribution,
        recent_reviews_count=recent_reviews_count,
    )


@router.get(
    "",
    response_model=PaginatedReviews,
    summary="获取影评列表",
)
async def list_reviews(
    movie_id: Optional[int] = Query(None, description="电影ID"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    max_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    author: Optional[str] = None,
    sort_by: ReviewSortBy = Query(ReviewSortBy.NEWEST, description="排序方式"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> PaginatedReviews:
    """获取影评列表，支持筛选和排序"""
    
    # 确保表存在
    await ensure_reviews_table_exists(db)
    
    # 创建过滤器
    filters = ReviewFilters(
        movie_id=movie_id,
        min_rating=min_rating,
        max_rating=max_rating,
        author=author,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    
    # 搜索影评
    reviews, total = await search_reviews(db, filters)
    
    # 转换为响应模型
    review_responses = []
    for review in reviews:
        # 构建海报URL
        poster_url = ""
        if review.get("poster_path"):
            poster_url = f"https://image.tmdb.org/t/p/w500{review['poster_path']}"
        
        review_responses.append(ReviewResponse(
            id=review["id"],
            movie_id=review["movie_id"],
            rating=float(review["rating"]),
            title=review["title"],
            content=review["content"],
            author=review["author"],
            helpful_count=review["helpful_count"],
            not_helpful_count=review["not_helpful_count"],
            created_at=review["created_at"],
            updated_at=review["updated_at"],
            movie_title=review.get("movie_title"),
            movie_poster_url=poster_url,
        ))
    
    return PaginatedReviews.from_reviews(review_responses, total, page, page_size)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="获取影评详情",
)
async def get_review(
    review_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> ReviewResponse:
    """获取影评详情"""
    
    # 确保表存在
    await ensure_reviews_table_exists(db)
    
    review = await get_review_by_id(db, review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"影评ID {review_id} 不存在",
        )
    
    # 构建海报URL
    poster_url = ""
    if review.get("poster_path"):
        poster_url = f"https://image.tmdb.org/t/p/w500{review['poster_path']}"
    
    return ReviewResponse(
        id=review["id"],
        movie_id=review["movie_id"],
        rating=float(review["rating"]),
        title=review["title"],
        content=review["content"],
        author=review["author"],
        helpful_count=review["helpful_count"],
        not_helpful_count=review["not_helpful_count"],
        created_at=review["created_at"],
        updated_at=review["updated_at"],
        movie_title=review.get("movie_title"),
        movie_poster_url=poster_url,
    )


@router.post(
    "",
    response_model=ReviewResponse,
    summary="创建影评",
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review_data: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> ReviewResponse:
    """创建新影评"""
    
    # 确保表存在
    await ensure_reviews_table_exists(db)
    
    # 检查电影是否存在
    movie_query = text("SELECT id, title, poster_path FROM movies WHERE id = :movie_id")
    movie_result = await db.execute(movie_query, {"movie_id": review_data.movie_id})
    movie = movie_result.fetchone()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"电影ID {review_data.movie_id} 不存在",
        )
    
    # 插入影评
    insert_query = text("""
        INSERT INTO reviews (
            movie_id, rating, title, content, author, 
            helpful_count, not_helpful_count
        ) VALUES (
            :movie_id, :rating, :title, :content, :author,
            :helpful_count, :not_helpful_count
        )
        RETURNING id, created_at, updated_at
    """)
    
    result = await db.execute(insert_query, {
        "movie_id": review_data.movie_id,
        "rating": review_data.rating,
        "title": review_data.title,
        "content": review_data.content,
        "author": review_data.author,
        "helpful_count": review_data.helpful_count,
        "not_helpful_count": review_data.not_helpful_count,
    })
    
    await db.commit()
    
    row = result.fetchone()
    
    # 构建海报URL
    poster_url = ""
    if movie.poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{movie.poster_path}"
    
    return ReviewResponse(
        id=row.id,
        movie_id=review_data.movie_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        author=review_data.author,
        helpful_count=review_data.helpful_count,
        not_helpful_count=review_data.not_helpful_count,
        created_at=row.created_at,
        updated_at=row.updated_at,
        movie_title=movie.title,
        movie_poster_url=poster_url,
    )


@router.get(
    "/stats/{movie_id}",
    response_model=ReviewStats,
    summary="获取影评统计信息",
)
async def get_movie_review_stats(
    movie_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> ReviewStats:
    """获取电影的影评统计信息"""
    return await get_review_stats(db, movie_id)


@router.post(
    "/{review_id}/vote",
    response_model=ReviewResponse,
    summary="投票影评（有用/无用）",
)
async def vote_review(
    review_id: int,
    vote_data: VoteReviewRequest,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> ReviewResponse:
    """为影评投票（有用或无用）"""
    
    # 确保表存在
    await ensure_reviews_table_exists(db)
    
    # 检查影评是否存在
    review = await get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"影评ID {review_id} 不存在",
        )
    
    # 更新投票数
    if vote_data.helpful:
        update_query = text("""
            UPDATE reviews 
            SET helpful_count = helpful_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :review_id
            RETURNING *
        """)
    else:
        update_query = text("""
            UPDATE reviews 
            SET not_helpful_count = not_helpful_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :review_id
            RETURNING *
        """)
    
    result = await db.execute(update_query, {"review_id": review_id})
    await db.commit()
    
    updated_review = result.fetchone()
    
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新影评投票失败",
        )
    
    # 获取电影信息
    movie_query = text("SELECT title, poster_path FROM movies WHERE id = :movie_id")
    movie_result = await db.execute(movie_query, {"movie_id": review["movie_id"]})
    movie = movie_result.fetchone()
    
    # 构建海报URL
    poster_url = ""
    if movie and movie.poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{movie.poster_path}"
    
    return ReviewResponse(
        id=updated_review.id,
        movie_id=updated_review.movie_id,
        rating=float(updated_review.rating),
        title=updated_review.title,
        content=updated_review.content,
        author=updated_review.author,
        helpful_count=updated_review.helpful_count,
        not_helpful_count=updated_review.not_helpful_count,
        created_at=updated_review.created_at,
        updated_at=updated_review.updated_at,
        movie_title=movie.title if movie else None,
        movie_poster_url=poster_url,
    )