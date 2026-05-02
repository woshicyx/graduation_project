"""
用户相关API：收藏、浏览历史、个人中心等
使用JWT token认证
"""

from __future__ import annotations

import jwt
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from app.core.config import settings
from app.core.db import Database, get_db
from app.models import User, UserFavorite, UserSearchHistory, UserWatchHistory, UserRating
from app.schemas import (
    UserProfileResponse, FavoriteRequest, FavoriteResponse, 
    FavoriteListResponse, WatchHistoryResponse, SearchHistoryResponse,
    UserStatsResponse, SearchHistoryCreate, MovieListItem
)

router = APIRouter(prefix="/users", tags=["用户"])
security = HTTPBearer(auto_error=False)

# JWT配置
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从Bearer token获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
            )
        
        # 获取用户信息
        user = Database.fetchrow(
            "SELECT * FROM users WHERE id = %s AND is_active = true",
            int(user_id)
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )


@router.get("/me/favorites", response_model=FavoriteListResponse)
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user_from_token),
):
    """获取当前用户的收藏列表"""
    user_id = current_user['id']
    
    # 获取收藏总数
    total_count_result = Database.fetchrow(
        "SELECT COUNT(*) as cnt FROM user_favorites WHERE user_id = %s AND is_liked = true",
        user_id
    )
    total_count = total_count_result['cnt'] if total_count_result else 0
    
    # 获取收藏列表
    offset = (page - 1) * page_size
    favorites_query = """
        SELECT uf.id, uf.user_id, uf.movie_id, uf.is_liked, uf.notes, 
               uf.created_at, uf.updated_at,
               m.id as movie_id, m.title, m.poster_path, m.release_date, m.vote_average
        FROM user_favorites uf
        LEFT JOIN movies m ON uf.movie_id = m.id
        WHERE uf.user_id = %s AND uf.is_liked = true
        ORDER BY uf.created_at DESC
        LIMIT %s OFFSET %s
    """
    
    favorites_rows = Database.fetch(favorites_query, user_id, page_size, offset)
    
    favorites = []
    for row in favorites_rows:
        movie_info = None
        if row['id'] and row.get('title'):  # movie exists
            movie_info = MovieListItem(
                id=row['id'],
                title=row['title'] or "未知",
                poster_path=row['poster_path'],
                vote_average=float(row['vote_average']) if row['vote_average'] else None,
                popularity=None,
                release_date=row['release_date'],
                genres=[],
                director=None
            )
        
        favorites.append(FavoriteResponse(
            id=row['id'],
            user_id=row['user_id'],
            movie_id=row['movie_id'],
            is_liked=bool(row['is_liked']),
            tags=[],
            notes=row.get('notes'),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            movie=movie_info
        ))
    
    return FavoriteListResponse(
        favorites=favorites,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size if total_count > 0 else 0
    )


