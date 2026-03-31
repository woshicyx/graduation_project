from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings


def _make_engine() -> AsyncEngine:
    # 使用 asyncpg 驱动
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(url, echo=settings.debug, future=True)


engine: AsyncEngine = _make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

