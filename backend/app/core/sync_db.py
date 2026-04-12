"""
同步数据库连接（作为异步连接的备选方案）
用于Windows上asyncpg不稳定的情况
"""

from typing import Iterator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import psycopg2
from .config import settings


def _make_sync_engine():
    """创建同步引擎"""
    return create_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


sync_engine = _make_sync_engine()
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False, class_=Session)


def get_sync_db() -> Iterator[Session]:
    """获取同步数据库会话"""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_sync_connection() -> bool:
    """测试同步数据库连接"""
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            return value == 1
    except Exception as e:
        print(f"同步数据库连接测试失败: {e}")
        return False


def execute_sync_query(query: str, params: dict = None):
    """执行同步查询"""
    if params is None:
        params = {}
    
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()
    except Exception as e:
        print(f"同步查询失败: {e}")
        return None


# 测试连接
if __name__ == "__main__":
    if test_sync_connection():
        print("同步连接测试成功!")
        
        # 测试查询
        rows = execute_sync_query("SELECT id, title FROM movies LIMIT 3")
        if rows:
            print(f"查询成功，获取到 {len(rows)} 行数据")
            for row in rows:
                print(f"  ID={row[0]}, 标题={row[1]}")
    else:
        print("同步连接测试失败")