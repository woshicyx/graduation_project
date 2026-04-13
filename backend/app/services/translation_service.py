"""
翻译服务 - 使用智谱 API 进行中英互译

功能：
1. 中英互译
2. 翻译缓存（避免重复翻译）
3. 批量翻译支持
"""
from __future__ import annotations

import os
import json
import time
import hashlib
from typing import Optional, Dict, List, Any
from functools import lru_cache

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

# 翻译模型
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "glm-4-flash")  # 使用免费版

# 简单内存缓存
_translation_cache: Dict[str, str] = {}
_CACHE_MAX_SIZE = 5000


def _get_cache_key(text: str, source_lang: str = "auto", target_lang: str = "zh") -> str:
    """生成缓存键"""
    content = f"{source_lang}:{target_lang}:{text}"
    return hashlib.md5(content.encode()).hexdigest()


def _is_chinese(text: str) -> bool:
    """简单检测文本是否包含中文"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def _is_english(text: str) -> bool:
    """简单检测文本是否主要是英文"""
    if not text:
        return False
    # 统计英文字符比例
    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_chars = sum(1 for c in text if c.isalpha())
    return total_chars > 0 and english_chars / total_chars > 0.8


def translate(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "zh"
) -> Optional[str]:
    """
    翻译文本
    
    Args:
        text: 待翻译文本
        source_lang: 源语言 (auto/en/zh)
        target_lang: 目标语言 (en/zh)
        
    Returns:
        翻译后的文本，失败返回 None
    """
    if not text or not text.strip():
        return text
    
    # 如果目标语言和检测到的语言一致，跳过翻译
    if target_lang == "zh" and _is_chinese(text):
        return text
    if target_lang == "en" and _is_english(text):
        return text
    
    # 检查缓存
    cache_key = _get_cache_key(text, source_lang, target_lang)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    # 调用智谱翻译 API
    result = _call_translation_api(text, source_lang, target_lang)
    
    if result:
        # 更新缓存
        if len(_translation_cache) < _CACHE_MAX_SIZE:
            _translation_cache[cache_key] = result
    
    return result


def _call_translation_api(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "zh"
) -> Optional[str]:
    """
    调用智谱翻译 API
    
    使用 GLM-4 的函数调用能力进行翻译
    """
    if not ZHIPUAI_API_KEY:
        print("警告: ZHIPUAI_API_KEY 未配置，使用降级翻译")
        return _fallback_translate(text, target_lang)
    
    # 构建 prompt
    if target_lang == "zh":
        prompt = f"""请将以下英文内容翻译为中文。保持专业术语的准确性，翻译要自然流畅。

英文内容：
{text}

只输出翻译结果，不要其他内容。"""
    else:
        prompt = f"""Please translate the following Chinese text to English. Keep professional terms accurate and natural.

Chinese text:
{text}

Only output the translation, nothing else."""
    
    headers = {
        "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": TRANSLATION_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
    }
    
    try:
        response = requests.post(
            f"{ZHIPUAI_API_BASE}/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            translated = result["choices"][0]["message"]["content"].strip()
            return translated
        else:
            print(f"翻译 API 调用失败: {response.status_code} - {response.text[:200]}")
            return _fallback_translate(text, target_lang)
            
    except requests.exceptions.Timeout:
        print("翻译 API 调用超时")
        return _fallback_translate(text, target_lang)
    except Exception as e:
        print(f"翻译 API 调用异常: {e}")
        return _fallback_translate(text, target_lang)


def _fallback_translate(text: str, target_lang: str = "zh") -> Optional[str]:
    """
    降级翻译：简单的关键词替换
    
    当 API 不可用时使用基础翻译
    """
    if target_lang == "zh":
        # 常见电影关键词翻译
        translations = {
            # 类型
            "Action": "动作",
            "Adventure": "冒险",
            "Animation": "动画",
            "Comedy": "喜剧",
            "Crime": "犯罪",
            "Documentary": "纪录片",
            "Drama": "剧情",
            "Family": "家庭",
            "Fantasy": "奇幻",
            "Horror": "恐怖",
            "Music": "音乐",
            "Mystery": "悬疑",
            "Romance": "爱情",
            "Science Fiction": "科幻",
            "Sci-Fi": "科幻",
            "Thriller": "惊悚",
            "War": "战争",
            "Western": "西部",
            
            # 常见关键词
            "love": "爱情",
            "action": "动作",
            "comedy": "喜剧",
            "science": "科学",
            "fiction": "幻想",
            "space": "太空",
            "time": "时间",
            "travel": "旅行",
            "future": "未来",
            "world": "世界",
            "war": "战争",
            "history": "历史",
            "magic": "魔法",
            "hero": "英雄",
            "death": "死亡",
            "life": "生命",
            "murder": "谋杀",
            "detective": "侦探",
            "mystery": "悬疑",
            "horror": "恐怖",
            "ghost": "鬼魂",
            "monster": "怪物",
            "zombie": "僵尸",
            "vampire": "吸血鬼",
            "supernatural": "超自然",
            "fantasy": "奇幻",
            "dragons": "龙",
            "kingdom": "王国",
            "princess": "公主",
            "knight": "骑士",
            "christmas": "圣诞节",
            "holiday": "节日",
            "canada": "加拿大",
            "england": "英格兰",
            "paris": "巴黎",
            "new york": "纽约",
            "los angeles": "洛杉矶",
            "tokyo": "东京",
        }
        
        result = text
        for en, zh in translations.items():
            result = result.replace(en, zh)
            result = result.replace(en.lower(), zh)
        
        return result if result != text else None
    
    return None


def batch_translate(
    texts: List[str],
    target_lang: str = "zh",
    delay: float = 0.1
) -> Dict[int, Optional[str]]:
    """
    批量翻译
    
    Args:
        texts: 文本列表
        target_lang: 目标语言
        delay: 请求间隔（秒），避免 API 限流
        
    Returns:
        {索引: 翻译结果}
    """
    results = {}
    
    for i, text in enumerate(texts):
        if not text or not text.strip():
            results[i] = text
            continue
        
        # 检测是否需要翻译
        needs_translate = True
        if target_lang == "zh" and not _is_chinese(text):
            needs_translate = True
        elif target_lang == "en" and not _is_english(text):
            needs_translate = True
        else:
            needs_translate = False
        
        if needs_translate:
            results[i] = translate(text, target_lang=target_lang)
            time.sleep(delay)  # 避免限流
        else:
            results[i] = text
    
    return results


def translate_keywords(keywords: List[str]) -> List[str]:
    """
    翻译关键词列表
    
    Args:
        keywords: 英文关键词列表
        
    Returns:
        中文关键词列表
    """
    if not keywords:
        return []
    
    translated = []
    for kw in keywords:
        result = translate(kw, target_lang="zh")
        if result:
            translated.append(result)
        else:
            translated.append(kw)  # 保留原文
    
    return translated


def clear_cache():
    """清空翻译缓存"""
    global _translation_cache
    _translation_cache.clear()


def get_cache_size() -> int:
    """获取缓存大小"""
    return len(_translation_cache)
