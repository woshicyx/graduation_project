"""
个性化推荐 API - "猜你喜欢"功能
基于用户浏览历史、收藏记录生成个性化推荐
"""
from __future__ import annotations

import time
import random
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.db import Database
from app.schemas import RecommendResponse, RecommendItem

router = APIRouter(prefix="/personalized", tags=["个性化推荐"])
security = HTTPBearer(auto_error=False)

# JWT配置
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """从Bearer token获取当前用户（可选，不强制登录）"""
    if not credentials:
        return None
    
    import jwt
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = Database.fetchrow(
            "SELECT * FROM users WHERE id = %s AND is_active = true",
            int(user_id)
        )
        
        return user if user else None
        
    except (jwt.ExpiredSignatureError, jwt.JWTError):
        return None


def get_user_preferences(user_id: int) -> dict:
    """获取用户偏好：喜欢的类型、评分偏好等"""
    preferences = {
        'liked_genres': [],
        'liked_directors': [],
        'avg_rating': 7.0,
        'watch_count': 0
    }
    
    # 从收藏记录中分析用户偏好
    query = """
        SELECT m.genres, m.director, m.vote_average
        FROM user_favorites uf
        JOIN movies m ON uf.movie_id = m.id
        WHERE uf.user_id = %s AND uf.is_liked = true
        LIMIT 100
    """
    
    rows = Database.fetch(query, user_id)
    if not rows:
        return preferences
    
    genres_count = {}
    directors_count = {}
    ratings = []
    
    for row in rows:
        # 解析类型
        genres_str = row.get('genres')
        if genres_str:
            import json
            try:
                genres = json.loads(genres_str)
                for g in genres:
                    genres_count[g] = genres_count.get(g, 0) + 1
            except:
                pass
        
        # 统计导演
        director = row.get('director')
        if director:
            directors_count[director] = directors_count.get(director, 0) + 1
        
        # 评分
        vote_avg = row.get('vote_average')
        if vote_avg:
            ratings.append(float(vote_avg))
    
    # 获取最喜欢的类型
    if genres_count:
        sorted_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)
        preferences['liked_genres'] = [g[0] for g in sorted_genres[:5]]
    
    # 获取最喜欢的导演
    if directors_count:
        sorted_directors = sorted(directors_count.items(), key=lambda x: x[1], reverse=True)
        preferences['liked_directors'] = [d[0] for d in sorted_directors[:3]]
    
    # 平均评分
    if ratings:
        preferences['avg_rating'] = sum(ratings) / len(ratings)
    
    preferences['watch_count'] = len(rows)
    
    return preferences


def compute_user_similarity(user_id: int) -> dict:
    """
    计算用户与其他用户的相似度（基于评分行为的协同过滤）
    返回相似用户ID及其相似度权重
    """
    # 获取当前用户的收藏电影（作为"评分"）
    user_movies_query = """
        SELECT movie_id FROM user_favorites 
        WHERE user_id = %s AND is_liked = true
    """
    user_movies = Database.fetch(user_movies_query, user_id)
    user_movie_set = set(row[0] for row in user_movies) if user_movies else set()
    
    if not user_movie_set:
        return {}
    
    # 找也收藏了这些电影的其他用户
    similar_users_query = """
        SELECT uf.user_id, COUNT(*) as common_count
        FROM user_favorites uf
        WHERE uf.movie_id IN %s
        AND uf.user_id != %s
        AND uf.is_liked = true
        GROUP BY uf.user_id
        HAVING COUNT(*) >= 2
        ORDER BY common_count DESC
        LIMIT 50
    """
    similar_users = Database.fetch(similar_users_query, tuple(user_movie_set), user_id)
    
    # 计算相似度权重（Jaccard相似度）
    similarity_scores = {}
    for row in similar_users:
        other_user_id = row[0]
        common_count = row[1]
        
        # 获取其他用户的收藏
        other_movies_query = """
            SELECT movie_id FROM user_favorites 
            WHERE user_id = %s AND is_liked = true
        """
        other_movies = Database.fetch(other_movies_query, other_user_id)
        other_movie_set = set(r[0] for r in other_movies)
        
        # Jaccard相似度
        intersection = len(user_movie_set & other_movie_set)
        union = len(user_movie_set | other_movie_set)
        if union > 0:
            similarity_scores[other_user_id] = intersection / union
    
    return similarity_scores


