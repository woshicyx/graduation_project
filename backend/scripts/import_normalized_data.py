#!/usr/bin/env python3
"""
规范化数据导入脚本 - 导入类型、演员、导演等规范化数据
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path
import logging
from typing import Optional, Dict, List, Tuple, Set
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

class NormalizedDataImporter:
    """规范化数据导入器"""
    
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
        
        # 缓存字典
        self.genre_cache = {}  # tmdb_id -> db_id
        self.actor_cache = {}  # tmdb_id -> db_id
        self.director_cache = {}  # tmdb_id -> db_id
        
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
            required_movie_cols = ['id', 'title', 'genres']
            missing_movie_cols = [col for col in required_movie_cols if col not in movies_df.columns]
            
            if missing_movie_cols:
                return None, None, f"电影数据缺少关键字段: {missing_movie_cols}"
            
            required_credits_cols = ['movie_id', 'cast', 'crew']
            missing_credits_cols = [col for col in required_credits_cols if col not in credits_df.columns]
            
            if missing_credits_cols:
                return None, None, f"演职员数据缺少关键字段: {missing_credits_cols}"
            
            # 数据类型转换
            movies_df['id'] = movies_df['id'].astype(int)
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
    
    def load_cache(self):
        """加载现有数据的缓存"""
        try:
            # 加载类型缓存
            self.cursor.execute("SELECT id, tmdb_id FROM genres")
            for db_id, tmdb_id in self.cursor.fetchall():
                self.genre_cache[tmdb_id] = db_id
            
            # 加载演员缓存
            self.cursor.execute("SELECT id, tmdb_id FROM actors")
            for db_id, tmdb_id in self.cursor.fetchall():
                self.actor_cache[tmdb_id] = db_id
            
            # 加载导演缓存
            self.cursor.execute("SELECT id, tmdb_id FROM directors")
            for db_id, tmdb_id in self.cursor.fetchall():
                self.director_cache[tmdb_id] = db_id
            
            logger.info(f"缓存加载完成: {len(self.genre_cache)} 类型, {len(self.actor_cache)} 演员, {len(self.director_cache)} 导演")
            
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
    
    def import_genres(self, movies_df: pd.DataFrame) -> bool:
        """导入电影类型数据"""
        try:
            logger.info("导入电影类型数据...")
            
            # 收集所有唯一的类型
            all_genres = set()
            for _, row in movies_df.iterrows():
                genres_json = row['genres']
                if pd.notna(genres_json):
                    genres = self.parse_json_field(genres_json)
                    for genre in genres:
                        if 'id' in genre and 'name' in genre:
                            all_genres.add((genre['id'], genre['name']))
            
            logger.info(f"发现 {len(all_genres)} 个唯一电影类型")
            
            # 准备插入数据
            genres_to_insert = []
            for tmdb_id, name in all_genres:
                if tmdb_id not in self.genre_cache:
                    genres_to_insert.append((tmdb_id, name))
            
            if genres_to_insert:
                # 批量插入新类型
                insert_sql = """
                INSERT INTO genres (tmdb_id, name) 
                VALUES (%s, %s)
                ON CONFLICT (tmdb_id) DO NOTHING
                RETURNING id, tmdb_id
                """
                
                execute_batch(self.cursor, insert_sql, genres_to_insert)
                self.conn.commit()
                
                # 更新缓存
                self.cursor.execute("SELECT id, tmdb_id FROM genres")
                for db_id, tmdb_id in self.cursor.fetchall():
                    self.genre_cache[tmdb_id] = db_id
                
                logger.info(f"导入 {len(genres_to_insert)} 个新电影类型")
            else:
                logger.info("没有新的电影类型需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入电影类型失败: {e}")
            self.conn.rollback()
            return False
    
    def import_movie_genres(self, movies_df: pd.DataFrame) -> bool:
        """导入电影-类型关联数据"""
        try:
            logger.info("导入电影-类型关联数据...")
            
            # 收集所有电影-类型关联
            movie_genres_data = []
            for _, row in movies_df.iterrows():
                movie_id = int(row['id'])
                genres_json = row['genres']
                
                if pd.notna(genres_json):
                    genres = self.parse_json_field(genres_json)
                    for genre in genres:
                        if 'id' in genre and genre['id'] in self.genre_cache:
                            genre_id = self.genre_cache[genre['id']]
                            movie_genres_data.append((movie_id, genre_id))
            
            logger.info(f"发现 {len(movie_genres_data)} 个电影-类型关联")
            
            if movie_genres_data:
                # 批量插入关联数据
                insert_sql = """
                INSERT INTO movie_genres (movie_id, genre_id) 
                VALUES (%s, %s)
                ON CONFLICT (movie_id, genre_id) DO NOTHING
                """
                
                execute_batch(self.cursor, insert_sql, movie_genres_data)
                self.conn.commit()
                
                logger.info(f"导入 {len(movie_genres_data)} 个电影-类型关联")
            else:
                logger.info("没有新的电影-类型关联需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入电影-类型关联失败: {e}")
            self.conn.rollback()
            return False
    
    def import_actors(self, credits_df: pd.DataFrame) -> bool:
        """导入演员数据"""
        try:
            logger.info("导入演员数据...")
            
            # 收集所有唯一的演员
            all_actors = set()
            for _, row in credits_df.iterrows():
                cast_json = row['cast']
                if pd.notna(cast_json):
                    cast = self.parse_json_field(cast_json)
                    for actor in cast:
                        if 'id' in actor and 'name' in actor:
                            gender = actor.get('gender', 0)
                            all_actors.add((actor['id'], actor['name'], gender))
            
            logger.info(f"发现 {len(all_actors)} 个唯一演员")
            
            # 准备插入数据
            actors_to_insert = []
            for tmdb_id, name, gender in all_actors:
                if tmdb_id not in self.actor_cache:
                    actors_to_insert.append((tmdb_id, name, gender))
            
            if actors_to_insert:
                # 批量插入新演员
                insert_sql = """
                INSERT INTO actors (tmdb_id, name, gender) 
                VALUES (%s, %s, %s)
                ON CONFLICT (tmdb_id) DO NOTHING
                RETURNING id, tmdb_id
                """
                
                execute_batch(self.cursor, insert_sql, actors_to_insert)
                self.conn.commit()
                
                # 更新缓存
                self.cursor.execute("SELECT id, tmdb_id FROM actors")
                for db_id, tmdb_id in self.cursor.fetchall():
                    self.actor_cache[tmdb_id] = db_id
                
                logger.info(f"导入 {len(actors_to_insert)} 个新演员")
            else:
                logger.info("没有新的演员需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入演员失败: {e}")
            self.conn.rollback()
            return False
    
    def import_movie_actors(self, credits_df: pd.DataFrame) -> bool:
        """导入电影-演员关联数据"""
        try:
            logger.info("导入电影-演员关联数据...")
            
            # 收集所有电影-演员关联
            movie_actors_data = []
            for _, row in credits_df.iterrows():
                movie_id = int(row['movie_id'])
                cast_json = row['cast']
                
                if pd.notna(cast_json):
                    cast = self.parse_json_field(cast_json)
                    for actor_info in cast:
                        if 'id' in actor_info and actor_info['id'] in self.actor_cache:
                            actor_id = self.actor_cache[actor_info['id']]
                            character = actor_info.get('character', '')
                            cast_order = actor_info.get('order', 0)
                            movie_actors_data.append((movie_id, actor_id, character, cast_order))
            
            logger.info(f"发现 {len(movie_actors_data)} 个电影-演员关联")
            
            if movie_actors_data:
                # 批量插入关联数据
                insert_sql = """
                INSERT INTO movie_actors (movie_id, actor_id, character, cast_order) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (movie_id, actor_id, character) DO NOTHING
                """
                
                execute_batch(self.cursor, insert_sql, movie_actors_data)
                self.conn.commit()
                
                logger.info(f"导入 {len(movie_actors_data)} 个电影-演员关联")
            else:
                logger.info("没有新的电影-演员关联需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入电影-演员关联失败: {e}")
            self.conn.rollback()
            return False
    
    def import_directors(self, credits_df: pd.DataFrame) -> bool:
        """导入导演数据"""
        try:
            logger.info("导入导演数据...")
            
            # 收集所有唯一的导演
            all_directors = set()
            for _, row in credits_df.iterrows():
                crew_json = row['crew']
                if pd.notna(crew_json):
                    crew = self.parse_json_field(crew_json)
                    for crew_info in crew:
                        if crew_info.get('job') == 'Director' and 'id' in crew_info and 'name' in crew_info:
                            all_directors.add((crew_info['id'], crew_info['name']))
            
            logger.info(f"发现 {len(all_directors)} 个唯一导演")
            
            # 准备插入数据
            directors_to_insert = []
            for tmdb_id, name in all_directors:
                if tmdb_id not in self.director_cache:
                    directors_to_insert.append((tmdb_id, name))
            
            if directors_to_insert:
                # 批量插入新导演
                insert_sql = """
                INSERT INTO directors (tmdb_id, name) 
                VALUES (%s, %s)
                ON CONFLICT (tmdb_id) DO NOTHING
                RETURNING id, tmdb_id
                """
                
                execute_batch(self.cursor, insert_sql, directors_to_insert)
                self.conn.commit()
                
                # 更新缓存
                self.cursor.execute("SELECT id, tmdb_id FROM directors")
                for db_id, tmdb_id in self.cursor.fetchall():
                    self.director_cache[tmdb_id] = db_id
                
                logger.info(f"导入 {len(directors_to_insert)} 个新导演")
            else:
                logger.info("没有新的导演需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入导演失败: {e}")
            self.conn.rollback()
            return False
    
    def import_movie_directors(self, credits_df: pd.DataFrame) -> bool:
        """导入电影-导演关联数据"""
        try:
            logger.info("导入电影-导演关联数据...")
            
            # 收集所有电影-导演关联
            movie_directors_data = []
            for _, row in credits_df.iterrows():
                movie_id = int(row['movie_id'])
                crew_json = row['crew']
                
                if pd.notna(crew_json):
                    crew = self.parse_json_field(crew_json)
                    for crew_info in crew:
                        if crew_info.get('job') == 'Director' and 'id' in crew_info:
                            tmdb_id = crew_info['id']
                            if tmdb_id in self.director_cache:
                                director_id = self.director_cache[tmdb_id]
                                movie_directors_data.append((movie_id, director_id))
            
            logger.info(f"发现 {len(movie_directors_data)} 个电影-导演关联")
            
            if movie_directors_data:
                # 批量插入关联数据
                insert_sql = """
                INSERT INTO movie_directors (movie_id, director_id) 
                VALUES (%s, %s)
                ON CONFLICT (movie_id, director_id) DO NOTHING
                """
                
                execute_batch(self.cursor, insert_sql, movie_directors_data)
                self.conn.commit()
                
                logger.info(f"导入 {len(movie_directors_data)} 个电影-导演关联")
            else:
                logger.info("没有新的电影-导演关联需要导入")
            
            return True
            
        except Exception as e:
            logger.error(f"导入电影-导演关联失败: {e}")
            self.conn.rollback()
            return False
    
    def update_movie_directors(self, credits_df: pd.DataFrame) -> bool:
        """更新movies表中的director字段"""
        try:
            logger.info("更新movies表中的director字段...")
            
            # 创建导演映射
            director_map = {}
            for _, row in credits_df.iterrows():
                movie_id = int(row['movie_id'])
                crew_json = row['crew']
                
                if pd.notna(crew_json):
                    crew = self.parse_json_field(crew_json)
                    for crew_info in crew:
                        if crew_info.get('job') == 'Director' and 'name' in crew_info:
                            director_map[movie_id] = crew_info['name']
                            break  # 只取第一个导演
            
            # 更新movies表
            update_count = 0
            for movie_id, director in director_map.items():
                self.cursor.execute(
                    "UPDATE movies SET director = %s WHERE id = %s",
                    (director, movie_id)
                )
                if self.cursor.rowcount > 0:
                    update_count += 1
            
            self.conn.commit()
            logger.info(f"更新 {update_count} 个电影的director字段")
            
            return True
            
        except Exception as e:
            logger.error(f"更新movies表director字段失败: {e}")
            self.conn.rollback()
            return False
    
    def verify_data(self) -> bool:
        """验证导入的数据"""
        try:
            logger.info("验证导入的数据...")
            
            # 统计各表数据量
            tables = ['genres', 'movie_genres', 'actors', 'movie_actors', 'directors', 'movie_directors']
            
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                logger.info(f"  📊 {table}表记录数: {count}")
            
            # 检查示例数据
            logger.info("示例数据:")
            
            # 类型示例
            self.cursor.execute("SELECT name FROM genres LIMIT 5")
            genres = self.cursor.fetchall()
            logger.info(f"  类型示例: {', '.join([g[0] for g in genres])}")
            
            # 演员示例
            self.cursor.execute("SELECT name FROM actors LIMIT 5")
            actors = self.cursor.fetchall()
            logger.info(f"  演员示例: {', '.join([a[0] for a in actors])}")
            
            # 导演示例
            self.cursor.execute("SELECT name FROM directors LIMIT 5")
            directors = self.cursor.fetchall()
            logger.info(f"  导演示例: {', '.join([d[0] for d in directors])}")
            
            logger.info("✅ 数据验证完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据验证失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("TMDB 5000 规范化数据导入工具")
    print("=" * 60)
    
    # 创建导入器
    importer = NormalizedDataImporter(data_dir=".")
    
    # 连接到数据库
    if not importer.connect():
        print("数据库连接失败，请检查数据库配置")
        return
    
    try:
        # 加载数据
        print("\n1. 加载CSV数据...")
        movies_df, credits_df, load_message = importer.load_data()
        
        if movies_df is None:
            print(f"数据加载失败: {load_message}")
            return
        
        print(f"数据加载成功:")
        print(f"  - 电影数据: {movies_df.shape[0]} 行")
        print(f"  - 演职员数据: {credits_df.shape[0]} 行")
        
        # 加载缓存
        print("\n2. 加载现有数据缓存...")
        importer.load_cache()
        
        # 导入类型数据
        print("\n3. 导入电影类型数据...")
        if not importer.import_genres(movies_df):
            print("导入电影类型数据失败")
            return
        
        # 导入电影-类型关联
        print("\n4. 导入电影-类型关联数据...")
        if not importer.import_movie_genres(movies_df):
            print("导入电影-类型关联数据失败")
            return
        
        # 导入演员数据
        print("\n5. 导入演员数据...")
        if not importer.import_actors(credits_df):
            print("导入演员数据失败")
            return
        
        # 导入电影-演员关联
        print("\n6. 导入电影-演员关联数据...")
        if not importer.import_movie_actors(credits_df):
            print("导入电影-演员关联数据失败")
            return
        
        # 导入导演数据
        print("\n7. 导入导演数据...")
        if not importer.import_directors(credits_df):
            print("导入导演数据失败")
            return
        
        # 导入电影-导演关联
        print("\n8. 导入电影-导演关联数据...")
        if not importer.import_movie_directors(credits_df):
            print("导入电影-导演关联数据失败")
            return
        
        # 更新movies表的director字段
        print("\n9. 更新movies表的director字段...")
        if not importer.update_movie_directors(credits_df):
            print("更新movies表director字段失败")
            return
        
        # 验证数据
        print("\n10. 验证导入的数据...")
        if not importer.verify_data():
            print("数据验证失败")
            return
        
        print("\n" + "=" * 60)
        print("✅ 规范化数据导入完成！")
        print("=" * 60)
        
    finally:
        # 断开数据库连接
        importer.disconnect()

if __name__ == "__main__":
    main()
