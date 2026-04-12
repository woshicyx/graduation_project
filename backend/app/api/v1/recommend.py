"""
AI 推荐 API - 基于 RAG 的电影推荐
"""
from __future__ import annotations

import time
from fastapi import APIRouter

from app import schemas
from app.services.rag_service import hybrid_search, retrieve_movies, fetch_movies_by_ids

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/recommend",
    response_model=schemas.RecommendResponse,
    summary="AI 推荐：基于自然语言需求返回影片列表",
)
async def recommend_movies(payload: schemas.RecommendRequest) -> schemas.RecommendResponse:
    """
    基于 RAG 的电影推荐接口
    
    流程:
    1. 对用户查询进行 embedding
    2. 在 Qdrant 中进行语义召回
    3. 从 PostgreSQL 获取电影详情
    4. 返回推荐列表及相似度分数
    """
    start_time = time.time()
    
    # 获取推荐数量
    limit = min(payload.max_results, 20)  # 最多返回20部
    
    try:
        # 语义召回（不调用 LLM）
        semantic_results = retrieve_movies(payload.query, limit=limit * 2)
        
        if not semantic_results:
            return schemas.RecommendResponse(
                query=payload.query,
                items=[],
                total_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # 获取电影ID
        movie_ids = [r["movie_id"] for r in semantic_results]
        
        # 从数据库获取完整信息
        movies = fetch_movies_by_ids(movie_ids)
        
        # 构建 ID 到分数的映射
        score_map = {r["movie_id"]: r["score"] for r in semantic_results}
        
        # 构建推荐结果
        items = []
        for movie in movies:
            movie_id = movie["id"]
            score = score_map.get(movie_id, 0)
            
            # 解析 genres
            genres = []
            if movie.get("genres"):
                if isinstance(movie["genres"], str):
                    import json
                    try:
                        genres = json.loads(movie["genres"])
                    except:
                        genres = []
                else:
                    genres = movie["genres"]
            
            items.append(schemas.RecommendItem(
                movie_id=movie_id,
                title=movie.get("title", "未知电影"),
                relevance_score=round(score, 4),
                reason=None  # 暂不生成推荐理由，等召回稳定后再加
            ))
        
        # 按相似度排序
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 限制数量
        items = items[:limit]
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return schemas.RecommendResponse(
            query=payload.query,
            items=items,
            total_time_ms=elapsed_ms
        )
        
    except Exception as e:
        print(f"推荐失败: {e}")
        import traceback
        traceback.print_exc()
        
        return schemas.RecommendResponse(
            query=payload.query,
            items=[],
            total_time_ms=int((time.time() - start_time) * 1000)
        )


@router.get(
    "/search",
    response_model=schemas.RecommendResponse,
    summary="AI 搜索：语义搜索电影",
)
async def ai_search(
    q: str,
    genre: str = None,
    director: str = None,
    rating_min: float = None,
    limit: int = 10
) -> schemas.RecommendResponse:
    """
    混合搜索接口（向量 + SQL 过滤）
    
    公式: final_score = 0.65*向量分 + 0.20*评分分 + 0.15*热度分
    """
    start_time = time.time()
    
    try:
        results = hybrid_search(
            query=q,
            genre=genre,
            director=director,
            rating_min=rating_min,
            limit=limit
        )
        
        items = []
        for movie in results:
            # 解析 genres
            genres = []
            if movie.get("genres"):
                if isinstance(movie["genres"], str):
                    import json
                    try:
                        genres = json.loads(movie["genres"])
                    except:
                        genres = []
                else:
                    genres = movie["genres"]
            
            items.append(schemas.RecommendItem(
                movie_id=movie["id"],
                title=movie.get("title", "未知电影"),
                relevance_score=round(movie.get("final_score", 0), 4),
                reason=None
            ))
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        return schemas.RecommendResponse(
            query=q,
            items=items,
            total_time_ms=elapsed_ms
        )
        
    except Exception as e:
        print(f"AI搜索失败: {e}")
        import traceback
        traceback.print_exc()
        
        return schemas.RecommendResponse(
            query=q,
            items=[],
            total_time_ms=int((time.time() - start_time) * 1000)
        )