def collaborative_filter_recommend(user_id: int, limit: int = 10) -> list:
    """
    协同过滤推荐：基于用户相似度和混合评分
    1. 计算与当前用户相似的其他用户
    2. 推荐这些相似用户喜欢的电影
    3. 结合内容相似度进行混合排序
    """
    # 获取当前用户偏好
    preferences = get_user_preferences(user_id)
    liked_genres = preferences['liked_genres']
    
    # 获取用户已看过的电影
    watched_query = """
        SELECT DISTINCT movie_id FROM (
            SELECT movie_id FROM user_favorites WHERE user_id = %s AND is_liked = true
            UNION
            SELECT movie_id FROM user_watch_history WHERE user_id = %s
        ) AS watched
    """
    watched_movies = Database.fetch(watched_query, user_id, user_id)
    watched_ids = set(row[0] for row in watched_movies) if watched_movies else set()
    
    # 计算用户相似度
    similarity_scores = compute_user_similarity(user_id)
    
    # 获取推荐候选电影（来自相似用户的收藏）
    candidate_scores = {}
    
    if similarity_scores:
        # 查询相似用户喜欢的电影
        similar_user_ids = list(similarity_scores.keys())
        
        for other_user_id in similar_user_ids:
            weight = similarity_scores[other_user_id]
            
            # 获取该相似用户的收藏
            other_favorites_query = """
                SELECT uf.movie_id, m.vote_average, m.genres, m.popularity
                FROM user_favorites uf
                JOIN movies m ON uf.movie_id = m.id
                WHERE uf.user_id = %s AND uf.is_liked = true
                AND uf.movie_id NOT IN %s
            """
            other_favorites = Database.fetch(
                other_favorites_query, other_user_id, tuple(watched_ids) if watched_ids else (0,)
            )
            
            for fav_row in other_favorites:
                movie_id = fav_row[0]
                if movie_id not in watched_ids:
                    vote_avg = float(fav_row[1]) if fav_row[1] else 0
                    genres_str = fav_row[2]
                    popularity = float(fav_row[3]) if fav_row[3] else 0
                    
                    # 解析类型
                    genre_match = 0
                    if genres_str and liked_genres:
                        import json
                        try:
                            movie_genres = json.loads(genres_str)
                            genre_match = len(set(movie_genres) & set(liked_genres)) / max(len(liked_genres), 1)
                        except:
                            pass
                    
                    # 综合评分 = 相似度权重 * 电影评分 * 类型匹配度
                    cf_score = weight * 0.6 + (vote_avg / 10) * 0.3 + genre_match * 0.1
                    
                    # 累加来自不同用户的评分
                    if movie_id in candidate_scores:
                        candidate_scores[movie_id]['weight'] += weight
                        candidate_scores[movie_id]['cf_score'] = max(candidate_scores[movie_id]['cf_score'], cf_score)
                    else:
                        candidate_scores[movie_id] = {
                            'cf_score': cf_score,
                            'weight': weight,
                            'vote_average': vote_avg,
                            'popularity': popularity
                        }
    
    # 如果协同过滤推荐不足，使用内容过滤补充
    if len(candidate_scores) < limit and liked_genres:
        # 内容过滤补充
        genre_conditions = " OR ".join(["m.genres LIKE %s" for _ in liked_genres])
        genre_params = [f"%{g}%" for g in liked_genres]
        
        exclude_ids = list(candidate_scores.keys()) + list(watched_ids) if watched_ids else list(candidate_scores.keys())
        if exclude_ids:
            exclude_condition = f"AND m.id NOT IN ({','.join(['%s'] * len(exclude_ids))})"
        else:
            exclude_condition = ""
        
        content_query = f"""
            SELECT m.id, m.title, m.poster_path, m.release_date, m.vote_average, m.genres, m.popularity
            FROM movies m
            WHERE m.vote_average >= 6.5
            AND ({genre_conditions})
            {exclude_condition}
            ORDER BY m.vote_average DESC, m.popularity DESC
            LIMIT %s
        """
        
        query_params = genre_params + exclude_ids + [limit - len(candidate_scores)] if exclude_ids else genre_params + [limit - len(candidate_scores)]
        content_results = Database.fetch(content_query, *query_params)
        
        for row in content_results:
            import json
            genres = []
            if row[5]:
                try:
                    genres = json.loads(row[5])
                    genre_match = len(set(genres) & set(liked_genres)) / max(len(liked_genres), 1)
                except:
                    genre_match = 0
            else:
                genre_match = 0
            
            vote_avg = float(row[4]) if row[4] else 0
            # 内容过滤分数
            content_score = (vote_avg / 10) * 0.5 + genre_match * 0.5
            
            if row[0] not in candidate_scores:
                candidate_scores[row[0]] = {
                    'cf_score': content_score,
                    'weight': 0.1,
                    'vote_average': vote_avg,
                    'popularity': row[6] if len(row) > 6 else 0,
                    'title': row[1],
                    'poster_path': row[2],
                    'release_date': row[3],
                    'genres': genres
                }
    
    # 按综合分数排序
    sorted_candidates = sorted(
        candidate_scores.items(),
        key=lambda x: x[1]['cf_score'],
        reverse=True
    )[:limit]
    
    # 获取完整电影信息
    recommendations = []
    for movie_id, scores in sorted_candidates:
        movie_query = """
            SELECT m.id, m.title, m.poster_path, m.release_date, m.vote_average, m.genres, m.popularity
            FROM movies m WHERE m.id = %s
        """
        movie_row = Database.fetchrow(movie_query, movie_id)
        
        if movie_row:
            import json
            genres = []
            if movie_row[5]:
                try:
                    genres = json.loads(movie_row[5])
                except:
                    pass
            
            recommendations.append({
                'movie_id': movie_row[0],
                'title': movie_row[1],
                'poster_path': movie_row[2],
                'release_date': movie_row[3],
                'vote_average': float(movie_row[4]) if movie_row[4] else 0,
                'genres': genres,
                'popularity': movie_row[6] if len(movie_row) > 6 else 0,
                'reason': '与你品味相似的用户也在看'
            })
    
    return recommendations


