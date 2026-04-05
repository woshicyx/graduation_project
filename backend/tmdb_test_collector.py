#!/usr/bin/env python3
"""
TMDB测试数据收集器 - 小型测试版本
用于测试API连接和数据收集功能
"""

import time
import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psycopg2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TMDBTestCollector:
    """TMDB测试收集器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # 数据库配置
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'movie_recommendation',
            'user': 'postgres',
            'password': '356921'
        }
        
        self.conn = None
        self.cursor = None
    
    def connect_db(self) -> bool:
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
    
    def disconnect_db(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")
    
    def test_api_connection(self) -> bool:
        """测试TMDB API连接"""
        try:
            logger.info("测试TMDB API连接...")
            params = {
                'api_key': self.api_key,
                'language': 'zh-CN',
                'page': 1
            }
            
            response = self.session.get(
                f"{self.base_url}/movie/popular",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                movies = data.get('results', [])
                logger.info(f"API连接成功! 获取到 {len(movies)} 部流行电影")
                if movies:
                    logger.info(f"示例电影: {movies[0].get('title')} (ID: {movies[0].get('id')})")
                return True
            else:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            return False
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """获取电影详情"""
        try:
            params = {
                'api_key': self.api_key,
                'language': 'zh-CN',
                'append_to_response': 'credits,keywords'
            }
            
            response = self.session.get(
                f"{self.base_url}/movie/{movie_id}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"获取电影详情失败 (ID: {movie_id}): {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取电影详情异常 (ID: {movie_id}): {e}")
            return None
    
    def extract_director(self, credits_data: Dict) -> str:
        """提取导演信息"""
        try:
            if not credits_data or 'crew' not in credits_data:
                return ''
            
            for crew_member in credits_data['crew']:
                if crew_member.get('job') == 'Director' and 'name' in crew_member:
                    return crew_member['name']
            return ''
        except:
            return ''
    
    def extract_json_list(self, data_list: List[Dict], key: str = 'name') -> str:
        """提取JSON列表"""
        try:
            if not data_list:
                return '[]'
            
            items = [item.get(key, '') for item in data_list if item.get(key)]
            return json.dumps(items)
        except:
            return '[]'
    
    def save_test_movie(self, movie_data: Dict) -> bool:
        """保存测试电影数据"""
        try:
            movie_id = movie_data.get('id')
            if not movie_id:
                logger.error("电影数据缺少ID")
                return False
            
            # 提取credits信息
            credits = movie_data.get('credits', {})
            
            # 准备所有25个字段的数据
            movie_record = (
                movie_id,                                           # id
                movie_data.get('title', '')[:500],                  # title
                movie_data.get('original_title', ''),               # original_title
                movie_data.get('overview', ''),                     # overview
                movie_data.get('tagline', ''),                      # tagline
                movie_data.get('budget', 0),                        # budget
                movie_data.get('revenue', 0),                       # revenue
                movie_data.get('popularity', 0.0),                  # popularity
                movie_data.get('release_date'),                     # release_date
                movie_data.get('runtime', 0),                       # runtime
                movie_data.get('vote_average', 0.0),                # vote_average
                movie_data.get('vote_count', 0),                    # vote_count
                movie_data.get('poster_path', ''),                  # poster_path
                movie_data.get('homepage', ''),                     # homepage
                movie_data.get('status', ''),                       # status
                movie_data.get('original_language', ''),            # original_language
                self.extract_json_list(movie_data.get('genres', [])), # genres
                self.extract_json_list(movie_data.get('keywords', {}).get('keywords', [])), # keywords
                self.extract_json_list(movie_data.get('production_companies', [])), # production_companies
                self.extract_json_list(movie_data.get('production_countries', []), 'iso_3166_1'), # production_countries
                self.extract_json_list(movie_data.get('spoken_languages', []), 'iso_639_1'), # spoken_languages
                self.extract_director(credits),                     # director
                None,                                               # created_at
                None,                                               # updated_at
                ''                                                  # rag_text
            )
            
            # 插入或更新数据
            insert_sql = """
            INSERT INTO movies (
                id, title, original_title, overview, tagline, budget, revenue, popularity,
                release_date, runtime, vote_average, vote_count, poster_path, homepage,
                status, original_language, genres, keywords, production_companies,
                production_countries, spoken_languages, director, created_at, updated_at, rag_text
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                original_title = EXCLUDED.original_title,
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
                homepage = EXCLUDED.homepage,
                status = EXCLUDED.status,
                original_language = EXCLUDED.original_language,
                genres = EXCLUDED.genres,
                keywords = EXCLUDED.keywords,
                production_companies = EXCLUDED.production_companies,
                production_countries = EXCLUDED.production_countries,
                spoken_languages = EXCLUDED.spoken_languages,
                director = EXCLUDED.director,
                updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(insert_sql, movie_record)
            self.conn.commit()
            
            logger.info(f"成功保存电影: {movie_data.get('title')} (ID: {movie_id})")
            return True
            
        except Exception as e:
            logger.error(f"保存电影数据失败 (ID: {movie_id}): {e}")
            self.conn.rollback()
            return False
    
    def collect_test_data(self, test_count: int = 10) -> bool:
        """收集测试数据"""
        logger.info(f"开始收集 {test_count} 部测试电影数据")
        
        try:
            # 获取流行电影列表
            params = {
                'api_key': self.api_key,
                'language': 'zh-CN',
                'page': 1
            }
            
            response = self.session.get(
                f"{self.base_url}/movie/popular",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"获取流行电影失败: {response.status_code}")
                return False
            
            data = response.json()
            movies = data.get('results', [])
            
            if not movies:
                logger.error("未获取到电影数据")
                return False
            
            logger.info(f"获取到 {len(movies)} 部流行电影")
            
            # 收集指定数量的电影
            collected = 0
            for movie_summary in movies:
                if collected >= test_count:
                    break
                
                movie_id = movie_summary.get('id')
                if not movie_id:
                    continue
                
                logger.info(f"处理电影 {collected + 1}/{test_count}: ID={movie_id}")
                
                # 获取电影详情
                movie_details = self.get_movie_details(movie_id)
                if not movie_details:
                    time.sleep(0.5)  # 避免过快请求
                    continue
                
                # 保存电影数据
                if self.save_test_movie(movie_details):
                    collected += 1
                    logger.info(f"成功保存第 {collected} 部电影")
                
                # 控制请求速率
                time.sleep(0.5)
            
            logger.info(f"测试数据收集完成! 共收集 {collected} 部电影")
            return True
            
        except Exception as e:
            logger.error(f"收集测试数据过程中出错: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("TMDB测试数据收集器")
    print("=" * 60)
    
    # API密钥
    API_KEY = "b569b88efd591d1c673734fca9242588"
    
    # 创建收集器
    collector = TMDBTestCollector(api_key=API_KEY)
    
    # 连接到数据库
    if not collector.connect_db():
        print("数据库连接失败，请检查数据库配置和运行状态")
        return
    
    try:
        # 测试API连接
        print("\n1. 测试TMDB API连接...")
        if not collector.test_api_connection():
            print("API连接测试失败，请检查API密钥和网络连接")
            return
        
        # 收集测试数据
        print("\n2. 收集测试数据...")
        success = collector.collect_test_data(test_count=10)
        
        if success:
            print("\n" + "=" * 60)
            print("测试数据收集成功!")
            print("已保存10部高质量电影到数据库")
            print("=" * 60)
            
            # 验证数据
            print("\n3. 验证数据库数据...")
            collector.cursor.execute("SELECT COUNT(*) FROM movies;")
            count = collector.cursor.fetchone()[0]
            print(f"数据库中现有电影总数: {count}")
            
            collector.cursor.execute("""
                SELECT title, release_date, vote_average 
                FROM movies 
                ORDER BY id DESC 
                LIMIT 5;
            """)
            recent_movies = collector.cursor.fetchall()
            print("\n最近添加的5部电影:")
            for movie in recent_movies:
                print(f"  - {movie[0]} ({movie[1]}) - 评分: {movie[2]}")
            
        else:
            print("\n测试数据收集失败，请检查日志")
            
    except Exception as e:
        print(f"程序执行过程中出错: {e}")
        
    finally:
        # 断开数据库连接
        collector.disconnect_db()
        print("\n程序执行完成")

if __name__ == "__main__":
    main()