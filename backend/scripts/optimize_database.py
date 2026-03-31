#!/usr/bin/env python3
"""
数据库优化脚本
1. 创建关键索引
2. 添加 pgvector 扩展
3. 创建向量表
4. 生成优化建议
"""

import asyncio
import logging
from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/movie_db"

# 优化索引定义
INDEX_DEFINITIONS = [
    # 电影表索引
    {
        "name": "idx_movies_title_gin",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_title_gin ON movies USING gin(to_tsvector('chinese', title))",
        "description": "中文标题全文搜索索引"
    },
    {
        "name": "idx_movies_genres_gin",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_genres_gin ON movies USING gin(genres)",
        "description": "类型数组GIN索引"
    },
    {
        "name": "idx_movies_box_office_desc",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_box_office_desc ON movies(box_office DESC) WHERE box_office > 0",
        "description": "票房降序索引（非零票房）"
    },
    {
        "name": "idx_movies_rating_desc",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_rating_desc ON movies(rating DESC) WHERE rating >= 0",
        "description": "评分降序索引（有效评分）"
    },
    {
        "name": "idx_movies_popularity_desc",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_popularity_desc ON movies(popularity DESC)",
        "description": "热度降序索引"
    },
    {
        "name": "idx_movies_release_date_desc",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_release_date_desc ON movies(release_date DESC)",
        "description": "上映日期降序索引"
    },
    # 复合索引
    {
        "name": "idx_movies_genre_rating",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_genre_rating ON movies(genres, rating DESC)",
        "description": "类型+评分复合索引"
    },
    {
        "name": "idx_movies_director_rating",
        "table": "movies",
        "sql": "CREATE INDEX idx_movies_director_rating ON movies(director, rating DESC)",
        "description": "导演+评分复合索引"
    },
    # 影评表索引
    {
        "name": "idx_reviews_movie_id_rating",
        "table": "reviews",
        "sql": "CREATE INDEX idx_reviews_movie_id_rating ON reviews(movie_id, rating DESC)",
        "description": "电影ID+评分复合索引"
    },
    {
        "name": "idx_reviews_rating_desc",
        "table": "reviews",
        "sql": "CREATE INDEX idx_reviews_rating_desc ON reviews(rating DESC)",
        "description": "影评评分降序索引"
    }
]

# pgvector 相关SQL
PGVECTOR_SQL = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    """
    CREATE TABLE IF NOT EXISTS movie_embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        movie_id UUID NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
        text_chunk TEXT NOT NULL,
        embedding vector(1536),  -- OpenAI text-embedding-3-small 维度
        chunk_type VARCHAR(50) NOT NULL,  -- 'metadata', 'synopsis', 'review'
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """,
    "CREATE INDEX idx_movie_embeddings_movie_id ON movie_embeddings(movie_id)",
    "CREATE INDEX idx_movie_embeddings_chunk_type ON movie_embeddings(chunk_type)",
    """
    CREATE INDEX idx_movie_embeddings_embedding 
    ON movie_embeddings 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100)
    """
]

# 性能优化建议
PERFORMANCE_TIPS = [
    "1. 定期运行 ANALYZE 更新统计信息",
    "2. 考虑对 movies 表进行分区（按 release_date 年份）",
    "3. 设置适当的 maintenance_work_mem 和 shared_buffers",
    "4. 启用 pg_stat_statements 扩展监控慢查询",
    "5. 考虑使用连接池（PgBouncer）"
]


async def check_existing_indexes(session: AsyncSession, table_name: str) -> List[str]:
    """检查已存在的索引"""
    query = text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = :table_name 
        AND schemaname = 'public'
    """)
    result = await session.execute(query, {"table_name": table_name})
    return [row[0] for row in result.fetchall()]


async def create_index(session: AsyncSession, index_def: dict):
    """创建单个索引"""
    try:
        # 检查索引是否已存在
        existing_indexes = await check_existing_indexes(session, index_def["table"])
        if index_def["name"] in existing_indexes:
            logger.info(f"索引 {index_def['name']} 已存在，跳过")
            return
        
        # 创建索引
        await session.execute(text(index_def["sql"]))
        await session.commit()
        logger.info(f"✅ 创建索引: {index_def['name']} - {index_def['description']}")
        
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ 创建索引 {index_def['name']} 失败: {str(e)}")
        # 继续执行其他索引


async def setup_pgvector(session: AsyncSession):
    """设置 pgvector 扩展和表"""
    try:
        logger.info("🔧 设置 pgvector 扩展...")
        
        for sql in PGVECTOR_SQL:
            await session.execute(text(sql))
        
        await session.commit()
        logger.info("✅ pgvector 扩展和表设置完成")
        
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ 设置 pgvector 失败: {str(e)}")
        raise


async def analyze_table_stats(session: AsyncSession):
    """分析表统计信息"""
    try:
        logger.info("📊 分析表统计信息...")
        
        tables = ["movies", "reviews", "movie_embeddings"]
        for table in tables:
            await session.execute(text(f"ANALYZE {table}"))
        
        await session.commit()
        logger.info("✅ 表统计信息更新完成")
        
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ 分析表统计信息失败: {str(e)}")


async def generate_performance_report(session: AsyncSession):
    """生成性能报告"""
    try:
        logger.info("📈 生成性能优化报告...")
        
        # 获取表大小信息
        size_query = text("""
            SELECT 
                table_name,
                pg_size_pretty(pg_total_relation_size('public.' || table_name)) as total_size,
                pg_size_pretty(pg_relation_size('public.' || table_name)) as table_size,
                pg_size_pretty(pg_total_relation_size('public.' || table_name) - pg_relation_size('public.' || table_name)) as index_size
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY pg_total_relation_size('public.' || table_name) DESC
        """)
        
        result = await session.execute(size_query)
        rows = result.fetchall()
        
        print("\n" + "="*60)
        print("📊 数据库表大小报告")
        print("="*60)
        for row in rows:
            print(f"{row[0]:20} | 总大小: {row[1]:10} | 表大小: {row[2]:10} | 索引大小: {row[3]:10}")
        
        # 获取索引信息
        index_query = text("""
            SELECT 
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size('public.' || indexname)) as index_size
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        result = await session.execute(index_query)
        indexes = result.fetchall()
        
        print("\n" + "="*60)
        print("🔍 索引信息")
        print("="*60)
        for idx in indexes:
            print(f"{idx[0]:15} | {idx[1]:30} | 大小: {idx[2]}")
        
        print("\n" + "="*60)
        print("💡 性能优化建议")
        print("="*60)
        for tip in PERFORMANCE_TIPS:
            print(f"  • {tip}")
            
    except Exception as e:
        logger.error(f"❌ 生成性能报告失败: {str(e)}")


async def main():
    """主函数"""
    logger.info("🚀 开始数据库优化...")
    
    # 创建数据库引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 1. 创建索引
            logger.info(f"📝 开始创建 {len(INDEX_DEFINITIONS)} 个索引...")
            for index_def in INDEX_DEFINITIONS:
                await create_index(session, index_def)
            
            # 2. 设置 pgvector
            await setup_pgvector(session)
            
            # 3. 分析统计信息
            await analyze_table_stats(session)
            
            # 4. 生成性能报告
            await generate_performance_report(session)
            
            logger.info("🎉 数据库优化完成！")
            
        except Exception as e:
            logger.error(f"❌ 数据库优化过程中出错: {str(e)}")
            raise
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())