@router.post("/me/favorites/{movie_id}", response_model=FavoriteResponse)
async def add_to_favorites(
    movie_id: int,
    request: FavoriteRequest,
    current_user: dict = Depends(get_current_user_from_token),
):
    """添加/更新电影收藏"""
    user_id = current_user['id']
    
    # 验证电影是否存在
    movie_result = Database.fetchrow(
        "SELECT id, title, poster_path FROM movies WHERE id = %s",
        movie_id
    )
    
    if not movie_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    # 检查是否已收藏
    existing_favorite = Database.fetchrow(
        "SELECT * FROM user_favorites WHERE user_id = %s AND movie_id = %s",
        user_id, movie_id
    )
    
    now = datetime.utcnow()
    
    if existing_favorite:
        # 更新现有收藏
        Database.execute(
            """UPDATE user_favorites SET is_liked = %s, notes = %s, updated_at = %s 
               WHERE user_id = %s AND movie_id = %s""",
            request.action == "like", request.notes, now, user_id, movie_id
        )
        favorite_id = existing_favorite['id']
    else:
        # 创建新收藏
        Database.execute(
            """INSERT INTO user_favorites (user_id, movie_id, is_liked, notes, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            user_id, movie_id, request.action == "like", request.notes, now, now
        )
        # 获取新创建的记录ID
        new_favorite = Database.fetchrow(
            "SELECT id FROM user_favorites WHERE user_id = %s AND movie_id = %s",
            user_id, movie_id
        )
        favorite_id = new_favorite['id'] if new_favorite else 0
    
    return FavoriteResponse(
        id=favorite_id,
        user_id=user_id,
        movie_id=movie_id,
        is_liked=request.action == "like",
        notes=request.notes,
        movie={
            'id': movie_result['id'],
            'title': movie_result['title'],
            'poster_path': movie_result['poster_path']
        },
        created_at=now,
        updated_at=now
    )


@router.delete("/me/favorites/{movie_id}")
async def remove_from_favorites(
    movie_id: int,
    current_user: dict = Depends(get_current_user_from_token),
):
    """从收藏中移除电影"""
    user_id = current_user['id']
    
    # 查找收藏记录
    favorite = Database.fetchrow(
        "SELECT id FROM user_favorites WHERE user_id = %s AND movie_id = %s",
        user_id, movie_id
    )
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在"
        )
    
    # 软删除：标记为不喜欢
    Database.execute(
        "UPDATE user_favorites SET is_liked = false, updated_at = %s WHERE user_id = %s AND movie_id = %s",
        datetime.utcnow(), user_id, movie_id
    )
    
    return {"message": "已从收藏中移除"}


@router.get("/me/watch-history", response_model=List[WatchHistoryResponse])
async def get_watch_history(
    limit: int = Query(50, ge=1, le=200, description="返回记录数量"),
    current_user: dict = Depends(get_current_user_from_token),
):
    """获取用户的浏览历史"""
    user_id = current_user['id']
    
    # 获取浏览历史记录
    history_rows = Database.fetch(
        """SELECT uwh.id, uwh.user_id, uwh.movie_id, uwh.watch_duration, 
                  uwh.progress, uwh.interaction_score, uwh.created_at,
                  m.id as m_id, m.title, m.poster_path, m.release_date
           FROM user_watch_history uwh
           LEFT JOIN movies m ON uwh.movie_id = m.id
           WHERE uwh.user_id = %s
           ORDER BY uwh.created_at DESC
           LIMIT %s""",
        user_id, limit
    )
    
    history_list = []
    for row in history_rows:
        movie_info = None
        if row.get('m_id') and row.get('title'):
            movie_info = MovieListItem(
                id=row['m_id'],
                title=row['title'],
                poster_path=row['poster_path'],
                release_date=row['release_date']
            )
        
        history_list.append(WatchHistoryResponse(
            id=row['id'],
            user_id=row['user_id'],
            movie_id=row['movie_id'],
            watch_date=row['created_at'],
            watch_duration=row.get('watch_duration') or 0,
            progress=row.get('progress') or 0.0,
            interaction_score=row.get('interaction_score') or 1,
            created_at=row['created_at'],
            movie=movie_info
        ))
    
    return history_list


@router.post("/me/watch-history/{movie_id}")
async def add_watch_history(
    movie_id: int,
    watch_duration: Optional[int] = Query(None, description="观看时长（秒）"),
    progress: Optional[float] = Query(None, ge=0.0, le=1.0, description="观看进度（0-1）"),
    current_user: dict = Depends(get_current_user_from_token),
):
    """记录用户浏览历史"""
    user_id = current_user['id']
    
    # 验证电影是否存在
    movie_result = Database.fetchrow(
        "SELECT id FROM movies WHERE id = %s",
        movie_id
    )
    
    if not movie_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    # 检查是否有历史记录
    history = Database.fetchrow(
        "SELECT * FROM user_watch_history WHERE user_id = %s AND movie_id = %s",
        user_id, movie_id
    )
    
    now = datetime.utcnow()
    
    if history:
        # 更新现有记录
        update_fields = ["created_at = %s"]
        update_values = [now]
        
        if watch_duration is not None:
            update_fields.append("watch_duration = %s")
            update_values.append(watch_duration)
        if progress is not None:
            update_fields.append("progress = %s")
            update_values.append(progress)
        
        update_fields.append("interaction_score = interaction_score + 1")
        update_values.extend([user_id, movie_id])
        
        Database.execute(
            f"UPDATE user_watch_history SET {', '.join(update_fields)} WHERE user_id = %s AND movie_id = %s",
            *update_values
        )
    else:
        # 创建新记录
        Database.execute(
            """INSERT INTO user_watch_history (user_id, movie_id, watch_duration, progress, interaction_score, created_at)
               VALUES (%s, %s, %s, %s, 1, %s)""",
            user_id, movie_id, watch_duration or 0, progress or 0.0, now
        )
    
    return {"message": "浏览历史已记录"}


@router.post("/me/search-history/{movie_id}")
async def add_search_history(
    movie_id: int,
    query: Optional[str] = Query(None, description="搜索关键词"),
    current_user: dict = Depends(get_current_user_from_token),
):
    """记录用户从搜索结果点击的电影"""
    user_id = current_user['id']
    
    # 验证电影是否存在
    movie_result = Database.fetchrow(
        "SELECT id, title FROM movies WHERE id = %s",
        movie_id
    )
    
    if not movie_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    now = datetime.utcnow()
    
    # 检查是否有搜索历史记录
    search_history = Database.fetchrow(
        "SELECT * FROM user_search_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
        user_id
    )
    
    if search_history:
        # 更新现有记录，增加点击次数
        click_count = search_history.get('click_count', 0) + 1
        Database.execute(
            """UPDATE user_search_history 
               SET click_count = %s, created_at = %s
               WHERE id = %s""",
            click_count, now, search_history['id']
        )
    else:
        # 创建新搜索历史记录（记录点击的电影）
        Database.execute(
            """INSERT INTO user_search_history 
               (user_id, query, result_count, result_ids, click_count, created_at)
               VALUES (%s, %s, 1, %s, 1, %s)""",
            user_id, query or f"电影:{movie_result['title']}", 
            f"[{movie_id}]", now
        )
    
    return {"message": "搜索历史已记录"}


@router.get("/check-favorite/{movie_id}")
async def check_favorite_status(
    movie_id: int,
    current_user: dict = Depends(get_current_user_from_token),
):
    """检查用户是否收藏了某部电影"""
    user_id = current_user['id']
    
    favorite = Database.fetchrow(
        "SELECT * FROM user_favorites WHERE user_id = %s AND movie_id = %s",
        user_id, movie_id
    )
    
    if not favorite:
        return {"is_favorited": False, "is_liked": False}
    
    return {
        "is_favorited": True,
        "is_liked": favorite['is_liked'],
        "notes": favorite.get('notes'),
        "updated_at": favorite.get('updated_at')
    }


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: dict = Depends(get_current_user_from_token),
):
    """获取用户统计信息"""
    user_id = current_user['id']
    
    # 统计各类数据
    watch_count = Database.fetchone(
        "SELECT COUNT(*) FROM user_watch_history WHERE user_id = %s",
        user_id
    )[0] or 0
    
    favorite_count = Database.fetchone(
        "SELECT COUNT(*) FROM user_favorites WHERE user_id = %s AND is_liked = true",
        user_id
    )[0] or 0
    
    rating_count = Database.fetchone(
        "SELECT COUNT(*) FROM user_ratings WHERE user_id = %s",
        user_id
    )[0] or 0
    
    search_count = Database.fetchone(
        "SELECT COUNT(*) FROM user_search_history WHERE user_id = %s",
        user_id
    )[0] or 0
    
    # 计算活跃度分数
    activity_score = (
        watch_count * 0.3 +
        favorite_count * 0.4 +
        rating_count * 0.2 +
        search_count * 0.1
    )
    
    # 获取最近活动时间
    recent_activity = None
    latest_favorite = Database.fetchrow(
        "SELECT updated_at FROM user_favorites WHERE user_id = %s AND is_liked = true ORDER BY updated_at DESC LIMIT 1",
        user_id
    )
    if latest_favorite:
        recent_activity = latest_favorite['updated_at']
    
    return UserStatsResponse(
        user_id=user_id,
        watch_count=watch_count,
        favorite_count=favorite_count,
        rating_count=rating_count,
        search_count=search_count,
        activity_score=round(activity_score, 2),
        recent_activity=recent_activity,
        member_since=current_user['created_at']
    )
