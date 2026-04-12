from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="健康检查")
async def health_check() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }

