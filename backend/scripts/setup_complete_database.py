#!/usr/bin/env python3
"""
完整数据库设置脚本 - 创建增强版数据库架构
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteDatabaseSetup:
    """完整数据库设置类"""
    
    def __init__(self, password="356921"):
        """初始化数据库设置"""
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': password,
            'database': 'postgres'
        }
        self.target_db = 'movie_recommendation'
        self.conn = None
        self.cursor = None
    
    def connect(self, database='postgres'):
        """连接到数据库"""
        try:
            config = self.db_config.copy()
            config['database'] = database
            self.conn = psycopg2.connect(**config)
            self.cursor = self.conn.cursor()
            logger.info(f"✅ 连接到数据库: {database}")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")
    
    def create_database(self):
        """创建电影推荐数据库"""
        try:
            # 连接到默认数据库
            if not self.connect('postgres'):
                return False
            
            self.conn.autocommit = True
            
            # 检查数据库是否已存在
            self.cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.target_db,))
            exists = self.cursor.fetchone()
            
            if not exists:
                # 创建数据库
                self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.target_db)))
                logger.info(f"✅ 数据库 '{self.target_db}' 创建成功")
            else:
                logger.info(f"✅ 数据库 '{self.target_db}' 已存在")
            
            self.disconnect()
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库创建失败: {e}")
            return False
    
    def create_complete_schema(self):
        """创建完整的数据库架构"""
        try:
            # 连接到目标数据库
            if not self.connect(self.target_db):
                return False
            
            logger.info("创建完整的数据库架构...")
            
            # 1. 创建movies表
            movies_table_sql = """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                original_title VARCHAR(500),
                overview TEXT,
                tagline TEXT,
                budget BIGINT,
                revenue BIGINT,
                popularity FLOAT,
                release_date DATE,
                runtime INTEGER,
                vote_average FLOAT,
                vote_count INTEGER,
                poster_path VARCHAR(500),
                homepage VARCHAR(500),
                status VARCHAR(50),
                original_language VARCHAR(10),
                genres TEXT,
                keywords TEXT,
                production_companies TEXT,
                production_countries TEXT,
                spoken_languages TEXT,
                director VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 2. 创建genres表
            genres_table_sql = """
            CREATE TABLE IF NOT EXISTS genres (
                id SERIAL PRIMARY KEY,
                tmdb_id INTEGER UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 3. 创建movie_genres表
            movie_genres_table_sql = """
            CREATE TABLE IF NOT EXISTS movie_genres (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
                PRIMARY KEY (movie_id, genre_id)
            );
            """
            
            # 4. 创建actors表
            actors_table_sql = """
            CREATE TABLE IF NOT EXISTS actors (
                id SERIAL PRIMARY KEY,
                tmdb_id INTEGER UNIQUE NOT NULL,
                name VARCHAR(500) NOT NULL,
                gender INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 5. 创建movie_actors表
            movie_actors_table_sql = """
            CREATE TABLE IF NOT EXISTS movie_actors (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                actor_id INTEGER REFERENCES actors(id) ON DELETE CASCADE,
                character VARCHAR(500),
                cast_order INTEGER,
                PRIMARY KEY (movie_id, actor_id, character)
            );
            """
            
            # 6. 创建directors表
            directors_table_sql = """
            CREATE TABLE IF NOT EXISTS directors (
                id SERIAL PRIMARY KEY,
                tmdb_id INTEGER UNIQUE NOT NULL,
                name VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 7. 创建movie_directors表
            movie_directors_table_sql = """
            CREATE TABLE IF NOT EXISTS movie_directors (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                director_id INTEGER REFERENCES directors(id) ON DELETE CASCADE,
                PRIMARY KEY (movie_id, director_id)
            );
            """
            
            # 8. 创建users表
            users_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                preferences JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 9. 创建user_ratings表
            user_ratings_table_sql = """
            CREATE TABLE IF NOT EXISTS user_ratings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                rating FLOAT CHECK (rating >= 0 AND rating <= 10),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, movie_id)
            );
            """
            
            # 10. 创建user_watch_history表
            user_watch_history_table_sql = """
            CREATE TABLE IF NOT EXISTS user_watch_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                watch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                watch_duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 执行所有创建语句
            tables_sql = [
                movies_table_sql,
                genres_table_sql,
                movie_genres_table_sql,
                actors_table_sql,
                movie_actors_table_sql,
                directors_table_sql,
                movie_directors_table_sql,
                users_table_sql,
                user_ratings_table_sql,
                user_watch_history_table_sql
            ]
            
            for i, sql_statement in enumerate(tables_sql, 1):
                try:
                    self.cursor.execute(sql_statement)
                    logger.info(f"  表 {i}/10 创建成功")
                except Exception as e:
                    logger.warning(f"  表 {i}/10 创建时出现警告: {e}")
                    self.conn.rollback()
                    # 继续执行下一个表
            
            self.conn.commit()
            
            # 创建索引
            logger.info("创建索引...")
            self.create_indexes()
            
            logger.info("✅ 完整的数据库架构创建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建数据库架构失败: {e}")
            self.conn.rollback()
            return False
    
    def create_indexes(self):
        """创建所有索引"""
        try:
            # movies表索引
            indexes_sql = [
                # movies表索引
                "CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);",
                "CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date);",
                "CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average);",
                "CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity);",
                "CREATE INDEX IF NOT EXISTS idx_movies_revenue ON movies(revenue);",
                "CREATE INDEX IF NOT EXISTS idx_movies_runtime ON movies(runtime);",
                "CREATE INDEX IF NOT EXISTS idx_movies_vote_count ON movies(vote_count);",
                
                # 关联表索引
                "CREATE INDEX IF NOT EXISTS idx_movie_genres_movie_id ON movie_genres(movie_id);",
                "CREATE INDEX IF NOT EXISTS idx_movie_genres_genre_id ON movie_genres(genre_id);",
                "CREATE INDEX IF NOT EXISTS idx_movie_actors_movie_id ON movie_actors(movie_id);",
                "CREATE INDEX IF NOT EXISTS idx_movie_actors_actor_id ON movie_actors(actor_id);",
                "CREATE INDEX IF NOT EXISTS idx_movie_directors_movie_id ON movie_directors(movie_id);",
                "CREATE INDEX IF NOT EXISTS idx_movie_directors_director_id ON movie_directors(director_id);",
                
                # 用户相关索引
                "CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON user_ratings(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_user_ratings_movie_id ON user_ratings(movie_id);",
                "CREATE INDEX IF NOT EXISTS idx_user_ratings_rating ON user_ratings(rating);",
                "CREATE INDEX IF NOT EXISTS idx_user_watch_history_user_id ON user_watch_history(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_user_watch_history_movie_id ON user_watch_history(movie_id);"
            ]
            
            for i, sql_statement in enumerate(indexes_sql, 1):
                try:
                    self.cursor.execute(sql_statement)
                    logger.info(f"  索引 {i}/{len(indexes_sql)} 创建成功")
                except Exception as e:
                    logger.warning(f"  索引 {i}/{len(indexes_sql)} 创建时出现警告: {e}")
                    self.conn.rollback()
            
            self.conn.commit()
            logger.info("✅ 所有索引创建成功")
            
        except Exception as e:
            logger.error(f"❌ 创建索引失败: {e}")
            self.conn.rollback()
    
    def enable_pgvector_extension(self):
        """启用pgvector扩展"""
        try:
            logger.info("启用pgvector扩展...")
            
            # 检查是否已安装pgvector
            self.cursor.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
            if not self.cursor.fetchone():
                logger.warning("pgvector扩展未安装，请先安装pgvector")
                return False
            
            # 启用扩展
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.conn.commit()
            
            # 创建向量表
            vector_table_sql = """
            CREATE TABLE IF NOT EXISTS movie_vectors (
                movie_id INTEGER PRIMARY KEY REFERENCES movies(id),
                embedding vector(1536),
                text_content TEXT,
                embedding_type VARCHAR(50) DEFAULT 'openai',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            self.cursor.execute(vector_table_sql)
            
            # 创建向量索引
            vector_index_sql = """
            CREATE INDEX IF NOT EXISTS idx_movie_vectors_embedding 
            ON movie_vectors 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
            """
            
            self.cursor.execute(vector_index_sql)
            self.conn.commit()
            
            logger.info("✅ pgvector扩展和向量表创建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启用pgvector扩展失败: {e}")
            self.conn.rollback()
            return False
    
    def verify_schema(self):
        """验证数据库架构"""
        try:
            logger.info("验证数据库架构...")
            
            # 检查所有表是否存在
            tables = [
                'movies', 'genres', 'movie_genres', 'actors', 'movie_actors',
                'directors', 'movie_directors', 'users', 'user_ratings', 'user_watch_history'
            ]
            
            for table in tables:
                self.cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table,))
                exists = self.cursor.fetchone()[0]
                if exists:
                    logger.info(f"  ✅ 表 '{table}' 存在")
                else:
                    logger.warning(f"  ⚠️  表 '{table}' 不存在")
            
            # 检查movies表数据
            self.cursor.execute("SELECT COUNT(*) FROM movies")
            movie_count = self.cursor.fetchone()[0]
            logger.info(f"  📊 movies表记录数: {movie_count}")
            
            # 检查索引
            self.cursor.execute("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE tablename IN ('movies', 'genres', 'movie_genres', 'actors', 'movie_actors', 
                                   'directors', 'movie_directors', 'users', 'user_ratings', 'user_watch_history')
            """)
            index_count = self.cursor.fetchone()[0]
            logger.info(f"  📊 索引总数: {index_count}")
            
            logger.info("✅ 数据库架构验证完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 验证数据库架构失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("智能电影推荐平台 - 完整数据库设置工具")
    print("=" * 60)
    
    # 创建数据库设置实例
    setup = CompleteDatabaseSetup(password="356921")
    
    try:
        # 1. 创建数据库
        print("\n1. 创建数据库...")
        if not setup.create_database():
            print("创建数据库失败")
            return
        
        # 2. 创建完整架构
        print("\n2. 创建完整数据库架构...")
        if not setup.create_complete_schema():
            print("创建数据库架构失败")
            return
        
        # 3. 启用pgvector扩展
        print("\n3. 启用pgvector扩展...")
        setup.enable_pgvector_extension()
        
        # 4. 验证架构
        print("\n4. 验证数据库架构...")
        setup.verify_schema()
        
        print("\n" + "=" * 60)
        print("✅ 完整数据库设置完成!")
        print("\n下一步:")
        print("1. 导入TMDB数据:")
        print("   python backend/scripts/import_tmdb_to_db.py")
        print("\n2. 导入规范化数据:")
        print("   python backend/scripts/import_normalized_data.py")
        print("\n3. 测试数据库连接:")
        print("   python backend/scripts/test_connection.py")
        print("\n4. 启动开发服务器:")
        print("   python -m uvicorn app.main:app --reload")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 数据库设置过程中出现错误: {e}")
        return False
    finally:
        setup.disconnect()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)