def get_popular_recommend(limit: int = 10) -> list:
    """获取热门推荐（用于游客或新用户）"""
    query = """
        SELECT m.id, m.title, m.poster_path, m.release_date, m.vote_average, m.genres, m.popularity
        FROM movies m
        WHERE m.vote_average >= 7.0 AND m.popularity > 100
        ORDER BY m.vote_average DESC, m.popularity DESC
        LIMIT %s
    """
    
    results = Database.fetch(query, limit)
    
    recommendations = []
    for row in results:
        import json
        genres = []
        genres_str = row.get('genres')
        if genres_str:
            try:
                genres = json.loads(genres_str)
            except:
                pass
        
        recommendations.append({
            'movie_id': row.get('id'),
            'title': row.get('title'),
            'poster_path': row.get('poster_path'),
            'release_date': row.get('release_date'),
            'vote_average': float(row.get('vote_average') or 0),
            'genres': genres,
            'popularity': row.get('popularity'),
            'reason': '热门高分电影'
        })
    
    return recommendations


def get_random_recommend(limit: int = 10) -> list:
    """获取随机推荐（备用）"""
    query = """
        SELECT m.id, m.title, m.poster_path, m.release_date, m.vote_average, m.genres, m.popularity
        FROM movies m
        WHERE m.poster_path IS NOT NULL AND m.poster_path != ''
        ORDER BY RANDOM()
        LIMIT %s
    """
    
    results = Database.fetch(query, limit)
    
    recommendations = []
    for row in results:
        import json
        genres = []
        genres_str = row.get('genres')
        if genres_str:
            try:
                genres = json.loads(genres_str)
            except:
                pass
        
        recommendations.append({
            'movie_id': row.get('id'),
            'title': row.get('title'),
            'poster_path': row.get('poster_path'),
            'release_date': row.get('release_date'),
            'vote_average': float(row.get('vote_average') or 0),
            'genres': genres,
            'popularity': row.get('popularity'),
            'reason': '发现好电影'
        })
    
    return recommendations


