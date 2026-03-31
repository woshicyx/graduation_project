from __future__ import annotations

from typing import Optional

from qdrant_client import QdrantClient

from .config import settings

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        if settings.qdrant_url:
            _qdrant_client = QdrantClient(
                url=str(settings.qdrant_url),
                api_key=settings.qdrant_api_key,
            )
        else:
            # 本地嵌入模式（无服务器）也可以稍后切换
            _qdrant_client = QdrantClient(":memory:")
    return _qdrant_client

