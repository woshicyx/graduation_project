from __future__ import annotations

from fastapi import APIRouter

from .. import schemas

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/recommend",
    response_model=schemas.RecommendResponse,
    summary="AI 推荐：基于自然语言需求返回影片列表及推荐理由",
)
async def recommend_movies(payload: schemas.RecommendRequest) -> schemas.RecommendResponse:
    # TODO:
    # 1. 根据 payload.query 生成 embedding
    # 2. 调用向量库做语义召回
    # 3. 读取 PostgreSQL 中的电影元数据
    # 4. 调用 LLM（OpenAI / LangChain / LlamaIndex）生成推荐理由
    # 目前先返回占位数据，便于前端联调
    return schemas.RecommendResponse(query=payload.query, items=[])

