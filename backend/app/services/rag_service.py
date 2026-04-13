"""
RAG 服务 - 负责文本处理、Embedding生成和向量召回

Phase 1: 单电影单向量模式
支持: OpenAI Embedding / ZhipuAI (智谱) Embedding
"""
from __future__ import annotations

import json
import os
from typing import Optional, List, Dict, Any, Tuple

# 尝试加载 .env 配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.core.db import Database
from app.core.vector import get_qdrant_client

# Collection 名称
COLLECTION_NAME = "movie_semantic"

# Embedding 配置 - 优先使用 ZhipuAI
# ZhipuAI embedding-2: 1024维, 免费额度充足
# ZhipuAI embedding-2-flash: 1024维, 免费版
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# 批量大小
BATCH_SIZE = 100


def _parse_json_field(value: Any, extract_name: bool = False) -> List[str]:
    """
    通用 JSON 字段解析器
    
    Args:
        value: 可能是 JSON 字符串、list 或 None
        extract_name: 是否从 dict 中提取 'name' 字段
        
    Returns:
        字符串列表
    """
    if not value:
        return []
    
    try:
        # 如果是字符串，尝试解析
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        
        # 确保是列表
        if not isinstance(data, list):
            return []
        
        # 提取名称
        if extract_name and data and isinstance(data[0], dict):
            return [item.get('name', '') for item in data if item.get('name')]
        
        # 直接返回字符串列表
        return [str(item) for item in data]
        
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        print(f"JSON 解析失败: {value[:50] if isinstance(value, str) else value}, 错误: {e}")
        return []


def build_movie_rag_text(movie: Dict[str, Any], target_lang: str = "zh") -> str:
    """
    构建电影的RAG文本描述（Phase 2 优化版）
    
    设计原则："卡住两头，放开中间"
    - 输入头：过滤条件统一为中文标准
    - 中间检索：保留英文关键词 + 中文上下文，提升跨语言匹配
    - 输出头：后续 Prompt 控制回复语言
    
    Args:
        movie: 电影数据字典
        target_lang: 目标语言（默认 zh，用于标签语言，保留英文关键词）
        
    Returns:
        格式化后的RAG文本（中英文混合，中文上下文 + 英文原始关键词）
    """
    # 导入翻译服务
    try:
        from app.services.translation_service import translate_keywords, _is_chinese
    except ImportError:
        _is_chinese = lambda x: any('\u4e00' <= c <= '\u9fff' for c in x)
        translate_keywords = None
    
    # 解析 genres（提取 name 字段）
    genres_list = _parse_json_field(movie.get("genres"), extract_name=True)
    genres = "、".join(genres_list) if genres_list else ""
    
    # 解析 keywords（保留原始英文 + 添加中文标注）
    keywords_list = _parse_json_field(movie.get("keywords"), extract_name=True)
    # 英文关键词保持原样，但在前面加中文标注提升跨语言匹配
    keywords_zh = "、".join(keywords_list) if keywords_list else ""
    
    # 字段值
    title = movie.get('title', '')
    original_title = movie.get('original_title', '')
    overview = movie.get('overview', '')
    tagline = movie.get('tagline', '')
    director = movie.get('director', '')
    original_language = movie.get('original_language', '')
    
    # 构建 RAG 文本（Phase 2 优化版）
    # 使用【中文标签: 原始值】格式，明确告诉 Embedding 这是什么字段
    parts = [
        f"【电影标题 Title】: {title}" if title else None,
        f"【原名 Original Title】: {original_title}" if original_title and original_title != title else None,
        f"【剧情简介 Overview】: {overview}" if overview else None,
        f"【电影宣传语 Tagline】: {tagline}" if tagline else None,
        f"【电影类型 Genres】: {genres}" if genres else None,
        f"【英文关键词 Keywords】: {keywords_zh}" if keywords_zh else None,  # 明确标注为英文关键词
        f"【导演 Director】: {director}" if director else None,
        f"【原语言 Language】: {original_language}" if original_language else None,
    ]
    
    # 过滤空行并组合
    rag_text = "\n".join(part for part in parts if part)
    return rag_text


def build_movie_rag_text_zh(movie: Dict[str, Any]) -> str:
    """
    构建电影的RAG文本描述（统一为中文）
    
    Args:
        movie: 电影数据字典
        
    Returns:
        格式化后的中文RAG文本
    """
    return build_movie_rag_text(movie, target_lang="zh")


