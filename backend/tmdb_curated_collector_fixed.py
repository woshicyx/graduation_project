#!/usr/bin/env python3
"""
TMDB精选电影数据收集器（优化版）
用于毕设RAG推荐系统的精选电影数据集（约10,000部高质量电影）
使用Discover接口按热度/评分人数排序，获取高质量电影数据
优化版本：修复数据库字段映射，支持批量收集
"""

import os
import sys
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple, Set
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
    """TMDB API客户端（优化版）"""
    
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
        
        # 请求统计
        self.stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'last_request_time': None
        }
        
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
        """发送API请求（带重试机制）"""
        self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.debug(f"请求URL: {url}, 参数: {params}")
                response = self.session.get(url, params=params, timeout=30)
                self.request_count += 1
                self.stats['total_requests'] += 1
                self.stats['last_request_time'] = datetime.now()
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 速率限制，等待后重试
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"API速率限制，等待 {retry_after} 秒后重试")
                    time.sleep(retry_after)
                    continue
                elif response.status_code >= 500:
                    # 服务器错误，等待后重试
                    wait_time = (attempt + 1) * 10  # 指数退避
                    logger.warning(f"服务器错误 {response.status_code}，等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API请求失败: {response.status_code} - {response.text}")
                    self.stats['failed_requests'] += 1
                    return None
                    
            except Exception as e:
                logger.error(f"API请求异常 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    time.sleep(wait_time)
                else:
                    self.stats['failed_requests'] += 1
                    return None
        
        return None
    
    def discover_movies(self, 
                       sort_by: str = "popularity.desc",
                       language: str = "zh-CN",
                       page: int = 1,
                       vote_count_gte: int = 100,
                       vote_average_gte: float = 6.0,
                       with_original_language: str = "en",
                       year: Optional[int] = None) -> Optional[Dict]:
        """
        使用Discover接口发现电影
        
        Args:
            sort_by: 排序方式 (popularity.desc, vote_count.desc, vote_average.desc)
            language: 语言
            page: 页码
            vote_count_gte: 最小投票数
            vote_average_gte: 最小评分
            with_original_language: 原始语言
            year: 年份筛选
        
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
        
        if year:
            params['primary_release_year'] = year
        
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
    """精选电影收集器（优化版）"""
    
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
            'total_processed': 0,
            'movies_by_year': {},
            'movies_by_genre': {},
            'start_time': datetime.now(),
            'collected_ids': set()
        }
    
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
    
    def _extract_json_list(self, data_list: List[Dict], key: str = 'name') -> str:
        """提取JSON列表"""
        try:
            if not data_list:
                return '[]'
            
            items = [item.get(key, '') for item in data_list if item.get(key)]
            return json.dumps(items)
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
            
            # 准备所有25个字段的数据（匹配现有表结构）
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
                self._extract_json_list(movie_data.get('genres', [])), # genres
                self._extract_json_list(movie_data.get('keywords', {}).get('keywords', [])), # keywords
                self._extract_json_list(movie_data.get('production_companies', [])), # production_companies
                self._extract_json_list(movie_data.get('production_countries', []), 'iso_3166_1'), # production_countries
                self._extract_json_list(movie_data.get('spoken_languages', []), 'iso_639_1'), # spoken_languages
                self._extract_director(credits),                     # director
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
            
            # 更新统计
            self.stats['total_collected'] += 1
            self.stats['collected_ids'].add(movie_id)
            
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
    
    def collect_by_popularity(self, target_count: int = 10000, max_pages: int = 500) -> bool:
        """
        按热度收集电影数据（主要策略）
        
        Args:
            target_count: 目标电影数量
            max_pages: 最大页数（每页20部电影）
        
        Returns:
            是否成功
        """
        logger.info(f"开始按热度收集电影数据，目标: {target_count} 部")
        
        try:
            # 策略：按年份分段收集，避免重复
            years = list(range(2026, 1990, -1))  # 从最新到最旧
            
            for year in years:
                if len(self.stats['collected_ids']) >= target_count:
                    break
                
                logger.info(f"收集 {year} 年的电影...")
                
                # 收集该年份的电影
                if not self._collect_by_year(year, target_count, max_pages_per_year=20):
                    logger.warning(f"收集 {year} 年电影时出现问题")
            
            # 如果还不够，继续收集其他年份
            if len(self.stats['collected_ids']) < target_count:
                logger.info("补充收集其他高质量电影...")
                self._collect_remaining(target_count, max_pages)
            
            return True
            
        except Exception as e:
            logger.error(f"收集电影数据过程中出错: {e}")
            return False
    
    def _collect_by_year(self, year: int, target_count: int, max_pages_per_year: int = 20) -> bool:
        """按年份收集电影"""
        try:
            for page in range(1, max_pages_per_year + 1):
                if len(self.stats['collected_ids']) >= target_count:
                    break
                
                logger.debug(f"获取 {year} 年第 {page} 页...")
                discover_data = self.api_client.discover_movies(
                    sort_by="popularity.desc",
                    language="zh-CN",
                    page=page,
                    vote_count_gte=100,
                    vote_average_gte=6.0,
                    with_original_language="en",
                    year=year
                )
                
                if not discover_data or 'results' not in discover_data:
                    logger.warning(f"{year} 年第 {page} 页无数据或请求失败")
                    time.sleep(1)
                    continue
                
                movies = discover_data['results']
                if not movies:
                    logger.info(f"{year} 年无更多电影数据")
                    break
                
                logger.info(f"{year} 年第 {page} 页获取到 {len(movies)} 部电影")
                
                # 处理本页电影
                for movie_summary in movies:
                    if len(self.stats['collected_ids']) >= target_count:
                        break
                    
                    movie_id = movie_summary.get('id')
                    if not movie_id or movie_id in self.stats['collected_ids']:
                        continue
                    
                    # 获取电影详情
                    movie_details = self.api_client.get_movie_details(movie_id, language="zh-CN")
                    
                    if not movie_details:
                        logger.warning(f"无法获取电影详情 ID: {movie_id}")
                        time.sleep(0.5)
                        continue
                    
                    # 保存电影数据
                    if self.save_movie(movie_details):
                        logger.debug(f"成功保存电影: {movie_details.get('title')} (ID: {movie_id})")
                    
                    # 控制请求速率
                    time.sleep(0.3)
                
                # 显示进度
                progress = len(self.stats['collected_ids']) / target_count * 100
                logger.info(f"进度: {len(self.stats['collected_ids'])}/{target_count} ({progress:.1f}%)")
                
                # 控制翻页速率
                if page % 5 == 0:
                    time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"按年份收集电影失败 (年份: {year}): {e}")
            return False
    
    def _collect_remaining(self, target_count: int, max_pages: int):
        """补充收集剩余电影"""
        try:
            # 使用Discover接口（不限制年份）
            for page in range(1, min(max_pages, 100) + 1):
                if len(self.stats['collected_ids']) >= target_count:
                    break
                
                logger.info(f"补充收集第 {page} 页...")
                discover_data = self.api_client.discover_movies(
                    sort_by="vote_count.desc",  # 按投票数排序，获取高人气电影
                    language="zh-CN",
                    page=page,
                    vote_count_gte=500,  # 更高的投票数要求
                    vote_average_gte=7.0,  # 更高的评分要求
                    with_original_language="en"
                )
                
                if not discover_data or 'results' not in discover_data:
                    logger.warning(f"补充收集第 {page} 页无数据")
                    time.sleep(1)
                    continue
                
                movies = discover_data['results']
                if not movies:
                    break
                
                logger.info(f"补充收集第 {page} 页获取到 {len(movies)} 部电影")
                
                for movie_summary in movies:
                    if len(self.stats['collected_ids']) >= target_count:
                        break
                    
                    movie_id = movie_summary.get('id')
                    if not movie_id or movie_id in self.stats['collected_ids']:
                        continue
                    
                    # 获取电影详情
                    movie_details = self.api_client.get_movie_details(movie_id, language="zh-CN")
                    
                    if movie_details and self.save_movie(movie_details):
                        logger.debug(f"补充保存电影: {movie_details.get('title')}")
                    
                    time.sleep(0.3)
                
                # 显示进度
                progress = len(self.stats['collected_ids']) / target_count * 100
                logger.info(f"补充收集进度: {len(self.stats['collected_ids'])}/{target_count} ({progress:.1f}%)")
                
                if page % 10 == 0:
                    time.sleep(3)
                    
        except Exception as e:
            logger.error(f"补充收集过程中出错: {e}")
    
    def collect_daily_batch(self, daily_target: int = 400) -> bool:
        """
        收集每日批次数据（考虑API限制）
        
        Args:
            daily_target: 每日目标电影数量（考虑API限制）
        
        Returns:
            是否成功
        """
        logger.info(f"收集每日批次数据，目标: {daily_target} 部")
        
        try:
            # 获取当前数据库中的电影数量
            self.cursor.execute("SELECT COUNT(*) FROM movies;")
            current_count = self.cursor.fetchone()[0]
            
            logger.info(f"当前数据库中有 {current_count} 部电影")
            
            # 设置每日目标
            target_increase = daily_target
            total_target = current_count + target_increase
            
            # 收集数据
            success = self.collect_by_popularity(target_count=total_target, max_pages=50)
            
            if success:
                # 获取最终数量
                self.cursor.execute("SELECT COUNT(*) FROM movies;")
                final_count = self.cursor.fetchone()[0]
                added_count = final_count - current_count
                
                logger.info(f"今日新增 {added_count} 部电影，总计 {final_count} 部")
                
                # 打印API使用统计
                self._print_api_stats()
            
            return success
            
        except Exception as e:
            logger.error(f"收集每日批次数据过程中出错: {e}")
            return False
    
    def _print_api_stats(self):
        """打印API使用统计"""
        logger.info("=" * 60)
        logger.info("API使用统计:")
        logger.info(f"  总请求数: {self.api_client.stats['total_requests']}")
        logger.info(f"  失败请求数: {self.api_client.stats['failed_requests']}")
        logger.info(f"  今日剩余请求数: {490 - self.api_client.request_count}")
        logger.info("=" * 60)
    
    def _print_statistics(self):
        """打印收集统计信息"""
        logger.info("=" * 60)
        logger.info("电影数据收集统计:")
        logger.info(f"  总收集电影数: {self.stats['total_collected']}")
        logger.info(f"  总耗时: {datetime.now() - self.stats['start_time']}")
        
        # 年份分布
        if self.stats['movies_by_year']:
            logger.info("年份分布 (前10):")
            for year, count in sorted(self.stats['movies_by_year'].items(), key=lambda x: x[0], reverse=True)[:10]:
                logger.info(f"    {year}: {count} 部")
        
        # 类型分布
        if self.stats['movies_by_genre']:
            logger.info("类型分布 (前10):")
            for genre, count in sorted(self.stats['movies_by_genre'].items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"    {genre}: {count} 部")
        
        logger.info("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("TMDB精选电影数据收集器（优化版）")
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
        # 获取当前数据库中的电影数量
        collector.cursor.execute("SELECT COUNT(*) FROM movies;")
        current_count = collector.cursor.fetchone()[0]
        print(f"当前数据库中有 {current_count} 部电影")
        
        # 询问收集模式
        print("\n请选择收集模式:")
        print("1. 收集每日批次（约400部，考虑API限制）")
        print("2. 收集到目标数量（例如10,000部）")
        print("3. 测试模式（收集10部）")
        
        choice = input("\n请选择 (1/2/3, 默认1): ").strip()
        
        if choice == "2":
            target_str = input("请输入目标电影总数（例如10000）: ").strip()
            try:
                target_count = int(target_str)
                if target_count <= current_count:
                    print(f"目标数量 {target_count} 小于等于当前数量 {current_count}，无需收集")
                    return
                
                print(f"\n开始收集电影数据，目标: {target_count} 部")
                success = collector.collect_by_popularity(target_count=target_count, max_pages=200)
                
            except ValueError:
                print("输入无效，使用默认目标: 10000")
                target_count = 10000
                success = collector.collect_by_popularity(target_count=target_count, max_pages=200)
                
        elif choice == "3":
            print("\n测试模式：收集10部电影")
            # 简单测试收集
            test_collector = TMDBTestCollector(API_KEY)
            if test_collector.connect_db():
                test_collector.collect_test_data(test_count=10)
                test_collector.disconnect_db()
            success = True
            
        else:  # 默认选项1
            print("\n每日批次模式：收集约400部电影")
            success = collector.collect_daily_batch(daily_target=400)
        
        if success:
            # 打印最终统计
            collector._print_statistics()
            collector._print_api_stats()
            
            # 获取最终数量
            collector.cursor.execute("SELECT COUNT(*) FROM movies;")
            final_count = collector.cursor.fetchone()[0]
            added_count = final_count - current_count
            
            print("\n" + "=" * 60)
            print(f"数据收集完成!")
            print(f"  新增电影: {added_count} 部")
            print(f"  电影总数: {final_count} 部")
            print("=" * 60)
            
            # 建议下一步
            print("\n建议下一步操作:")
            print("1. 运行数据验证脚本: python check_db_direct.py")
            print("2. 如果需要继续收集，明天再次运行此脚本")
            print("3. 启动后端API服务: cd backend && python -m uvicorn app.main:app --reload")
            print("4. 启动前端开发服务器: cd frontend && npm run dev")
        else:
            print("\n数据收集过程中出现问题，请检查日志")
            
    except KeyboardInterrupt:
        print("\n\n用户中断，正在保存已收集的数据...")
    except Exception as e:
        print(f"\n程序执行过程中出错: {e}")
        
    finally:
        # 断开数据库连接
        collector.disconnect_db()
        print("\n程序执行完成")

# 需要从测试收集器导入TMDBTestCollector类
class TMDBTestCollector:
    """简单的测试收集器（用于测试模式）"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'movie_recommendation',
            'user': 'postgres',
            'password': '356921'
        }
        self.conn = None
        self.cursor = None
    
    def connect_db(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            return True
        except:
            return False
    
    def disconnect_db(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def collect_test_data(self, test_count=10):
        import requests
        import time
        
        session = requests.Session()
        params = {'api_key': self.api_key, 'language': 'zh-CN', 'page': 1}
        
        response = session.get("https://api.themoviedb.org/3/movie/popular", params=params)
        if response.status_code != 200:
            return False
        
        movies = response.json().get('results', [])
        collected = 0
        
        for movie in movies:
            if collected >= test_count:
                break
            
            movie_id = movie.get('id')
            if not movie_id:
                continue
            
            # 简化的保存逻辑
            try:
                self.cursor.execute("""
                    INSERT INTO movies (id, title, overview, release_date, vote_average)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    movie_id,
                    movie.get('title', ''),
                    movie.get('overview', ''),
                    movie.get('release_date'),
                    movie.get('vote_average', 0)
                ))
                self.conn.commit()
                collected += 1
                print(f"测试保存电影: {movie.get('title')}")
            except:
                self.conn.rollback()
            
            time.sleep(0.5)
        
        return True

if __name__ == "__main__":
    main()