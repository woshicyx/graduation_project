"""
用户相关API：收藏、浏览历史、个人中心等
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from ..core.db import get_db
from ..models_extended import User, UserFavorite, UserSearchHistory, UserWatchHistory, UserRating
from ..schemas_extended import (
    UserProfileResponse, FavoriteRequest, FavoriteResponse, 
    FavoriteListResponse, WatchHistoryResponse, SearchHistoryResponse,
    UserStatsResponse
)

router = APIRouter(prefix="/users", tags=["用户"])

async def get_current_user_from_token(
    token: str = Depends(lambda: None),  # 简化处理，实际应从header获取
    db: Session = Depends(get_db)
) -> Optional[User]:
    """从令牌获取当前用户（简化版）"""
    # 在实际应用中，这里应该解析JWT令牌
    # 为了简化，我们暂时支持session_id或user_id参数
    return None

@router.get("/me/favorites", response_model=FavoriteListResponse)
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可用）"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user_from_token)  # 实际需要认证
):
    """获取用户的收藏列表"""
    # 简化：暂时支持user_id参数
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 获取收藏总数
    total_count = db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.is_liked == True
    ).scalar() or 0
    
    # 获取收藏列表（连接movies表获取电影信息）
    favorites_query = db.query(UserFavorite, func.jsonb_build_object(
        'id', UserFavorite.id,
        'user_id', UserFavorite.user_id,
        'movie_id', UserFavorite.movie_id,
        'is_liked', UserFavorite.is_liked,
        'notes', UserFavorite.notes,
        'created_at', UserFavorite.created_at,
        'updated_at', UserFavorite.updated_at
    )).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.is_liked == True
    ).order_by(desc(UserFavorite.created_at))
    
    # 分页
    offset = (page - 1) * page_size
    favorites_items = favorites_query.offset(offset).limit(page_size).all()
    
    # 构建响应
    favorites = []
    for fav_item in favorites_items:
        fav_dict = fav_item[1]  # 获取JSONB对象
        # 获取电影信息（这里需要连接movies表，简化处理）
        movie_info = {}
        try:
            # 执行原始SQL查询获取电影信息
            movie_result = db.execute(
                "SELECT id, title, poster_path, release_date, vote_average FROM movies WHERE id = :movie_id",
                {"movie_id": fav_dict['movie_id']}
            ).fetchone()
            
            if movie_result:
                movie_info = {
                    'id': movie_result[0],
                    'title': movie_result[1],
                    'poster_path': movie_result[2],
                    'release_date': movie_result[3],
                    'vote_average': float(movie_result[4]) if movie_result[4] else 0.0
                }
        except Exception as e:
            # 忽略错误，movie_info为空
            pass
        
        fav_dict['movie'] = movie_info
        favorites.append(fav_dict)
    
    return FavoriteListResponse(
        favorites=favorites,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=(total_count + page_size - 1) // page_size
    )

@router.post("/me/favorites/{movie_id}", response_model=FavoriteResponse)
async def add_to_favorites(
    movie_id: int,
    request: FavoriteRequest,
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """添加电影到收藏"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证电影是否存在
    movie_result = db.execute(
        "SELECT id FROM movies WHERE id = :movie_id",
        {"movie_id": movie_id}
    ).fetchone()
    
    if not movie_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    # 检查是否已收藏
    existing_favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.movie_id == movie_id
    ).first()
    
    if existing_favorite:
        # 更新现有收藏
        existing_favorite.is_liked = request.action == "like"
        existing_favorite.notes = request.notes
        existing_favorite.updated_at = datetime.utcnow()
    else:
        # 创建新收藏
        favorite = UserFavorite(
            user_id=user_id,
            movie_id=movie_id,
            is_liked=request.action == "like",
            tags=request.tags or [],
            notes=request.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(favorite)
    
    db.commit()
    
    # 获取更新后的收藏记录
    if existing_favorite:
        favorite = existing_favorite
    else:
        favorite = db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.movie_id == movie_id
        ).first()
    
    # 获取电影信息
    movie_result = db.execute(
        "SELECT id, title, poster_path FROM movies WHERE id = :movie_id",
        {"movie_id": movie_id}
    ).fetchone()
    
    movie_info = {}
    if movie_result:
        movie_info = {
            'id': movie_result[0],
            'title': movie_result[1],
            'poster_path': movie_result[2]
        }
    
    return FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        movie_id=favorite.movie_id,
        is_liked=favorite.is_liked,
        notes=favorite.notes,
        movie=movie_info,
        created_at=favorite.created_at,
        updated_at=favorite.updated_at
    )

