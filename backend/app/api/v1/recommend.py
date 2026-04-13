"""
AI 推荐 API - 基于 RAG 的电影推荐

集成 LLM 需求解析 + 向量检索 + 混合排序
"""
from __future__ import annotations

import time
import json
from fastapi import APIRouter

from app import schemas
from app.services.rag_service_fixed import (
    hybrid_search,
    retrieve_movies,
    fetch_movies_by_ids,
    enhanced_hybrid_search,
)

router = APIRouter(prefix="/ai", tags=["ai"])


def build_recommend_items(movies: list, limit: int = 10) -> list:
    """构建推荐结果列表"""
    items = []
    for movie in movies[:limit]:
        movie_id = movie.get("id")
        
        # 解析 genres
        genres = movie.get("genres", [])
        if isinstance(genres, str):
            try:
                genres = json.loads(genres)
            except:
                genres = []
        
        items.append(schemas.RecommendItem(
            movie_id=movie_id,
            title=movie.get("title", "未知电影"),
            relevance_score=round(movie.get("final_score", movie.get("score", 0)), 4),
            reason=None  # 暂不生成推荐理由
        ))
    
    return items


@router.post(
    "/recommend",
    response_model=schemas.RecommendResponse,
    summary="AI 推荐：基于自然语言需求返回影片列表",
)
async def recommend_movies(payload: schemas.RecommendRequest) -> schemas.RecommendResponse:
    """
    基于增强 RAG 的电影推荐接口
    
    流程:
    1. LLM 解析用户查询，提取硬性过滤条件
    2. 使用语义核心进行向量检索
    3. 应用硬性过滤条件筛选结果
    4. 混合排序（向量分 + 评分 + 热度）
    5. 返回推荐列表及相似度分数
    """
    start_time = time.time()
    
    # 获取推荐数量
    limit = min(payload.max_results, 20)
    
    try:
        # 使用增强混合搜索（包含 LLM 需求解析）
        result = enhanced_hybrid_search(
            query=payload.query,
            limit=limit
        )
        
        movies = result.get("movies", [])
        llm_success = result.get("llm_parsing_success", False)
        semantic_query = result.get("semantic_query", payload.query)
        filters = result.get("filters", {})
        
        # 构建推荐结果
        items = build_recommend_items(movies, limit)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 日志输出
        if llm_success:
            print(f"推荐查询: '{payload.query}' -> 语义: '{semantic_query}', 过滤: {filters}")
        else:
            print(f"推荐查询(降级): '{payload.query}'")
        
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
    summary="AI 搜索：语义搜索电影（支持硬性过滤）",
)
async def ai_search(
    q: str,
    genre: str = None,
    director: str = None,
    rating_min: float = None,
    rating_max: float = None,
    year_min: int = None,
    year_max: int = None,
    runtime_min: int = None,
    runtime_max: int = None,
    language: str = None,
    limit: int = 10
) -> schemas.RecommendResponse:
    """
    混合搜索接口（向量 + SQL 过滤）
    
    显式指定过滤条件时使用此接口。
    如需从自然语言自动提取过滤条件，请使用 /recommend 接口。
    
    公式: final_score = 0.65*向量分 + 0.20*评分分 + 0.15*热度分
    """
    start_time = time.time()
    
    try:
        results = hybrid_search(
            query=q,
            genre=genre,
            director=director,
            rating_min=rating_min,
            rating_max=rating_max,
            year_min=year_min,
            year_max=year_max,
            runtime_min=runtime_min,
            runtime_max=runtime_max,
            language=language,
            limit=limit
        )
        
        items = build_recommend_items(results, limit)
        
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


@router.post(
    "/recommend/stream",
    summary="AI 推荐（流式输出）",
)
async def recommend_movies_stream(payload: schemas.RecommendRequest):
    """
    基于增强 RAG 的电影推荐接口 - 流式输出版本
    
    流式返回：
    - event: movie - 单个推荐电影信息
    - event: done - 推荐完成
    - event: error - 错误信息
    """
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    start_time = time.time()
    limit = min(payload.max_results, 20)
    
    async def generate():
        try:
            # 使用增强混合搜索
            result = enhanced_hybrid_search(
                query=payload.query,
                limit=limit
            )
            
            movies = result.get("movies", [])
            llm_success = result.get("llm_parsing_success", False)
            semantic_query = result.get("semantic_query", payload.query)
            filters = result.get("filters", {})
            
            # 发送初始信息
            yield f"event: info\ndata: {json.dumps({'type': 'start', 'query': payload.query, 'llm_success': llm_success})}\n\n"
            
            # 逐个发送电影
            for i, movie in enumerate(movies[:limit]):
                movie_id = movie.get("id")
                
                # 解析 genres
                genres = movie.get("genres", [])
                if isinstance(genres, str):
                    try:
                        genres = json.loads(genres)
                    except:
                        genres = []
                
                movie_data = {
                    "type": "movie",
                    "index": i,
                    "movie_id": movie_id,
                    "title": movie.get("title", "未知电影"),
                    "poster_path": movie.get("poster_path"),
                    "vote_average": movie.get("vote_average"),
                    "release_date": movie.get("release_date"),
                    "relevance_score": round(movie.get("final_score", movie.get("score", 0)), 4),
                    "genres": [g.get("name") if isinstance(g, dict) else str(g) for g in genres],
                }
                
                yield f"event: movie\ndata: {json.dumps(movie_data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)  # 控制发送速率，让前端有打字机效果
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # 发送完成信息
            yield f"event: done\ndata: {json.dumps({'total': len(movies), 'time_ms': elapsed_ms})}\n\n"
            
            if llm_success:
                print(f"流式推荐: '{payload.query}' -> 语义: '{semantic_query}', 过滤: {filters}")
            
        except Exception as e:
            print(f"流式推荐失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post(
    "/parse-query",
    summary="解析查询：提取硬性过滤条件（调试用）",
)
async def parse_query(payload: schemas.RecommendRequest):
    """
    仅解析用户查询，提取硬性过滤条件，不执行搜索。
    
    用于调试 LLM 需求解析的效果。
    """
    try:
        from app.services.requirement_extractor import extract_requirements
        
        result = extract_requirements(payload.query)
        
        return {
            "query": payload.query,
            "semantic_query": result.get("semantic_query", ""),
            "filters": result.get("filters", {}),
            "llm_parsing_success": True,
        }
        
    except Exception as e:
        print(f"查询解析失败: {e}")
        return {
            "query": payload.query,
            "semantic_query": payload.query,
            "filters": {},
            "llm_parsing_success": False,
            "error": str(e)
        }
