"""
向量数据库模块 - Qdrant 客户端封装
"""
from __future__ import annotations

import os
from typing import Optional

from qdrant_client import QdrantClient

from .config import settings

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    获取 Qdrant 客户端实例
    
    优先使用配置的 QDRANT_URL，支持本地和云端部署
    """
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_url = settings.qdrant_url
        api_key = settings.qdrant_api_key
        
        if qdrant_url:
            # 使用配置的 URL（可以是云端或本地）
            _qdrant_client = QdrantClient(
                url=str(qdrant_url),
                api_key=api_key if api_key else None,
            )
            print(f"Qdrant 已连接: {qdrant_url}")
        else:
            # 没有配置 Qdrant URL，报错提示而不是使用内存模式
            raise RuntimeError(
                "QDRANT_URL 未配置！\n"
                "请在 backend/.env 中配置 QDRANT_URL:\n"
                "  本地: QDRANT_URL=http://localhost:6333\n"
                "  云端: QDRANT_URL=https://your-cluster.qdrant.tech\n"
                "如果还没有 Qdrant，运行: python -m scripts.setup_qdrant"
            )
    
    return _qdrant_client


def reset_qdrant_client():
    """重置客户端（用于测试或配置变更后）"""
    global _qdrant_client
    _qdrant_client = None