@router.get("/for-you", response_model=RecommendResponse)
async def get_personalized_recommendations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    获取个性化推荐（"猜你喜欢"）
    
    - 已登录用户：
      1. 分析用户收藏和浏览历史，获取偏好
      2. 基于偏好类型，使用协同过滤推荐相似电影
      3. 如果偏好不足，补充热门推荐
    
    - 游客/新用户：
      返回热门推荐
    """
    start_time = time.time()
    
    try:
        recommendations = []
        recommendation_type = "popular"
        
        if current_user:
            user_id = current_user['id']
            preferences = get_user_preferences(user_id)
            
            # 如果有足够数据，使用协同过滤
            if preferences['watch_count'] >= 3:
                recommendations = collaborative_filter_recommend(user_id, limit)
                recommendation_type = "personalized"
                
                # 如果推荐不足，补充热门
                if len(recommendations) < limit:
                    popular = get_popular_recommend(limit - len(recommendations))
                    recommendations.extend(popular)
            else:
                # 数据不足，使用热门推荐
                recommendations = get_popular_recommend(limit)
                recommendation_type = "popular"
                
            print(f"个性化推荐 for user {user_id}: {recommendation_type}, 偏好: {preferences['liked_genres']}")
        else:
            # 游客
            recommendations = get_popular_recommend(limit)
            recommendation_type = "popular"
            print("游客推荐: 热门电影")
        
        # 构建响应
        items = []
        for r in recommendations[:limit]:
            import json
            genres_list = r.get('genres', [])
            if isinstance(genres_list, str):
                try:
                    genres_list = json.loads(genres_list)
                except:
                    genres_list = []
            
            release_date = r.get('release_date')
            if release_date and hasattr(release_date, 'isoformat'):
                release_date = release_date.isoformat()
            elif release_date:
                release_date = str(release_date)
            
            items.append(RecommendItem(
                movie_id=r['movie_id'],
                title=r['title'],
                poster_path=r.get('poster_path'),
                vote_average=r.get('vote_average'),
                release_date=release_date,
                genres=genres_list if isinstance(genres_list, list) else [],
                relevance_score=r['vote_average'] / 10.0 if r.get('vote_average') else 0.5,
                reason=r.get('reason')
            ))
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return RecommendResponse(
            query=f"猜你喜欢 - {recommendation_type}",
            items=items,
            total_time_ms=elapsed_ms
        )
        
    except Exception as e:
        print(f"个性化推荐失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 降级：返回随机推荐
        recommendations = get_random_recommend(limit)
        items = []
        for r in recommendations:
            import json
            genres_list = r.get('genres', [])
            if isinstance(genres_list, str):
                try:
                    genres_list = json.loads(genres_list)
                except:
                    genres_list = []
            
            release_date = r.get('release_date')
            if release_date and hasattr(release_date, 'isoformat'):
                release_date = release_date.isoformat()
            elif release_date:
                release_date = str(release_date)
            
            items.append(RecommendItem(
                movie_id=r['movie_id'],
                title=r['title'],
                poster_path=r.get('poster_path'),
                vote_average=r.get('vote_average'),
                release_date=release_date,
                genres=genres_list if isinstance(genres_list, list) else [],
                relevance_score=r['vote_average'] / 10.0 if r.get('vote_average') else 0.5,
                reason=r.get('reason')
            ))
        
        return RecommendResponse(
            query="猜你喜欢 - fallback",
            items=items,
            total_time_ms=int((time.time() - start_time) * 1000)
        )