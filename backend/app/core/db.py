"""
数据库模块 - 使用同步psycopg2避免Windows+asyncpg兼容性问题
"""
import os
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# 数据库连接参数
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "movie_recommendation"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "356921"),
}

# 连接池
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


def get_pool() -> pool.ThreadedConnectionPool:
    """获取或创建连接池"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **DB_CONFIG
        )
    return _connection_pool


def close_pool():
    """关闭连接池"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None


@contextmanager
def get_connection():
    """获取数据库连接的上下文管理器"""
    p = get_pool()
    conn = p.getconn()
    try:
        yield conn
    finally:
        p.putconn(conn)


def execute(query: str, *args) -> None:
    """执行查询（无返回）"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, args)
        conn.commit()


def fetch_one(query: str, *args) -> Optional[Dict[str, Any]]:
    """获取单行数据"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            result = cur.fetchone()
            return dict(result) if result else None


def fetch_all(query: str, *args) -> List[Dict[str, Any]]:
    """获取所有行数据"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            results = cur.fetchall()
            return [dict(row) for row in results]


class Database:
    """数据库操作类"""
    
    @staticmethod
    def fetch(query: str, *args) -> List[Dict[str, Any]]:
        """获取所有行"""
        return fetch_all(query, *args)
    
    @staticmethod
    def fetchrow(query: str, *args) -> Optional[Dict[str, Any]]:
        """获取单行"""
        return fetch_one(query, *args)
    
    @staticmethod
    def execute(query: str, *args) -> None:
        """执行查询"""
        execute(query, *args)
    
    @staticmethod
    def fetch_val(query: str, *args) -> Any:
        """获取单个值"""
        row = fetch_one(query, *args)
        if row and len(row) > 0:
            return list(row.values())[0]
        return None


# 初始化连接池（延迟到实际使用时）
def init_db():
    """初始化数据库连接"""
    try:
        p = get_pool()
        # 测试连接
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        print("数据库连接池初始化成功")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def close_db():
    """关闭数据库连接"""
    close_pool()
    print("数据库连接池已关闭")


# 兼容旧的 async API
async def get_db():
    """兼容旧的异步 get_db（但实际使用同步连接）"""
    yield Database()


def test_connection():
    """测试数据库连接"""
    return init_db()
