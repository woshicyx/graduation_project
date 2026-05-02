"""
需求提取器 - 使用 LLM 解析用户查询中的硬性约束

功能：
1. 接收用户自然语言查询（支持任意语言）
2. 提取结构化过滤条件（统一映射为中文标准）
3. 提取用于语义检索的核心语义描述

设计原则：
- "卡住两头，放开中间"
- 输入头：LLM 翻译所有过滤条件为中文标准词汇
- 中间检索：利用 Embedding 跨语言能力
- 输出头：后续 Prompt 控制回复语言
"""
from __future__ import annotations

import os
import json
import re
from typing import Optional, Dict, Any, List

import requests

# 尝试加载 .env 配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 智谱 API 配置
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
ZHIPUAI_API_BASE = os.getenv("ZHIPUAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
ZHIPUAI_LLM_MODEL = os.getenv("ZHIPUAI_LLM_MODEL", "glm-4-flash")

# 中文类型标准词汇映射（英文/中文口语 → 中文标准）
GENRE_MAPPING = {
    # 标准中文
    "动作": "动作",
    "冒险": "冒险",
    "动画": "动画",
    "喜剧": "喜剧",
    "犯罪": "犯罪",
    "纪录": "纪录",
    "剧情": "剧情",
    "家庭": "家庭",
    "奇幻": "奇幻",
    "历史": "历史",
    "恐怖": "恐怖",
    "音乐": "音乐",
    "悬疑": "悬疑",
    "爱情": "爱情",
    "科幻": "科幻",
    "惊悚": "惊悚",
    "战争": "战争",
    "西部": "西部",
    # 英文标准类型
    "Action": "动作",
    "Adventure": "冒险",
    "Animation": "动画",
    "Comedy": "喜剧",
    "Crime": "犯罪",
    "Documentary": "纪录",
    "Drama": "剧情",
    "Family": "家庭",
    "Fantasy": "奇幻",
    "History": "历史",
    "Horror": "恐怖",
    "Music": "音乐",
    "Mystery": "悬疑",
    "Romance": "爱情",
    "Science Fiction": "科幻",
    "Sci-Fi": "科幻",
    "Thriller": "惊悚",
    "War": "战争",
    "Western": "西部",
    # 口语/中文
    "funny": "喜剧",
    "搞笑": "喜剧",
    "搞笑片": "喜剧",
    "恐怖片": "恐怖",
    "恐怖片": "恐怖",
    "科幻片": "科幻",
    "爱情片": "爱情",
    "动画片": "动画",
    "动画片": "动画",
    "动画片": "动画",
}

# 导演名称映射（中文昵称 → 标准英文名）
DIRECTOR_MAPPING = {
    "诺兰": "Christopher Nolan",
    "卡梅隆": "James Cameron",
    "斯皮尔伯格": "Steven Spielberg",
    " Spielberg": "Steven Spielberg",
    "张艺谋": "Yimou Zhang",
    "周星驰": "Stephen Chow",
    "宫崎骏": "Hayao Miyazaki",
    "昆汀": "Quentin Tarantino",
    "马丁": "Martin Scorsese",
    "李安": "Ang Lee",
    "吴京": "Jing Wu",
    "王家卫": "Wong Kar-wai",
}

# 语言代码映射
LANGUAGE_MAPPING = {
    "en": "en",
    "english": "en",
    "英语": "en",
    "英文": "en",
    "zh": "zh",
    "chinese": "zh",
    "中文": "zh",
    "普通话": "zh",
    "ja": "ja",
    "japanese": "ja",
    "日语": "ja",
    "ko": "ko",
    "korean": "ko",
    "韩语": "ko",
    "法语": "fr",
    "french": "fr",
    "德语": "de",
    "german": "de",
    "西班牙语": "es",
    "spanish": "es",
}


def normalize_genre(genre: str) -> Optional[str]:
    """将任意语言的类型映射为中文标准类型"""
    if not genre:
        return None
    
    genre = genre.strip()
    
    # 直接映射
    if genre in GENRE_MAPPING:
        return GENRE_MAPPING[genre]
    
    # 不区分大小写匹配
    genre_lower = genre.lower()
    for key, value in GENRE_MAPPING.items():
        if key.lower() == genre_lower:
            return value
    
    return None


def normalize_director(director: str) -> str:
    """将中文导演名映射为标准英文名"""
    if not director:
        return ""
    
    director = director.strip()
    
    # 直接映射
    if director in DIRECTOR_MAPPING:
        return DIRECTOR_MAPPING[director]
    
    # 不区分大小写匹配
    director_lower = director.lower()
    for key, value in DIRECTOR_MAPPING.items():
        if key.lower() in director_lower or director_lower in key.lower():
            return value
    
    return director


def normalize_language(lang: str) -> Optional[str]:
    """将语言名称映射为标准代码"""
    if not lang:
        return None
    
    lang = lang.strip().lower()
    
    if lang in LANGUAGE_MAPPING:
        return LANGUAGE_MAPPING[lang]
    
    return None


def _is_chinese(text: str) -> bool:
    """检测文本是否包含中文"""
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def _extract_genres_from_query(query: str) -> List[str]:
    """从查询中提取类型（使用正则匹配）"""
    genres = []
    query_lower = query.lower()
    
    # 检测所有可能的中英文类型
    for eng, zh in GENRE_MAPPING.items():
        if eng.lower() in query_lower:
            normalized = normalize_genre(eng)
            if normalized and normalized not in genres:
                genres.append(normalized)
    
    # 口语类型检测
    oral_genres = {
        r'搞笑[片电影]?': '喜剧',
        r'恐怖[片电影]?': '恐怖',
        r'科幻[片电影]?': '科幻',
        r'爱情[片电影]?': '爱情',
        r'动画[片电影]?': '动画',
        r'动作[片电影]?': '动作',
        r'喜剧[片电影]?': '喜剧',
        r'惊悚[片电影]?': '惊悚',
        r'悬疑[片电影]?': '悬疑',
    }
    
    for pattern, genre in oral_genres.items():
        if re.search(pattern, query):
            if genre not in genres:
                genres.append(genre)
    
    return genres


def _extract_director_from_query(query: str) -> Optional[str]:
    """从查询中提取导演名"""
    # 检测中文导演昵称
    for cn_name, en_name in DIRECTOR_MAPPING.items():
        if cn_name in query:
            return en_name
    
    # 检测英文 "directed by" 或 "director"
    director_match = re.search(r'directed by\s+([A-Za-z\s\.]+)', query, re.IGNORECASE)
    if director_match:
        return director_match.group(1).strip()
    
    return None


def _extract_rating_from_query(query: str) -> Optional[float]:
    """从查询中提取评分要求"""
    # 评分 8 分以上
    match = re.search(r'(\d+\.?\d*)\s*[分星]\s*以?[上下]', query)
    if match:
        return float(match.group(1))
    
    # rating above 8
    match = re.search(r'rating\s*(?:above|over|>)\s*(\d+\.?\d*)', query, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # 8 分以上
    match = re.search(r'(\d+\.?\d*)\s*分.*以?[上下]', query)
    if match:
        return float(match.group(1))
    
    return None


def _extract_year_from_query(query: str) -> Optional[int]:
    """从查询中提取年份要求"""
    # 2020 年以后
    match = re.search(r'(\d{4})\s*年.*以?[后前]', query)
    if match:
        year = int(match.group(1))
        if '后' in query:
            return year  # year_min
        elif '前' in query:
            return year  # year_max
    
    # after 2020
    match = re.search(r'after\s*(\d{4})', query, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # before 2020
    match = re.search(r'before\s*(\d{4})', query, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return None


# 需求提取的 Prompt 模板（Phase 1 核心）
EXTRACT_PROMPT_TEMPLATE = """你是一个电影推荐助手。请解析用户的查询，提取出明确的过滤条件和语义核心。

【重要】类型映射要求：
- 无论用户用什么语言提问（如 "Comedy", "funny movie", "搞笑片"），都必须翻译并映射为以下中文标准类型之一：
  '动作', '冒险', '动画', '喜剧', '犯罪', '纪录', '剧情', '家庭', '奇幻', '历史', 
  '恐怖', '音乐', '悬疑', '爱情', '科幻', '惊悚', '战争', '西部'
- 如果用户提到的类型无法映射，返回 null

【导演映射要求】：
- "诺兰" → "Christopher Nolan"
- "卡梅隆" → "James Cameron"
- "宫崎骏" → "Hayao Miyazaki"
- 其他导演名保持原样

【重要】情感/意境类描述处理：
- 如果用户描述的是心情、情绪、意境（如"失恋了"、"平静的生活增添趣味"、"想放松一下"、"治愈"、"暖心"），
  请在 filters 中返回空对象 {{}}，不要生成任何 genre/year/rating 硬性条件
- 只在 semantic_query 中保留用户原始的情感描述，让向量检索去匹配电影的剧情和情感基调
- 语义查询应该是用户的完整原话，帮助向量检索找到情感基调匹配的电影

用户查询: {query}

请输出 JSON 格式（只输出JSON，不要其他内容）：
{{
  "semantic_query": "用于语义检索的核心描述（情感类保留原话，类型类提取关键词）",
  "filters": {{
    "genre": "中文标准类型（只有用户明确提到类型时才填）",
    "director": "导演姓名（只有用户明确提到导演时才填）",
    "rating_min": 最低评分数字（只有用户明确提到评分时才填）",
    "year_min": 最早年份（只有用户明确提到年代时才填）",
    "runtime_max": 最长时长（分钟）（只有用户明确提到时长时才填）"
  }}
}}

示例：
查询 "Find me a funny comedy movie with rating above 8" 
输出: {{"semantic_query": "funny comedy movie", "filters": {{"genre": "喜剧", "rating_min": 8.0}}}}

查询 "想看诺兰导演的科幻片，评分8分以上"
输出: {{"semantic_query": "科幻片", "filters": {{"genre": "科幻", "director": "Christopher Nolan", "rating_min": 8.0}}}}

查询 "失恋了想看部温暖的电影"
输出: {{"semantic_query": "失恋了想看部温暖的电影", "filters": {{}}}}

查询 "平静的生活增添趣味"
输出: {{"semantic_query": "平静的生活增添趣味", "filters": {{}}}}"""


def call_zhipuai_llm(prompt: str, model: str = None) -> Optional[str]:
    """调用智谱 GLM-4 API"""
    if not ZHIPUAI_API_KEY:
        print("警告: ZHIPUAI_API_KEY 未配置")
        return None
    
    model = model or ZHIPUAI_LLM_MODEL
    
    headers = {
        "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 500,
    }
    
    try:
        response = requests.post(
            f"{ZHIPUAI_API_BASE}/chat/completions",
            headers=headers,
            json=data,
            timeout=30  # 增加超时时间到30秒
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"智谱 LLM 调用失败: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"智谱 LLM 调用异常: {e}")
        return None


def extract_requirements(query: str) -> Dict[str, Any]:
    """
    解析用户查询，提取结构化需求
    
    Args:
        query: 用户自然语言查询（支持任意语言）
        
    Returns:
        {
            "semantic_query": "用于语义检索的核心描述",
            "filters": {
                "genre": "中文标准类型",
                "director": "导演姓名",
                "rating_min": float,
                "year_min": int,
                "runtime_max": int,
            }
        }
    """
    if not query or not query.strip():
        return {
            "semantic_query": "",
            "filters": {}
        }
    
    # 优先使用 LLM 解析
    prompt = EXTRACT_PROMPT_TEMPLATE.format(query=query)
    response = call_zhipuai_llm(prompt)
    
    if response:
        try:
            json_str = response.strip()
            # 清理 markdown 包装
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            result = json.loads(json_str.strip())
            
            # 标准化过滤条件
            filters = result.get("filters", {})
            normalized_filters = _normalize_filters(filters)
            
            return {
                "semantic_query": result.get("semantic_query", query),
                "filters": normalized_filters,
                "llm_used": True
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}, 使用降级策略")
    
    # LLM 失败时的降级策略：使用正则提取
    return _fallback_extract(query)


def _normalize_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """标准化过滤条件"""
    normalized = {}
    
    # 标准化类型
    genre = filters.get("genre")
    if genre:
        normalized_genre = normalize_genre(genre)
        if normalized_genre:
            normalized["genre"] = normalized_genre
    
    # 标准化导演
    director = filters.get("director")
    if director:
        normalized["director"] = normalize_director(director)
    
    # 数值字段
    if filters.get("rating_min"):
        try:
            normalized["rating_min"] = float(filters["rating_min"])
        except:
            pass
    
    if filters.get("year_min"):
        try:
            normalized["year_min"] = int(filters["year_min"])
        except:
            pass
    
    if filters.get("runtime_max"):
        try:
            normalized["runtime_max"] = int(filters["runtime_max"])
        except:
            pass
    
    return normalized


def _fallback_extract(query: str) -> Dict[str, Any]:
    """
    降级策略：使用正则表达式提取基本过滤条件
    
    当 LLM 不可用时使用
    """
    filters = {}
    
    # 提取类型
    genres = _extract_genres_from_query(query)
    if genres:
        filters["genre"] = genres[0]  # 只取第一个
    
    # 提取导演
    director = _extract_director_from_query(query)
    if director:
        filters["director"] = director
    
    # 提取评分
    rating = _extract_rating_from_query(query)
    if rating:
        filters["rating_min"] = rating
    
    # 提取年份
    year = _extract_year_from_query(query)
    if year:
        filters["year_min"] = year
    
    # 提取时长
    runtime_match = re.search(r'(\d+)\s*分.*以内|时长.*?(\d+)', query)
    if runtime_match:
        runtime = runtime_match.group(1) or runtime_match.group(2)
        filters["runtime_max"] = int(runtime)
    
    return {
        "semantic_query": query,
        "filters": filters,
        "llm_used": False
    }
