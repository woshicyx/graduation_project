#!/usr/bin/env python3
"""
TMDB 5000 数据集导入到PostgreSQL数据库
简化版本 - 只导入核心电影数据
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path
import logging
from typing import Optional, Dict, List, Tuple
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2.extensions import register_adapter, AsIs
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 适配numpy类型到PostgreSQL
def adapt_numpy_int64(numpy_int64):
    return AsIs(int(numpy_int64))

def adapt_numpy_float64(numpy_float64):
    return AsIs(float(numpy_float64))

register_adapter(np.int64, adapt_numpy_int64)
register_adapter(np.float64, adapt_numpy_float64)

class TMDBDatabaseImporter:
    """TMDB数据集数据库导入器"""
    
    def __init__(self, 
                 data_dir: str = ".",
                 db_config: Optional[Dict] = None):
        """
        初始化导入器
        
        Args:
            data_dir: 数据存储目录
            db_config: 数据库配置
        """
        self.data_dir = Path(data_dir)
        
        # 默认数据库配置
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'movie_recommendation',
            'user': 'postgres',
            'password': '356921'
        }
        
        self.conn = None
        self.cursor = None
        
    def connect(self) -> bool:
        """连接到数据库"""
        try:
            logger.info(f"连接到数据库: {self.db_config['database']}")
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")
    
    def create_schema(self) -> bool:
        """
        创建简化的数据库架构
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("创建数据库架构...")
            
            # 创建电影表（简化版本）
            movies_table_sql = """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
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
                status VARCHAR(50),
                genres TEXT,  -- 存储为JSON字符串
                director VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # 创建索引
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);",
                "CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date);",
                "CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average);",
                "CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity);",
                "CREATE INDEX IF NOT EXISTS idx_movies_revenue ON movies(revenue);"
            ]
            
            # 执行创建语句
            self.cursor.execute(movies_table_sql)
            
            # 创建索引
            for sql in indexes_sql:
                self.cursor.execute(sql)
            
            self.conn.commit()
            logger.info("数据库架构创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建数据库架构失败: {e}")
            self.conn.rollback()
            return False
    
    def load_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], str]:
        """
        加载CSV数据
        
        Returns:
            Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], str]: 
            (电影DataFrame, 演职员DataFrame, 错误信息)
        """
        try:
            movies_path = self.data_dir / "tmdb_5000_movies.csv"
            credits_path = self.data_dir / "tmdb_5000_credits.csv"
            
            if not movies_path.exists():
                return None, None, f"电影数据文件不存在: {movies_path}"
            if not credits_path.exists():
                return None, None, f"演职员数据文件不存在: {credits_path}"
            
            logger.info("正在加载电影数据...")
            movies_df = pd.read_csv(movies_path)
            
            logger.info("正在加载演职员数据...")
            credits_df = pd.read_csv(credits_path)
            
            # 基本验证
            logger.info(f"电影数据形状: {movies_df.shape}")
            logger.info(f"演职员数据形状: {credits_df.shape}")
            
            # 检查关键字段
            required_movie_cols = ['id', 'title', 'overview', 'release_date', 'vote_average']
            missing_movie_cols = [col for col in required_movie_cols if col not in movies_df.columns]
            
            if missing_movie_cols:
                return None, None, f"电影数据缺少关键字段: {missing_movie_cols}"
            
            required_credits_cols = ['movie_id', 'title', 'cast', 'crew']
            missing_credits_cols = [col for col in required_credits_cols if col not in credits_df.columns]
            
            if missing_credits_cols:
                return None, None, f"演职员数据缺少关键字段: {missing_credits_cols}"
            
            # 数据类型转换
            movies_df['id'] = movies_df['id'].astype(int)
            movies_df['release_date'] = pd.to_datetime(movies_df['release_date'], errors='coerce')
            movies_df['vote_average'] = pd.to_numeric(movies_df['vote_average'], errors='coerce')
            movies_df['budget'] = pd.to_numeric(movies_df['budget'], errors='coerce')
            movies_df['revenue'] = pd.to_numeric(movies_df['revenue'], errors='coerce')
            movies_df['popularity'] = pd.to_numeric(movies_df['popularity'], errors='coerce')
            movies_df['runtime'] = pd.to_numeric(movies_df['runtime'], errors='coerce')
            movies_df['vote_count'] = pd.to_numeric(movies_df['vote_count'], errors='coerce')
            
            credits_df['movie_id'] = credits_df['movie_id'].astype(int)
            
            logger.info("数据加载完成")
            return movies_df, credits_df, "成功"
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            return None, None, str(e)
    
    def parse_json_field(self, json_str: str) -> List[Dict]:
        """解析JSON字段"""
        try:
            if pd.isna(json_str) or json_str == '':
                return []
            return json.loads(json_str)
        except:
            return []
    
    def extract_director(self, crew_json: str) -> str:
        """从crew字段提取导演"""
        try:
            if pd.isna(crew_json) or crew_json == '':
                return ''
            
            crew = json.loads(crew_json)
            for crew_info in crew:
                if crew_info.get('job') == 'Director' and 'name' in crew_info:
                    return crew_info['name']
            return ''
        except:
            return ''
    
    def extract_genres(self, genres_json: str) -> str:
        """从genres字段提取类型"""
        try:
            if pd.isna(genres_json) or genres_json == '':
                return '[]'
            
            genres = json.loads(genres_json)
            genre_names = [genre.get('name', '') for genre in genres if 'name' in genre]
            return json.dumps(genre_names)
        except:
            return '[]'
    
    def import_data(self, movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> bool:
        """导入所有数据"""
        try:
            logger.info("开始导入数据...")
            
            # 创建导演映射
            director_map = {}
            for _, row in credits_df.iterrows():
                movie_id = int(row['movie_id'])
                director = self.extract_director(row['crew'])
                if director:
                    director_map[movie_id] = director
            
            # 准备电影数据
            movies_data = []
            for _, row in movies_df.iterrows():
                movie_id = int(row['id'])
                
                # 提取类型
                genres_json = self.extract_genres(row['genres'])
                
                # 获取导演
                director = director_map.get(movie_id, '')
                
                movie_data = (
                    movie_id,
                    str(row['title'])[:500] if pd.notna(row['title']) else '',
                    str(row['overview']) if pd.notna(row['overview']) else '',
                    str(row['tagline']) if pd.notna(row['tagline']) else '',
                    int(row['budget']) if pd.notna(row['budget']) else 0,
                    int(row['revenue']) if pd.notna(row['revenue']) else 0,
                    float(row['popularity']) if pd.notna(row['popularity']) else 0.0,
                    row['release_date'] if pd.notna(row['release_date']) else None,
                    int(row['runtime']) if pd.notna(row['runtime']) else 0,
                    float(row['vote_average']) if pd.notna(row['vote_average']) else 0.0,
                    int(row['vote_count']) if pd.notna(row['vote_count']) else 0,
                    '',  # poster_path - 原始CSV中没有这个字段
                    str(row['status']) if pd.notna(row['status']) else '',
                    genres_json,
                    director
                )
                movies_data.append(movie_data)
            
            # 批量插入电影数据
            insert_sql = """
            INSERT INTO movies (
                id, title, overview, tagline, budget, revenue, popularity,
                release_date, runtime, vote_average, vote_count, poster_path,
                status, genres, director
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                overview = EXCLUDED.overview,
                tagline = EXCLUDED.tagline,
                budget = EXCLUDED.budget,
                revenue = EXCLUDED.revenue,
                popularity = EXCLUDED.popularity,
                release_date = EXCLUDED.release_date,
                runtime = EXCLUDED.runtime,
                vote_average = EXCLUDED.vote_average,
                vote_count = EXCLUDED.vote_count,
                poster_path = EXCLUDED.poster_path,
                status = EXCLUDED.status,
                genres = EXCLUDED.genres,
                director = EXCLUDED.director,
                updated_at = CURRENT_TIMESTAMP
            """
            
            execute_batch(self.cursor, insert_sql, movies_data)
            self.conn.commit()
            
            logger.info(f"导入电影数据完成: {len(movies_data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"导入数据失败: {e}")
            self.conn.rollback()
            return False
    
    def verify_data(self) -> bool:
        """验证导入的数据"""
        try:
            logger.info("验证导入的数据...")
            
            # 统计电影数量
            self.cursor.execute("SELECT COUNT(*) FROM movies")
            movie_count = self.cursor.fetchone()[0]
            
            # 统计有预算的电影
            self.cursor.execute("SELECT COUNT(*) FROM movies WHERE budget > 0")
            budget_count = self.cursor.fetchone()[0]
            
            # 统计有票房收入的电影
            self.cursor.execute("SELECT COUNT(*) FROM movies WHERE revenue > 0")
            revenue_count = self.cursor.fetchone()[0]
            
            # 统计有评分的电影
            self.cursor.execute("SELECT COUNT(*) FROM movies WHERE vote_average > 0")
            rating_count = self.cursor.fetchone()[0]
            
            # 获取示例数据
            self.cursor.execute("""
                SELECT id, title, release_date, vote_average, revenue, director 
                FROM movies 
                WHERE vote_average > 7.5 
                ORDER BY vote_average DESC 
                LIMIT 5
            """)
            top_movies = self.cursor.fetchall()
            
            logger.info(f"数据验证结果:")
            logger.info(f"  - 总电影数: {movie_count}")
            logger.info(f"  - 有预算的电影: {budget_count}")
            logger.info(f"  - 有票房收入的电影: {revenue_count}")
            logger.info(f"  - 有评分的电影: {rating_count}")
            
            logger.info(f"评分最高的5部电影:")
            for movie in top_movies:
                logger.info(f"  - {movie[1]} ({movie[2]}) - 评分: {movie[3]}, 票房: ${movie[4]:,}, 导演: {movie[5]}")
            
            return True
            
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("TMDB 5000 数据集导入工具")
    print("=" * 60)
    
    # 创建导入器
    importer = TMDBDatabaseImporter(data_dir=".")
    
    # 连接到数据库
    if not importer.connect():
        print("数据库连接失败，请检查数据库配置")
        return
    
    try:
        # 创建数据库架构
        print("\n1. 创建数据库架构...")
        if not importer.create_schema():
            print("创建数据库架构失败")
            return
        
        # 加载数据
        print("\n2. 加载CSV数据...")
        movies_df, credits_df, load_message = importer.load_data()
        
        if movies_df is None:
            print(f"数据加载失败: {load_message}")
            print("\n请先运行下载脚本:")
            print("  python backend/scripts/download_tmdb_data.py")
            return
        
        print(f"数据加载成功:")
        print(f"  - 电影数据: {movies_df.shape[0]} 行, {movies_df.shape[1]} 列")
        print(f"  - 演职员数据: {credits_df.shape[0]} 行, {credits_df.shape[1]} 列")
        
        # 导入数据
        print("\n3. 导入数据到数据库...")
        if not importer.import_data(movies_df, credits_df):
            print("数据导入失败")
            return
        
        # 验证数据
        print("\n4. 验证导入的数据...")
        if not importer.verify_data():
            print("数据验证失败")
            return
        
        print("\n" + "=" * 60)
        print("数据导入完成！")
        print("=" * 60)
        
    finally:
        # 断开数据库连接
        importer.disconnect()

if __name__ == "__main__":
    main()