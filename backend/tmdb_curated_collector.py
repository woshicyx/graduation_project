#!/usr/bin/env python3
"""
TMDB精选电影数据收集器
用于毕设RAG推荐系统的精选电影数据集（约10,000部高质量电影）
使用Discover接口按热度/评分人数排序，获取高质量电影数据
"""

import os
import sys
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TMDBAPIClient:
    """TMDB API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # API限制：免费账户每天500个请求
        self.daily_limit = 490  # 留10个请求余量
        self.request_count = 0
        self.last_reset = datetime.now()
        
    def _check_rate_limit(self):
        """检查并管理API速率限制"""
        now = datetime.now()
        # 如果过了午夜，重置计数器
        if now.date() > self.last_reset.date():
            self.request_count = 0
            self.last_reset = now
            logger.info(f"API请求计数器已重置，新的一天开始")
        
        if self.request_count >= self.daily_limit:
            logger.warning(f"已达到每日API限制({self.daily_limit})，等待到明天")
            # 计算到明天的时间
            tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (tomorrow - now).total_seconds()
            logger.info(f"等待 {wait_seconds:.0f} 秒直到明天")
            time.sleep(wait_seconds)
            self.request_count = 0
            self.last_reset = datetime.now()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        try:
            logger.debug(f"请求URL: {url}, 参数: {params}")
            response = self.session.get(url, params=params, timeout=30)
            self.request_count += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # 速率限制，等待后重试
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"API速率限制，等待 {retry_after} 秒")
                time.sleep(retry_after)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            return None
    
    def discover_movies(self, 
                       sort_by: str = "popularity.desc",
                       language: str = "zh-CN",
                       page: int = 1,
                       vote_count_gte: int = 100,
                       vote_average_gte: float = 6.0,
                       with_original_language: str = "en") -> Optional[Dict]:
        """
        使用Discover接口发现电影
        
        Args:
            sort_by: 排序方式 (popularity.desc, vote_count.desc, vote_average.desc)
            language: 语言
            page: 页码
            vote_count_gte: 最小投票数
            vote_average_gte: 最小评分
            with_original_language: 原始语言
        
        Returns:
            API响应数据
        """
        params = {
            'sort_by': sort_by,
            'language': language,
            'page': page,
            'vote_count.gte': vote_count_gte,
            'vote_average.gte': vote_average_gte,
            'with_original_language': with_original_language,
            'include_adult': False,  # 排除成人内容
            'include_video': False,
        }
        
        return self._make_request("discover/movie", params)
    
    def get_movie_details(self, movie_id: int, language: str = "zh-CN") -> Optional[Dict]:
        """获取电影详情（包含credits信息）"""
        params = {
            'language': language,
            'append_to_response': 'credits,keywords'  # 一次请求获取多个信息
        }
        
        return self._make_request(f"movie/{movie_id}", params)
    
    def get_popular_movies(self, page: int = 1, language: str = "zh-CN") -> Optional[Dict]:
        """获取流行电影"""
        params = {
            'language': language,
            'page': page
        }
        
        return self._make_request("movie/popular", params)
    
    def get_now_playing(self, language: str = "zh-CN") -> Optional[Dict]:
        """获取正在上映的电影"""
        params = {
            'language': language,
            'page': 1
        }
        
        return self._make_request("movie/now_playing", params)


class CuratedMovieCollector:
    """精选电影收集器"""
    
    def __init__(self, api_key: str, db_config: Dict = None):
        self.api_client = TMDBAPIClient(api_key)
        
        # 数据库配置
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'movie_recommendation',
            'user': 'postgres',
            'password': '356921'
        }
        
        self.conn = None
        self.cursor = None
        
        # 收集统计
        self.stats = {
            'total_collected': 0,
            'total_requests': 0,
            'movies_by_year': {},
            'movies_by_genre': {},
            'start_time': datetime.now()
        }
    
    def connect_db(self) -> bool:
        """连接到数据库"""
        try:
            logger.info(f"连接到数据库: {self.db_config['database']}")
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            
            # 确保表存在
            self._ensure_table_exists()
            
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
    
    def _ensure_table_exists(self):
        """确保movies表存在并包含必要字段"""
        try:
            # 检查表是否存在
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'movies'
                );
            """)
            
            if not self.cursor.fetchone()[0]:
                logger.error("movies表不存在，请先运行数据库设置脚本")
                raise Exception("movies表不存在")
            
            # 检查是否有必要字段
            self.cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'movies';
            """)
            
            columns = {row[0] for row in self.cursor.fetchall()}
            required_columns = {'id', 'title', 'overview', 'release_date', 'vote_average'}
            
            missing_columns = required_columns - columns
            if missing_columns:
                logger.error(f"movies表缺少必要字段: {missing_columns}")
                raise Exception(f"表结构不完整，缺少字段: {missing_columns}")
                
            logger.info("数据库表结构验证通过")
            
        except Exception as e:
            logger.error(f"数据库表检查失败: {e}")
            raise
    
    def _extract_director(self, credits_data: Dict) -> str:
        """从credits数据中提取导演"""
        try:
            if not credits_data or 'crew' not in credits_data:
                return ''
            
            for crew_member in credits_data['crew']:
                if crew_member.get('job') == 'Director' and 'name' in crew_member:
                    return crew_member['name']
            return ''
        except:
            return ''
    
    def _extract_genres(self, genres_data: List[Dict]) -> str:
        """提取电影类型"""
        try:
            if not genres_data:
                return '[]'
            
            genre_names = [genre.get('name', '') for genre in genres_data if genre.get('name')]
            return json.dumps(genre_names)
        except:
            return '[]'
    
    def _extract_keywords(self, keywords_data: Dict) -> str:
        """提取关键词"""
        try:
            if not keywords_data or 'keywords' not in keywords_data:
                return '[]'
            
            keywords = [kw.get('name', '') for kw in keywords_data['keywords'] if kw.get('name')]
            return json.dumps(keywords)
        except:
            return '[]'
    
    def _extract_production_companies(self, companies_data: List[Dict]) -> str:
        """提取制作公司"""
        try:
            if not companies_data:
                return '[]'
            
            companies = [comp.get('name', '') for comp in companies_data if comp.get('name')]
            return json.dumps(companies)
        except:
            return '[]'
    
    def save_movie(self, movie_data: Dict) -> bool:
        """保存电影数据到数据库"""
        try:
            # 提取基本信息
            movie_id = movie_data.get('id')
            if not movie_id:
                logger.error("电影数据缺少ID")
                return False
            
            # 提取credits信息
            credits = movie_data.get('credits', {})
            
            # 准备电影数据
            movie_record = (
                movie_id,
                movie_data.get('title', '')[:500],
                movie_data.get('overview', ''),
                movie_data.get('tagline', ''),
                movie_data.get('budget', 0),
                movie_data.get('revenue', 0),
                movie_data.get('popularity', 0.0),
                movie_data.get('release_date'),  # 可能是None
                movie_data.get('runtime', 0),
                movie_data.get('vote_average', 0.0),
                movie_data.get('vote_count', 0),
                movie_data.get('poster_path', ''),
                movie_data.get('status', ''),
                self._extract_genres(movie_data.get('genres', [])),
                self._extract_director(credits),
                movie_data.get('original_title', ''),
                movie_data.get('homepage', ''),
                movie_data.get('original_language', ''),
                self._extract_keywords(movie_data.get('keywords', {})),
                self._extract_production_companies(movie_data.get('production_companies', []))
            )
            
            # 插入或更新数据
            insert_sql = """
            INSERT INTO movies (
                id, title, overview, tagline, budget, revenue, popularity,
                release_date, runtime, vote_average, vote_count, poster_path,
                status, genres, director, original_title, homepage, original_language,
                keywords, production_companies
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                original_title = EXCLUDED.original_title,
                homepage = EXCLUDED.homepage,
                original_language = EXCLUDED.original_language,
                keywords = EXCLUDED.keywords,
                production_companies = EXCLUDED.production_companies,
                updated_at = CURRENT_TIMESTAMP
            """
            
            self.cursor.execute(insert_sql, movie_record)
            self.conn.commit()
            
            # 更新统计
            self.stats['total_collected'] += 1
            
            # 按年份统计
            if movie_data.get('release_date'):
                year = movie_data['release_date'][:4] if movie_data['release_date'] else '未知'
                self.stats['movies_by_year'][year] = self.stats['movies_by_year'].get(year, 0) + 1
            
            # 按类型统计
            for genre in movie_data.get('genres', []):
                genre_name = genre.get('name', '')
                if genre_name:
                    self.stats['movies_by_genre'][genre_name] = self.stats['movies_by_genre'].get(genre_name, 0) + 1
            
            if self.stats['total_collected'] % 100 == 0:
                logger.info(f"已收集 {self.stats['total_collected']} 部电影")
            
            return True
            
        except Exception as e:
            logger.error(f"保存电影数据失败 (ID: {movie_id}): {e}")
            self.conn.rollback()
            return False
    
    def collect_curated_movies(self, target_count: int = 10000, max_pages: int = 500) -> bool:
        """
        收集精选电影数据
        
        Args:
            target_count: 目标电影数量
            max_pages: 最大页数（每页20部电影）
        
        Returns:
            是否成功
        """
        logger.info(f"开始收集精选电影数据，目标: {target_count} 部")
        
        try:
            collected_ids = set()
            
            # 策略1：按热度发现电影（主要来源）
            logger.info("策略1：按热度发现电影...")
            for page in range(1, min(max_pages, 250) + 1):
                if len(collected_ids) >= target_count:
                    break
                
                logger.info(f"获取Discover页面 {page}...")
                discover_data = self.api_client.discover_movies(
                    sort_by="popularity.desc",
                    language="zh-CN",
                    page=page,
                    vote_count_gte=100,
                    vote_average_gte=6.0,
                    with_original_language="en"
                )
                
                if not discover_data or 'results' not in discover_data:
                    logger.warning(f"第 {page} 页无数据或请求失败")
                    time.sleep(1)  # 避免过快请求
                    continue
                
                movies = discover_data['results']
                if not movies:
                    logger.info(f"第 {page} 页无电影数据，停止")
                    break
                
                logger.info(f"第 {page} 页获取到 {len(movies)} 部电影")
                
                # 处理本页电影
                for movie_summary in movies:
                    if len(collected_ids) >= target_count:
                        break
                    
                    movie_id = movie_summary.get('id')
                    if not movie_id or movie_id in collected_ids:
                        continue
                    
                    # 获取电影详情
                    logger.debug(f"获取电影详情 ID: {movie_id}")
                    movie_details = self.api_client.get_movie_details(movie_id, language="zh-CN")
                    
                    if not movie_details:
                        logger.warning(f"无法获取电影详情 ID: {movie_id}")
                        time.sleep(0.5)
                        continue
                    
                    # 保存电影数据
                    if self.save_movie(movie_details):
                        collected_ids.add(movie_id)
                        logger.debug(f"成功保存电影: {movie_details.get('title')} (ID: {movie_id})")
                    
                    # 控制请求速率
                    time.sleep(0.2)
                
                # 显示进度
                progress = len(collected_ids) / target_count * 100
                logger.info(f"进度: {len(collected_ids)}/{target_count} ({progress:.1f}%)")
                
                # 控制翻页速率
                if page % 10 == 0:
                    time.sleep(2)
            
            # 策略2：获取流行电影（补充热门新片）
            if len(collected_ids) < target_count:
                logger.info("策略2：获取流行电影...")
                for page in range(1, 11):  # 只获取前10页流行电影
                    if len(collected_ids) >= target_count:
                        break
                    
                    logger.info(f"获取流行电影页面 {page}...")
                    popular_data = self.api_client.get_popular_movies(page=page, language="zh-CN")
                    
                    if not popular_data or 'results' not in popular_data:
                        continue
                    
                    movies = popular_data['results']
                    logger.info(f"流行电影第 {page} 页获取到 {len(movies)} 部电影")
                    
                    for movie_summary in movies:
                        if len(collected_ids) >= target_count:
                            break
                        
                        movie_id = movie_summary.get('id')
                        if not movie_id or movie_id in collected_ids:
                            continue
                        
                        # 获取电影详情
                        movie_details = self.api_client.get_movie_details(movie_id, language="zh-CN")
                        
                        if movie_details and self.save_movie(movie_details):
                            collected_ids.add(movie_id)
                        
                        time.sleep(0.2)
            
            # 策略3：获取正在上映的电影（最新电影）
            if len(collected_ids) < target_count:
                logger.info("策略3：获取正在上映的电影...")
                now_playing_data = self.api_client.get_now_playing(language="zh-CN")
                
                if now_playing_data and 'results' in now_playing_data:
                    movies = now_playing_data['results']
                    logger.info(f"正在上映的电影: {len(movies)} 部")
                    
                    for movie_summary in movies:
                        if len(collected_ids) >= target_count:
                            break
                        
                        movie_id = movie_summary.get('id')
                        if not movie_id or movie_id in collected_ids:
                            continue
                        
                        # 获取电影详情
                        movie_details = self.api_client.get_movie_details(movie_id, language="zh-CN")
                        
                        if movie_details and self.save_movie(movie_details):
                            collected_ids.add(movie_id)
                        
                        time.sleep(0.2)
            
            # 打印最终统计
            self._print_statistics(collected_ids)
            
            return True
            
        except Exception as e:
            logger.error(f"收集电影数据过程中出错: {e}")
            return False
    
    def _print_statistics(self, collected_ids: set):
        """打印收集统计信息"""
        logger.info("=" * 60)
        logger.info("电影数据收集完成!")
        logger.info(f"总收集电影数: {len(collected_ids)}")
        logger.info(f"总API请求数: {self.api_client.request_count}")
        
        # 计算花费时间
        elapsed_time = datetime.now() - self.stats['start_time']
        logger.info(f"总耗时: {elapsed_time}")
        
        # 年份分布
        if self.stats['movies_by_year']:
            logger.info("年份分布:")
            for year, count in sorted(self.stats['movies_by_year'].items(), key=lambda x: x[0], reverse=True)[:10]:
                logger.info(f"  {year}: {count} 部")
        
        # 类型分布
        if self.stats['movies_by_genre']:
            logger.info("类型分布 (前10):")
            for genre, count in sorted(self.stats['movies_by_genre'].items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"  {genre}: {count} 部")
        
        logger.info("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("TMDB精选电影数据收集器")
    print("用于毕设RAG推荐系统的精选电影数据集")
    print("=" * 60)
    
    # API密钥
    API_KEY = "b569b88efd591d1c673734fca9242588"
    
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'movie_recommendation',
        'user': 'postgres',
        'password': '356921'
    }
    
    # 创建收集器
    collector = CuratedMovieCollector(api_key=API_KEY, db_config=db_config)
    
    # 连接到数据库
    if not collector.connect_db():
        print("数据库连接失败，请检查数据库配置和运行状态")
        return
    
    try:
        # 收集电影数据
        target_count = 10000  # 目标收集10,000部电影
        success = collector.collect_curated_movies(target_count=target_count, max_pages=250)
        
        if success:
            print("\n" + "=" * 60)
            print(f"成功收集约 {collector.stats['total_collected']} 部高质量电影!")
            print("数据已保存到数据库")
            print("=" * 60)
            
            # 建议下一步
            print("\n建议下一步操作:")
            print("1. 运行数据验证脚本: python backend/scripts/test_connection.py")
            print("2. 启动后端API服务: python -m uvicorn app.main:app --reload")
            print("3. 启动前端开发服务器: cd frontend && npm run dev")
        else:
            print("\n收集过程中出现问题，请检查日志")
            
    finally:
        # 断开数据库连接
        collector.disconnect_db()


if __name__ == "__main__":
    main()