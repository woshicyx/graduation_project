"""
RAG 服务 - 混合搜索与智能推荐核心模块

功能：
1. 向量语义检索 (Qdrant)
2. 混合搜索 (向量 + 过滤条件)
3. 智能推荐 (LLM 需求解析 + RAG)
4. 支持多种搜索策略

搜索策略：
- "filter_first": 先过滤后向量搜索（适用于有明确硬性条件的查询）
- "search_first": 先向量搜索后过滤（适用于模糊/相关性优先的查询）
- "hybrid": 扩大召回池后过滤（平衡策略）
"""
from __future__ import annotations

import os
import time
import requests
from typing import List, Dict, Any, Optional, Tuple

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.http import models

from ..core.config import settings
from ..core.db import Database

# Embedding 配置
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# ==================== Qdrant 客户端初始化 ====================

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """获取 Qdrant 客户端实例"""
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_url = settings.qdrant_url
        api_key = settings.qdrant_api_key
        
        if qdrant_url:
            _qdrant_client = QdrantClient(
                url=str(qdrant_url),
                api_key=api_key if api_key else None,
            )
            print(f"Qdrant 已连接: {qdrant_url}")
        else:
            raise RuntimeError(
                "QDRANT_URL 未配置！\n"
                "请在 backend/.env 中配置 QDRANT_URL"
            )
    
    return _qdrant_client


def reset_qdrant_client():
    """重置客户端（用于测试或配置变更后）"""
    global _qdrant_client
    _qdrant_client = None


# ==================== Embedding 函数 ====================

