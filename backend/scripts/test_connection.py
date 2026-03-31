#!/usr/bin/env python3
"""
数据库连接测试脚本
"""

import os
import sys
import psycopg2
import time
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionTester:
    """数据库连接测试器"""
    
    def __init__(self, password="356921"):
        """初始化测试器"""
        self.db_configs = {
            'postgres': {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': password,
                'database': 'postgres'
            },
            'movie_recommendation': {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': password,
                'database': 'movie_recommendation'
            }
        }
    
    def test_connection(self, db_name: str) -> bool:
        """测试数据库连接"""
        try:
            config = self.db_configs.get(db_name)
            if not config:
                logger.error(f"未知数据库: {db_name}")
                return False
            
            start_time = time.time()
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # 测试查询
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_user")
            current_user = cursor.fetchone()[0]
            
            # 获取数据库信息
            cursor.execute("""
                SELECT 
                    pg_database_size(%s) as db_size,
                    pg_size_pretty(pg_database_size(%s)) as db_size_pretty
            """, (db_name, db_name))
            db_info = cursor.fetchone()
            
            elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 数据库 '{db_name}' 连接成功")
            logger.info(f"  连接时间: {elapsed_time:.2f}ms")
            logger.info(f"  数据库: {current_db}")
            logger.info(f"  用户: {current_user}")
            logger.info(f"  数据库大小: {db_info[1]}")
            logger.info(f"  PostgreSQL版本: {version.split(',')[0]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库 '{db_name}' 连接失败: {e}")
            return False
    
    def test_query_performance(self, db_name: str) -> bool:
        """测试查询性能"""
        try:
            config = self.db_configs.get(db_name)
            if not config:
                return False
            
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            logger.info(f"测试数据库 '{db_name}' 查询性能...")
            
            # 测试1: 简单查询
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM movies")
            movie_count = cursor.fetchone()[0]
            simple_query_time = (time.time() - start_time) * 1000
            
            # 测试2: 带条件的查询
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM movies WHERE vote_average > 7.0")
            high_rated_count = cursor.fetchone()[0]
            conditional_query_time = (time.time() - start_time) * 1000
            
            # 测试3: 连接查询
            start_time = time.time()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM movies m
                JOIN movie_genres mg ON m.id = mg.movie_id
                JOIN genres g ON mg.genre_id = g.id
                WHERE g.name = 'Action'
            """)
            action_movies_count = cursor.fetchone()[0]
            join_query_time = (time.time() - start_time) * 1000
            
            # 测试4: 排序查询
            start_time = time.time()
            cursor.execute("""
                SELECT title, vote_average, revenue 
                FROM movies 
                WHERE vote_average > 0 
                ORDER BY vote_average DESC 
                LIMIT 10
            """)
            top_movies = cursor.fetchall()
            sort_query_time = (time.time() - start_time) * 1000
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 查询性能测试完成:")
            logger.info(f"  电影总数: {movie_count}")
            logger.info(f"  高评分电影(vote_average > 7.0): {high_rated_count}")
            logger.info(f"  动作电影: {action_movies_count}")
            logger.info(f"  简单查询时间: {simple_query_time:.2f}ms")
            logger.info(f"  条件查询时间: {conditional_query_time:.2f}ms")
            logger.info(f"  连接查询时间: {join_query_time:.2f}ms")
            logger.info(f"  排序查询时间: {sort_query_time:.2f}ms")
            
            # 显示前5部高评分电影
            logger.info(f"  评分最高的5部电影:")
            for i, movie in enumerate(top_movies[:5], 1):
                title, rating, revenue = movie
                revenue_str = f"${revenue:,}" if revenue else "未知"
                logger.info(f"    {i}. {title} - 评分: {rating:.1f}, 票房: {revenue_str}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 查询性能测试失败: {e}")
            return False
    
    def check_tables(self, db_name: str) -> bool:
        """检查数据库表结构"""
        try:
            config = self.db_configs.get(db_name)
            if not config:
                return False
            
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            logger.info(f"检查数据库 '{db_name}' 表结构...")
            
            # 获取所有表
            cursor.execute("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            logger.info(f"  发现 {len(tables)} 个表:")
            for table_name, table_type in tables:
                # 获取表信息
                cursor.execute("""
                    SELECT 
                        COUNT(*) as row_count,
                        pg_size_pretty(pg_total_relation_size(%s)) as table_size
                """, (f"public.{table_name}",))
                
                try:
                    row_count, table_size = cursor.fetchone()
                    logger.info(f"    📊 {table_name} ({table_type}): {row_count} 行, 大小: {table_size}")
                except:
                    logger.info(f"    📊 {table_name} ({table_type})")
            
            # 检查索引
            cursor.execute("""
                SELECT 
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            indexes = cursor.fetchall()
            
            logger.info(f"  发现 {len(indexes)} 个索引:")
            for tablename, indexname, indexdef in indexes[:10]:  # 只显示前10个
                logger.info(f"    🔍 {tablename}.{indexname}")
            
            if len(indexes) > 10:
                logger.info(f"    ... 还有 {len(indexes) - 10} 个索引")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查表结构失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("数据库连接和性能测试")
        print("=" * 60)
        
        all_passed = True
        
        # 测试postgres数据库连接
        print("\n1. 测试postgres数据库连接...")
        if not self.test_connection('postgres'):
            all_passed = False
        
        # 测试movie_recommendation数据库连接
        print("\n2. 测试movie_recommendation数据库连接...")
        if not self.test_connection('movie_recommendation'):
            all_passed = False
        
        # 检查movie_recommendation数据库表结构
        print("\n3. 检查movie_recommendation数据库表结构...")
        if not self.check_tables('movie_recommendation'):
            all_passed = False
        
        # 测试查询性能
        print("\n4. 测试查询性能...")
        if not self.test_query_performance('movie_recommendation'):
            all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ 所有测试通过!")
        else:
            print("❌ 部分测试失败")
        print("=" * 60)
        
        return all_passed

def main():
    """主函数"""
    tester = DatabaseConnectionTester(password="356921")
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()