@router.delete("/me/favorites/{movie_id}")
async def remove_from_favorites(
    movie_id: int,
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """从收藏中移除电影"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 查找收藏记录
    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.movie_id == movie_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在"
        )
    
    # 软删除：标记为不喜欢
    favorite.is_liked = False
    favorite.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "已从收藏中移除"}

@router.get("/me/watch-history", response_model=List[WatchHistoryResponse])
async def get_watch_history(
    limit: int = Query(50, ge=1, le=200, description="返回记录数量"),
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """获取用户的浏览历史"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 获取浏览历史记录
    history_query = db.query(UserWatchHistory).filter(
        UserWatchHistory.user_id == user_id
    ).order_by(desc(UserWatchHistory.created_at))
    
    history_items = history_query.limit(limit).all()
    
    # 构建响应
    history_list = []
    for item in history_items:
        # 获取电影信息
        movie_result = db.execute(
            "SELECT id, title, poster_path, release_date FROM movies WHERE id = :movie_id",
            {"movie_id": item.movie_id}
        ).fetchone()
        
        movie_info = {}
        if movie_result:
            movie_info = {
                'id': movie_result[0],
                'title': movie_result[1],
                'poster_path': movie_result[2],
                'release_date': movie_result[3]
            }
        
        history_list.append(WatchHistoryResponse(
            id=item.id,
            user_id=item.user_id,
            movie_id=item.movie_id,
            movie=movie_info,
            watch_duration=item.watch_duration or 0,
            progress=item.progress or 0.0,
            interaction_score=item.interaction_score or 1,
            created_at=item.created_at
        ))
    
    return history_list

@router.post("/me/watch-history/{movie_id}")
async def add_watch_history(
    movie_id: int,
    watch_duration: Optional[int] = Query(None, description="观看时长（秒）"),
    progress: Optional[float] = Query(None, ge=0.0, le=1.0, description="观看进度（0-1）"),
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """记录用户浏览历史"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 验证电影是否存在
    movie_result = db.execute(
        "SELECT id FROM movies WHERE id = :movie_id",
        {"movie_id": movie_id}
    ).fetchone()
    
    if not movie_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    # 检查是否有历史记录
    history = db.query(UserWatchHistory).filter(
        UserWatchHistory.user_id == user_id,
        UserWatchHistory.movie_id == movie_id
    ).first()
    
    if history:
        # 更新现有记录
        if watch_duration is not None:
            history.watch_duration = watch_duration
        if progress is not None:
            history.progress = progress
        history.interaction_score = (history.interaction_score or 1) + 1
        history.created_at = datetime.utcnow()
    else:
        # 创建新记录
        history = UserWatchHistory(
            user_id=user_id,
            movie_id=movie_id,
            watch_duration=watch_duration or 0,
            progress=progress or 0.0,
            interaction_score=1,
            created_at=datetime.utcnow()
        )
        db.add(history)
    
    db.commit()
    
    return {"message": "浏览历史已记录"}

@router.get("/me/search-history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = Query(20, ge=1, le=100, description="返回记录数量"),
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    session_id: Optional[str] = Query(None, description="会话ID（游客模式）"),
    db: Session = Depends(get_db)
):
    """获取用户的搜索历史"""
    # 支持用户ID或会话ID
    if not user_id and not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需要用户ID或会话ID"
        )
    
    # 构建查询条件
    query_filter = []
    if user_id:
        query_filter.append(UserSearchHistory.user_id == user_id)
    if session_id:
        query_filter.append(UserSearchHistory.session_id == session_id)
    
    # 获取搜索历史
    history_query = db.query(UserSearchHistory).filter(
        or_(*query_filter)
    ).order_by(desc(UserSearchHistory.created_at))
    
    history_items = history_query.limit(limit).all()
    
    # 构建响应
    history_list = []
    for item in history_items:
        history_list.append(SearchHistoryResponse(
            id=item.id,
            user_id=item.user_id,
            session_id=item.session_id,
            query=item.query,
            search_type=item.search_type or "keyword",
            filters=item.filters or {},
            result_count=item.result_count or 0,
            click_count=item.click_count or 0,
            is_successful=item.is_successful or True,
            created_at=item.created_at
        ))
    
    return history_list

@router.post("/me/search-history")
async def add_search_history(
    query: str = Query(..., min_length=1, max_length=500, description="搜索词"),
    search_type: str = Query("keyword", description="搜索类型"),
    filters: Dict[str, Any] = Query({}, description="筛选条件"),
    result_count: int = Query(0, ge=0, description="结果数量"),
    result_ids: List[int] = Query([], description="结果ID列表"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    session_id: Optional[str] = Query(None, description="会话ID（游客模式）"),
    db: Session = Depends(get_db)
):
    """记录用户搜索历史"""
    # 支持用户ID或会话ID
    if not user_id and not session_id:
        # 生成随机会话ID（简化处理）
        import uuid
        session_id = str(uuid.uuid4())[:20]
    
    # 创建搜索历史记录
    history = UserSearchHistory(
        user_id=user_id,
        session_id=session_id,
        query=query,
        search_type=search_type,
        filters=filters,
        result_count=result_count,
        result_ids=result_ids,
        click_count=0,
        is_successful=result_count > 0,
        created_at=datetime.utcnow()
    )
    
    db.add(history)
    db.commit()
    
    return {
        "message": "搜索历史已记录",
        "session_id": session_id if not user_id else None
    }

@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """获取用户统计信息"""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要用户认证"
        )
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 统计各类数据
    watch_count = db.query(func.count(UserWatchHistory.id)).filter(
        UserWatchHistory.user_id == user_id
    ).scalar() or 0
    
    favorite_count = db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.is_liked == True
    ).scalar() or 0
    
    rating_count = db.query(func.count(UserRating.id)).filter(
        UserRating.user_id == user_id
    ).scalar() or 0
    
    search_count = db.query(func.count(UserSearchHistory.id)).filter(
        UserSearchHistory.user_id == user_id
    ).scalar() or 0
    
    # 计算活跃度分数（简化版）
    activity_score = (
        watch_count * 0.3 +
        favorite_count * 0.4 +
        rating_count * 0.2 +
        search_count * 0.1
    )
    
    # 获取最近活动时间
    recent_activity = None
    
    # 检查最近收藏
    latest_favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.is_liked == True
    ).order_by(desc(UserFavorite.updated_at)).first()
    
    if latest_favorite:
        recent_activity = latest_favorite.updated_at
    
    return UserStatsResponse(
        user_id=user_id,
        watch_count=watch_count,
        favorite_count=favorite_count,
        rating_count=rating_count,
        search_count=search_count,
        activity_score=round(activity_score, 2),
        recent_activity=recent_activity,
        member_since=user.created_at
    )

@router.get("/check-favorite/{movie_id}")
async def check_favorite_status(
    movie_id: int,
    user_id: Optional[int] = Query(None, description="用户ID（仅测试用）"),
    db: Session = Depends(get_db)
):
    """检查用户是否收藏了某部电影"""
    if not user_id:
        return {"is_favorited": False, "is_liked": False}
    
    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == user_id,
        UserFavorite.movie_id == movie_id
    ).first()
    
    if not favorite:
        return {"is_favorited": False, "is_liked": False}
    
    return {
        "is_favorited": True,
        "is_liked": favorite.is_liked,
        "notes": favorite.notes,
        "updated_at": favorite.updated_at
    }