def get_text_embeddings(texts: List[str]) -> List[List[float]]:
    """
    获取文本的向量嵌入（使用 ZhipuAI API）
    
    Args:
        texts: 文本列表
        
    Returns:
        向量列表
    """
    api_key = os.getenv("ZHIPUAI_API_KEY", "")
    api_base = os.getenv("ZHIPUAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
    model = os.getenv("EMBEDDING_MODEL", "embedding-2")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    embeddings = []
    for text in texts:
        if not text or not text.strip():
            # 返回零向量
            embeddings.append([0.0] * EMBEDDING_DIMENSION)
            continue
            
        try:
            response = requests.post(
                f"{api_base}/embeddings",
                headers=headers,
                json={"model": model, "input": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result["data"][0]["embedding"]
                embeddings.append(embedding)
            else:
                print(f"Embedding API 失败: {response.status_code} - {response.text[:200]}")
                embeddings.append([0.0] * EMBEDDING_DIMENSION)
                
        except Exception as e:
            print(f"Embedding 请求异常: {e}")
            embeddings.append([0.0] * EMBEDDING_DIMENSION)
    
    return embeddings


def vector_search(
    query: str,
    limit: int = 10,
    score_threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """
    纯向量语义搜索（使用新版 query_points API）
    
    Args:
        query: 搜索查询
        limit: 返回数量
        score_threshold: 最低相似度分数
        
    Returns:
        [{movie_id, score, payload}, ...]
    """
    try:
        client = get_qdrant_client()
        
        # 获取查询向量
        query_vector = get_text_embeddings([query])[0]
        
        # 使用新版 query_points API
        search_results = client.query_points(
            collection_name="movie_semantic",
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )
        
        results = []
        for point in search_results.points:
            results.append({
                "movie_id": int(point.id) if isinstance(point.id, int) else int(point.id),
                "score": point.score,
                "payload": point.payload or {}
            })
        
        return results
        
    except Exception as e:
        print(f"向量搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def retrieve_movies(
    query: str,
    limit: int = 10,
    score_threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """
    检索电影：向量搜索 + 获取详细信息
    
    Args:
        query: 搜索查询
        limit: 返回数量
        score_threshold: 最低相似度分数
        
    Returns:
        [{movie_id, title, overview, ...}, ...]
    """
    try:
        # 向量搜索
        semantic_results = vector_search(query, limit=limit * 3, score_threshold=score_threshold)
        
        if not semantic_results:
            print(f"向量搜索无结果: {query}")
            return []
        
        # 提取电影ID和分数
        movie_ids = [r["movie_id"] for r in semantic_results]
        score_map = {r["movie_id"]: r["score"] for r in semantic_results}
        
        # 从数据库获取详细信息
        movies = fetch_movies_by_ids(movie_ids)
        
        # 添加向量分数
        for movie in movies:
            movie_id = movie.get("id")
            movie["vector_score"] = score_map.get(movie_id, 0)
        
        # 按向量分数排序
        movies.sort(key=lambda x: x.get("vector_score", 0), reverse=True)
        
        return movies[:limit]
        
    except Exception as e:
        print(f"检索失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_movies_by_ids(movie_ids: List[int]) -> List[Dict[str, Any]]:
    """
    根据ID列表从PostgreSQL获取电影详情
    
    Args:
        movie_ids: 电影ID列表
        
    Returns:
        电影详情列表
    """
    if not movie_ids:
        return []
    
    try:
        placeholders = ",".join(["%s"] * len(movie_ids))
        query = f"""
            SELECT 
                id, title, overview, poster_path,
                release_date, vote_average, vote_count,
                popularity, runtime, genres, director,
                original_language
            FROM movies 
            WHERE id IN ({placeholders})
        """
        
        # Database.fetch expects individual args, use * to unpack
        rows = Database.fetch(query, *movie_ids)
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"数据库查询失败: {e}")
        import traceback
        traceback.print_exc()
        return []


# 中文到英文的类型映射
GENRE_TRANSLATION = {
    "动作": "Action",
    "冒险": "Adventure",
    "动画": "Animation",
    "喜剧": "Comedy",
    "犯罪": "Crime",
    "纪录": "Documentary",
    "剧情": "Drama",
    "家庭": "Family",
    "奇幻": "Fantasy",
    "历史": "History",
    "恐怖": "Horror",
    "音乐": "Music",
    "悬疑": "Mystery",
    "爱情": "Romance",
    "科幻": "Science Fiction",
    "惊悚": "Thriller",
    "战争": "War",
    "西部": "Western",
}


def fetch_filtered_movie_ids(
    filters: Dict[str, Any],
    limit: int = 500
) -> List[int]:
    """
    根据过滤条件从数据库获取候选电影ID
    
    Args:
        filters: 过滤条件字典
        limit: 最大返回数量
        
    Returns:
        符合条件的电影ID列表
    """
    conditions = []
    params = []
    
    # 类型过滤 - 支持中英文类型
    genre = filters.get("genre")
    if genre:
        # 如果是中文类型，转换为英文
        english_genre = GENRE_TRANSLATION.get(genre, genre)
        # 同时匹配中英文（数据库中可能是英文）
        conditions.append("(genres ILIKE %s OR genres ILIKE %s)")
        params.extend([f"%{genre}%", f"%{english_genre}%"])
    
    # 导演过滤（精确匹配）
    director = filters.get("director")
    if director:
        conditions.append("director = %s")
        params.append(director)
    
    # 评分过滤
    rating_min = filters.get("rating_min")
    if rating_min is not None:
        conditions.append("vote_average >= %s")
        params.append(float(rating_min))
    
    rating_max = filters.get("rating_max")
    if rating_max is not None:
        conditions.append("vote_average <= %s")
        params.append(float(rating_max))
    
    # 年份过滤
    year_min = filters.get("year_min")
    if year_min is not None:
        conditions.append("EXTRACT(YEAR FROM release_date) >= %s")
        params.append(int(year_min))
    
    year_max = filters.get("year_max")
    if year_max is not None:
        conditions.append("EXTRACT(YEAR FROM release_date) <= %s")
        params.append(int(year_max))
    
    # 时长过滤
    runtime_min = filters.get("runtime_min")
    if runtime_min is not None:
        conditions.append("runtime >= %s")
        params.append(int(runtime_min))
    
    runtime_max = filters.get("runtime_max")
    if runtime_max is not None:
        conditions.append("runtime <= %s")
        params.append(int(runtime_max))
    
    # 构建查询
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT id FROM movies 
        WHERE {where_clause}
        ORDER BY vote_average DESC, popularity DESC
        LIMIT %s
    """
    params.append(limit)
    
    try:
        rows = Database.fetch(query, *params)
        return [row["id"] for row in rows]
    except Exception as e:
        print(f"过滤查询失败: {e}")
        import traceback
        traceback.print_exc()
        return []


# ==================== 混合搜索策略 ====================

def filter_first_search(
    query: str,
    filters: Dict[str, Any],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    先过滤后向量搜索（策略一）
    
    适用于有明确硬性条件的查询，确保结果100%符合条件
    
    Args:
        query: 语义查询
        filters: 过滤条件
        limit: 返回数量
        
    Returns:
        电影列表
    """
    # 1. 根据过滤条件获取候选电影
    candidate_ids = fetch_filtered_movie_ids(filters, limit=500)
    
    if not candidate_ids:
        print(f"没有符合条件的电影: {filters}")
        return []
    
    print(f"候选电影数量: {len(candidate_ids)}")
    
    # 2. 获取查询向量
    query_vector = get_text_embeddings([query])[0]
    
    # 3. 在候选电影中进行向量搜索
    try:
        client = get_qdrant_client()
        
        # 使用 query_points 在候选集中搜索
        search_results = client.query_points(
            collection_name="movie_semantic",
            query=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="id",
                        match=models.MatchAny(any=candidate_ids)
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
        )
        
        # 4. 获取详细信息
        result_ids = [int(point.id) for point in search_results.points]
        score_map = {int(point.id): point.score for point in search_results.points}
        
        movies = fetch_movies_by_ids(result_ids)
        
        # 添加分数
        for movie in movies:
            movie["vector_score"] = score_map.get(movie["id"], 0)
            # 计算综合分数
            vote_norm = (movie.get("vote_average", 0) or 0) / 10.0
            popularity = movie.get("popularity", 0) or 0
            pop_norm = min(popularity / 500.0, 1.0)
            movie["final_score"] = 0.65 * movie["vector_score"] + 0.20 * vote_norm + 0.15 * pop_norm
        
        # 按综合分数排序
        movies.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        return movies[:limit]
        
    except Exception as e:
        print(f"先过滤后搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def search_first_filter(
    query: str,
    filters: Dict[str, Any],
    limit: int = 10,
    expansion_factor: int = 5
) -> List[Dict[str, Any]]:
    """
    先向量搜索后过滤（策略二）
    
    适用于模糊/相关性优先的查询
    
    Args:
        query: 语义查询
        filters: 过滤条件
        limit: 返回数量
        expansion_factor: 扩大召回倍数
        
    Returns:
        电影列表
    """
    # 1. 扩大召回范围
    semantic_results = vector_search(query, limit=limit * expansion_factor)
    
    if not semantic_results:
        return []
    
    # 2. 获取详细信息
    movie_ids = [r["movie_id"] for r in semantic_results]
    score_map = {r["movie_id"]: r["score"] for r in semantic_results}
    
    movies = fetch_movies_by_ids(movie_ids)
    
    # 3. 应用过滤条件
    filtered_movies = apply_filters(movies, filters, score_map)
    
    # 4. 按综合分数排序
    filtered_movies.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    return filtered_movies[:limit]


def apply_filters(
    movies: List[Dict[str, Any]],
    filters: Dict[str, Any],
    score_map: Dict[int, float] = None
) -> List[Dict[str, Any]]:
    """
    应用过滤条件到电影列表
    
    Args:
        movies: 电影列表
        filters: 过滤条件
        score_map: 向量分数映射
        
    Returns:
        过滤后的电影列表
    """
    results = []
    
    for movie in movies:
        movie_id = movie.get("id")
        movie_year = None
        if movie.get("release_date"):
            try:
                movie_year = int(str(movie["release_date"])[:4])
            except:
                pass
        
        # 类型过滤 - 同时匹配中英文
        genre = filters.get("genre")
        if genre:
            genres_str = str(movie.get("genres", ""))
            # 匹配中文类型或英文类型
            genre_match = False
            genre_lower = genre.lower()
            # 检查是否直接包含（英文或中文）
            if genre_lower in genres_str.lower():
                genre_match = True
            # 检查翻译后的英文类型
            english_genre = GENRE_TRANSLATION.get(genre, "").lower()
            if english_genre in genres_str.lower():
                genre_match = True
            # 检查翻译后的中文类型
            for zh, en in GENRE_TRANSLATION.items():
                if zh.lower() == genre_lower and zh.lower() in genres_str.lower():
                    genre_match = True
                    break
            
            if not genre_match:
                continue
        
        # 导演过滤（精确匹配）
        director = filters.get("director")
        if director:
            director_str = str(movie.get("director", ""))
            # 精确匹配：完全一致
            if director.lower() != director_str.lower():
                continue
        
        # 评分过滤
        rating_min = filters.get("rating_min")
        if rating_min is not None and (movie.get("vote_average", 0) or 0) < rating_min:
            continue
        
        rating_max = filters.get("rating_max")
        if rating_max is not None and (movie.get("vote_average", 0) or 0) > rating_max:
            continue
        
        # 年份过滤
        if year_min := filters.get("year_min"):
            if (movie_year or 0) < year_min:
                continue
        
        if year_max := filters.get("year_max"):
            if (movie_year or 9999) > year_max:
                continue
        
        # 时长过滤
        runtime_min = filters.get("runtime_min")
        if runtime_min and (movie.get("runtime", 0) or 0) < runtime_min:
            continue
        
        runtime_max = filters.get("runtime_max")
        if runtime_max and (movie.get("runtime", 0) or 0) > runtime_max:
            continue
        
        # 计算综合分数
        vector_score = score_map.get(movie_id, 0) if score_map else movie.get("vector_score", 0)
        vote_norm = (movie.get("vote_average", 0) or 0) / 10.0
        popularity = movie.get("popularity", 0) or 0
        pop_norm = min(popularity / 500.0, 1.0)
        
        final_score = 0.65 * vector_score + 0.20 * vote_norm + 0.15 * pop_norm
        
        movie["vector_score"] = vector_score
        movie["final_score"] = final_score
        results.append(movie)
    
    return results


# ==================== 智能混合搜索入口 ====================

def hybrid_search(
    query: str,
    limit: int = 10,
    strategy: str = "auto",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    智能混合搜索 - 根据条件自动选择策略
    
    Args:
        query: 用户查询
        limit: 返回数量
        strategy: 搜索策略
            - "auto": 自动选择（根据过滤条件判断）
            - "filter_first": 先过滤后搜索
            - "search_first": 先搜索后过滤
            - "hybrid": 扩大召回池后过滤
        
    Returns:
        电影列表
    """
    filters = {
        "genre": kwargs.get("genre"),
        "director": kwargs.get("director"),
        "rating_min": kwargs.get("rating_min"),
        "rating_max": kwargs.get("rating_max"),
        "year_min": kwargs.get("year_min"),
        "year_max": kwargs.get("year_max"),
        "runtime_min": kwargs.get("runtime_min"),
        "runtime_max": kwargs.get("runtime_max"),
    }
    # 移除 None 值
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # 自动策略选择
    if strategy == "auto":
        # 始终使用 search_first，避免 filter_first 的 id 索引问题
        # filter_first 需要 Qdrant 为 id 字段创建索引
        strategy = "search_first"
    
    # 当filters为空时，使用更大的expansion_factor进行情感类查询
    expansion_factor = 15 if not filters else 5
    
    print(f"混合搜索策略: {strategy}, 查询: {query}, 过滤: {filters}, expansion: {expansion_factor}")
    
    if strategy == "filter_first_or":
        return filter_first_search_with_or(query, filters, limit)
    elif strategy == "filter_first":
        return filter_first_search(query, filters, limit)
    elif strategy == "search_first":
        return search_first_filter(query, filters, limit)
    else:  # hybrid
        return search_first_filter(query, filters, limit, expansion_factor=10)


def filter_first_search_with_or(
    query: str,
    filters: Dict[str, Any],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    先过滤后向量搜索 - 使用OR逻辑组合导演和类型
    
    适用于导演+类型的组合查询，优先返回导演的电影
    
    Args:
        query: 语义查询
        filters: 过滤条件
        limit: 返回数量
        
    Returns:
        电影列表
    """
    genre = filters.get("genre")
    director = filters.get("director")
    
    if genre and director:
        # 使用OR逻辑：要么是指定导演，要么是指定类型
        # 先获取导演的电影
        director_filter = {"director": director}
        director_ids = set(fetch_filtered_movie_ids(director_filter, limit=200))
        
        # 获取类型的电影
        genre_filter = {"genre": genre}
        genre_ids = set(fetch_filtered_movie_ids(genre_filter, limit=200))
        
        # OR组合
        candidate_ids = list(director_ids | genre_ids)
        
        print(f"导演电影: {len(director_ids)}, 类型电影: {len(genre_ids)}, 合并后: {len(candidate_ids)}")
        
        # 先做向量搜索，扩大召回范围
        query_vector = get_text_embeddings([query])[0]
        client = get_qdrant_client()
        
        # 扩大召回以确保覆盖所有候选电影
        semantic_results = client.query_points(
            collection_name="movie_semantic",
            query=query_vector,
            limit=500,
            with_payload=False,
        )
        
        # 获取向量分数
        score_map = {int(p.id): p.score for p in semantic_results.points}
        
        # 获取候选电影的详细信息
        all_movies = fetch_movies_by_ids(candidate_ids)
        
        # 分开排序
        director_movies = [m for m in all_movies if m["id"] in director_ids]
        genre_movies = [m for m in all_movies if m["id"] in genre_ids and m["id"] not in director_ids]
        
        # 计算分数
        for m in director_movies + genre_movies:
            m["vector_score"] = score_map.get(m["id"], 0)
            vote_norm = (m.get("vote_average", 0) or 0) / 10.0
            popularity = m.get("popularity", 0) or 0
            pop_norm = min(popularity / 500.0, 1.0)
            m["final_score"] = 0.65 * m["vector_score"] + 0.20 * vote_norm + 0.15 * pop_norm
        
        # 排序
        director_movies.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        genre_movies.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        # 合并：导演的优先
        return (director_movies + genre_movies)[:limit]
        
    else:
        # 单独条件，使用AND
        return filter_first_search(query, filters, limit)


# ==================== LLM 增强的推荐系统 ====================

def enhanced_hybrid_search(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    增强混合搜索：先使用 LLM 解析需求，再向量检索
    
    Args:
        query: 用户自然语言查询
        limit: 返回数量
        
    Returns:
        {
            "semantic_query": "用于语义检索的核心描述",
            "filters": {...},  # 提取的过滤条件
            "movies": [...],   # 搜索结果
            "llm_parsing_success": True/False,
            "strategy": "filter_first/search_first/hybrid"
        }
    """
    # 1. 使用 LLM 解析需求
    try:
        from app.services.requirement_extractor import extract_requirements
        requirements = extract_requirements(query)
        llm_success = True
    except Exception as e:
        print(f"需求提取失败，使用原始查询: {e}")
        requirements = {
            "semantic_query": query,
            "filters": {}
        }
        llm_success = False
    
    # 2. 提取语义查询和过滤条件
    semantic_query = requirements.get("semantic_query", query)
    filters = requirements.get("filters", {})
    
    print(f"LLM 解析结果: 语义查询={semantic_query}, 过滤={filters}")
    
    # 3. 始终使用 search_first 策略，避免 filter_first 的 id 索引问题
    # filter_first 需要 Qdrant 为 id 字段创建索引
    strategy = "search_first"
    
    # 4. 执行混合搜索
    movies = hybrid_search(
        query=semantic_query,
        strategy=strategy,
        limit=limit,
        **filters
    )
    
    print(f"最终策略: {strategy}, 返回结果: {len(movies)} 条")
    
    # 5. 返回结果
    return {
        "semantic_query": semantic_query,
        "filters": filters,
        "movies": movies,
        "llm_parsing_success": llm_success,
        "strategy": strategy,
    }


# ==================== 兼容旧 API ====================

def semantic_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """兼容旧 API"""
    return retrieve_movies(query, limit=limit)


def hybrid_search_compat(
    query: str,
    genre: str = None,
    director: str = None,
    rating_min: float = None,
    rating_max: float = None,
    year_min: int = None,
    year_max: int = None,
    runtime_min: int = None,
    runtime_max: int = None,
    language: str = None,
    country: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """兼容旧 API"""
    return hybrid_search(
        query=query,
        genre=genre,
        director=director,
        rating_min=rating_min,
        rating_max=rating_max,
        year_min=year_min,
        year_max=year_max,
        runtime_min=runtime_min,
        runtime_max=runtime_max,
        language=language,
        country=country,
        limit=limit
    )