def embed_text(text: str) -> Optional[List[float]]:
    """
    生成文本的Embedding向量
    
    优先使用 ZhipuAI (智谱)，如果未配置则尝试 OpenAI
    
    Args:
        text: 待嵌入的文本
        
    Returns:
        浮点数向量列表，失败返回 None
    """
    if not text or not text.strip():
        print("警告: 文本为空，跳过 embedding")
        return None
    
    # 优先使用 ZhipuAI
    zhipuai_key = os.getenv("ZHIPUAI_API_KEY")
    if zhipuai_key and zhipuai_key != "your-zhipuai-api-key-here":
        return _embed_zhipuai(text, zhipuai_key)
    
    # 降级到 OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your-openai-api-key-here":
        return _embed_openai(text, openai_key)
    
    print("警告: 未配置任何 Embedding API (ZHIPUAI_API_KEY 或 OPENAI_API_KEY)")
    return None


def _embed_zhipuai(text: str, api_key: str) -> Optional[List[float]]:
    """
    使用智谱AI生成Embedding
    
    API文档: https://open.bigmodel.cn/dev/api#text-embedding
    """
    try:
        import requests
        
        api_base = os.getenv("ZHIPUAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
        model = os.getenv("EMBEDDING_MODEL", "embedding-2")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model,
            "input": text,
        }
        
        response = requests.post(
            f"{api_base}/embeddings",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["data"][0]["embedding"]
        else:
            print(f"智谱AI Embedding失败: {response.status_code} - {response.text}")
            return None
            
    except ImportError:
        print("错误: requests 库未安装，运行: pip install requests")
        return None
    except Exception as e:
        print(f"智谱AI Embedding异常: {e}")
        return None


def _embed_openai(text: str, api_key: str) -> Optional[List[float]]:
    """
    使用 OpenAI 生成Embedding
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
        
    except ImportError:
        print("错误: openai 库未安装，运行: pip install openai")
        return None
    except Exception as e:
        print(f"OpenAI Embedding失败: {e}")
        return None


def ensure_collection_exists(force_recreate: bool = False) -> bool:
    """
    确保 Qdrant collection 存在
    
    Args:
        force_recreate: 是否强制重建（删除后重建）
        
    Returns:
        是否成功
    """
    try:
        client = get_qdrant_client()
        
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME in collection_names:
            if force_recreate:
                client.delete_collection(collection_name=COLLECTION_NAME)
                print(f"已删除旧 collection: {COLLECTION_NAME}")
            else:
                print(f"Collection {COLLECTION_NAME} 已存在")
                return True
        
        # 创建新 collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": EMBEDDING_DIMENSION,
                "distance": "Cosine"
            }
        )
        print(f"已创建 collection: {COLLECTION_NAME}")
        return True
        
    except Exception as e:
        print(f"确保 collection 存在失败: {e}")
        return False


def index_movie(movie: Dict[str, Any], target_lang: str = "zh") -> Tuple[bool, str]:
    """
    将单部电影索引到向量数据库
    
    Args:
        movie: 电影数据字典
        target_lang: 目标语言，默认中文
        
    Returns:
        (是否成功, 错误信息)
    """
    movie_id = movie.get("id")
    if not movie_id:
        return False, "电影ID为空"
    
    try:
        client = get_qdrant_client()
        
        # 构建 RAG 文本（统一为中文）
        rag_text = build_movie_rag_text(movie, target_lang=target_lang)
        if not rag_text.strip():
            return False, "RAG文本为空"
        
        # 生成向量
        vector = embed_text(rag_text)
        if vector is None:
            return False, "Embedding生成失败"
        
        # 验证向量维度
        if len(vector) != EMBEDDING_DIMENSION:
            print(f"警告: 向量维度 {len(vector)} 与配置不匹配 {EMBEDDING_DIMENSION}")
        
        # 解析 payload 数据（保留原始数据）
        genres = _parse_json_field(movie.get("genres"), extract_name=True)
        keywords = _parse_json_field(movie.get("keywords"), extract_name=True)
        
        payload = {
            "movie_id": movie_id,
            "title": movie.get("title", ""),
            "original_title": movie.get("original_title", ""),
            "overview": movie.get("overview", ""),
            "genres": genres,
            "keywords": keywords,
            "vote_average": movie.get("vote_average", 0) or 0,
            "popularity": movie.get("popularity", 0) or 0,
            "director": movie.get("director", "") or "",
            "language": movie.get("original_language", "") or "",
            "language_version": target_lang,
        }
        
        # Upsert 到 Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[{
                "id": movie_id,
                "vector": vector,
                "payload": payload
            }]
        )
        
        return True, ""
        
    except Exception as e:
        error_msg = f"索引电影 {movie_id} 失败: {e}"
        print(error_msg)
        return False, error_msg


def batch_index_movies(movies: List[Dict[str, Any]]) -> Tuple[int, int, List[int]]:
    """
    批量索引电影
    
    Args:
        movies: 电影列表
        
    Returns:
        (成功数, 失败数, 失败ID列表)
    """
    success_count = 0
    fail_count = 0
    fail_ids = []
    
    # 确保 collection 存在（只做一次）
    if not ensure_collection_exists():
        print("Collection 初始化失败")
        return 0, len(movies), [m.get("id") for m in movies if m.get("id")]
    
    # 准备批量数据
    points = []
    
    for movie in movies:
        movie_id = movie.get("id")
        if not movie_id:
            fail_count += 1
            continue
        
        try:
            rag_text = build_movie_rag_text(movie)
            if not rag_text.strip():
                fail_count += 1
                fail_ids.append(movie_id)
                continue
            
            vector = embed_text(rag_text)
            if vector is None:
                fail_count += 1
                fail_ids.append(movie_id)
                continue
            
            # 验证向量维度
            if len(vector) != EMBEDDING_DIMENSION:
                print(f"警告: 电影 {movie_id} 向量维度 {len(vector)} 不匹配")
                fail_count += 1
                fail_ids.append(movie_id)
                continue
            
            genres = _parse_json_field(movie.get("genres"), extract_name=True)
            keywords = _parse_json_field(movie.get("keywords"), extract_name=True)
            
            points.append({
                "id": movie_id,
                "vector": vector,
                "payload": {
                    "movie_id": movie_id,
                    "title": movie.get("title", ""),
                    "genres": genres,
                    "keywords": keywords,
                    "vote_average": movie.get("vote_average", 0) or 0,
                    "popularity": movie.get("popularity", 0) or 0,
                    "director": movie.get("director", "") or "",
                }
            })
            
        except Exception as e:
            fail_count += 1
            fail_ids.append(movie_id)
            print(f"准备电影 {movie_id} 失败: {e}")
    
    # 批量写入
    if points:
        try:
            client = get_qdrant_client()
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            success_count = len(points)
            print(f"批量写入 {success_count} 条成功")
        except Exception as e:
            fail_count += len(points)
            fail_ids.extend([p["id"] for p in points])
            print(f"批量写入失败: {e}")
    
    return success_count, fail_count, fail_ids


def retrieve_movies(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    语义检索相似电影
    
    Args:
        query: 查询文本
        limit: 返回数量
        
    Returns:
        电影ID列表及相似度分数
    """
    if not query or not query.strip():
        print("警告: 查询文本为空")
        return []
    
    try:
        client = get_qdrant_client()
        
        # 生成查询向量
        query_vector = embed_text(query)
        if query_vector is None:
            print("查询 embedding 失败")
            return []
        
        # 检查 collection 是否存在
        collections = client.get_collections().collections
        if COLLECTION_NAME not in [c.name for c in collections]:
            print(f"Collection {COLLECTION_NAME} 不存在，请先运行索引脚本")
            return []
        
        # 搜索 - 使用新版本API (qdrant-client >= 1.7.0)
        # 直接传入向量进行搜索（不使用using参数，因为是默认向量）
        try:
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,  # 直接传入向量列表
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            # 提取结果
            movies = []
            for hit in results.points:
                movie_info = {
                    "movie_id": hit.payload.get("movie_id", hit.id) if hit.payload else hit.id,
                    "score": hit.score,
                    "title": hit.payload.get("title", "") if hit.payload else "",
                    "genres": hit.payload.get("genres", []) if hit.payload else [],
                    "director": hit.payload.get("director", "") if hit.payload else "",
                }
                movies.append(movie_info)
            
            return movies
            
        except Exception as e:
            print(f"检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        return movies
        
    except Exception as e:
        print(f"检索失败: {e}")
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
        query = f"SELECT * FROM movies WHERE id IN ({placeholders})"
        
        rows = Database.fetch(query, *movie_ids)
        
        movies = []
        for row in rows:
            movie = dict(row)
            # 解析 JSON 字段
            movie["genres"] = _parse_json_field(movie.get("genres"), extract_name=True)
            movie["keywords"] = _parse_json_field(movie.get("keywords"), extract_name=True)
            movies.append(movie)
        
        return movies
        
    except Exception as e:
        print(f"获取电影详情失败: {e}")
        return []


def hybrid_search(
    query: str,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    runtime_min: Optional[int] = None,
    runtime_max: Optional[int] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    混合搜索：向量召回 + SQL过滤
    
    公式: final_score = 0.65*向量分 + 0.20*评分分 + 0.15*热度分
    
    Args:
        query: 查询文本
        genre: 类型过滤
        director: 导演过滤
        rating_min: 最低评分
        rating_max: 最高评分
        year_min: 最早年份
        year_max: 最晚年份
        runtime_min: 最短时长（分钟）
        runtime_max: 最长时长（分钟）
        language: 语言
        country: 国家/地区
        limit: 返回数量
        
    Returns:
        混合评分后的电影列表
    """
    # 1. 向量语义召回
    semantic_results = retrieve_movies(query, limit=limit * 5)
    
    if not semantic_results:
        return []
    
    # 2. 获取完整电影数据
    movie_ids = [r["movie_id"] for r in semantic_results]
    movies = fetch_movies_by_ids(movie_ids)
    
    # 3. 构建ID到分数的映射
    score_map = {r["movie_id"]: r["score"] for r in semantic_results}
    
    # 4. 混合评分
    results = []
    for movie in movies:
        movie_id = movie["id"]
        
        # 提取电影年份
        movie_year = None
        if movie.get("release_date"):
            if hasattr(movie["release_date"], 'year'):
                movie_year = movie["release_date"].year
            elif isinstance(movie["release_date"], str) and len(movie["release_date"]) >= 4:
                try:
                    movie_year = int(movie["release_date"][:4])
                except:
                    pass
        
        # SQL 过滤
        if genre:
            genres_str = str(movie.get("genres", []))
            if genre.lower() not in genres_str.lower():
                continue
        
        if director:
            director_str = str(movie.get("director", ""))
            if director.lower() not in director_str.lower():
                continue
        
        if rating_min is not None and (movie.get("vote_average", 0) or 0) < rating_min:
            continue
        
        if rating_max is not None and (movie.get("vote_average", 0) or 0) > rating_max:
            continue
        
        if year_min is not None and (movie_year or 0) < year_min:
            continue
        
        if year_max is not None and (movie_year or 9999) > year_max:
            continue
        
        if runtime_min is not None and (movie.get("runtime", 0) or 0) < runtime_min:
            continue
        
        if runtime_max is not None and (movie.get("runtime", 0) or 0) > runtime_max:
            continue
        
        if language:
            lang_str = str(movie.get("original_language", "")).lower()
            if language.lower() not in lang_str and lang_str not in language.lower():
                continue
        
        # 向量相似度
        vector_score = score_map.get(movie_id, 0)
        
        # 评分归一化
        vote_norm = (movie.get("vote_average", 0) or 0) / 10.0
        
        # 热度归一化
        popularity = movie.get("popularity", 0) or 0
        pop_norm = min(popularity / 500.0, 1.0)
        
        # 最终分数
        final_score = 0.65 * vector_score + 0.20 * vote_norm + 0.15 * pop_norm
        
        movie["vector_score"] = vector_score
        movie["final_score"] = final_score
        results.append(movie)
    
    # 排序
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return results[:limit]


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
        }
    """
    # 1. 导入需求提取器
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
    
    # 3. 调用混合搜索
    movies = hybrid_search(
        query=semantic_query,
        genre=filters.get("genre"),
        director=filters.get("director"),
        rating_min=filters.get("rating_min"),
        rating_max=filters.get("rating_max"),
        year_min=filters.get("year_min"),
        year_max=filters.get("year_max"),
        runtime_min=filters.get("runtime_min"),
        runtime_max=filters.get("runtime_max"),
        language=filters.get("language"),
        country=filters.get("country"),
        limit=limit
    )
    
    # 4. 返回结果
    return {
        "semantic_query": semantic_query,
        "filters": filters,
        "movies": movies,
        "llm_parsing_success": llm_success,
    }
