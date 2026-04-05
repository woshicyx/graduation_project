#!/usr/bin/env python3
"""
TMDB批量电影数据收集器（优化版）
根据最新TMDB API策略：无硬性每日限制，动态速率限制（建议<50请求/秒）
一次性收集约10,000部高质量电影，适合毕设RAG系统
"""

import os
import sys
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Set
from datetime import datetime
import psycopg2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TMDBBatchCollector:
    """TMDB批量电影收集器（优化速率限制）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # API速率限制：每秒不超过30个请求（安全范围内）
        self.requests_per_second = 30
        self.last_request_time = None
        self.request_count = 0
        
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
        
        # 收集统计
        self.stats = {
            'total_collected': 0,
            'total_requests': 0,
            'failed_requests': 0,
            'movies_by_year': {},
            'movies_by_genre': {},
            'start_time': datetime.now(),
            'collected_ids': set()
        }
    
    def _rate_limit(self):
        """智能速率限制：确保每秒不超过指定请求数"""
        now = time.time()
        
        if self.last_request_time is not None:
            elapsed = now - self.last_request_time
            min_interval = 1.0 / self.requests_per_second
            
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送API请求（带速率限制和重试机制）"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.stats['total_requests'] += 1
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 速率限制，等待后重试
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"API速率限制，等待 {retry_after} 秒后重试")
                    time.sleep(retry_after)
                    continue
                elif response.status_code >= 500:
                    # 服务器错误，等待后重试
                    wait_time = (attempt + 1) * 3  # 指数退避
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
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    self.stats['failed_requests'] += 1
                    return None
        
        return None
    
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
    
    def get_current_movie_count(self) -> int:
        """获取当前数据库中的电影数量"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM movies;")
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"获取电影数量失败: {e}")
            return 0
    
    def discover_movies(self, 
                       sort_by: str = "popularity.desc",
                       language: str = "zh-CN",
                       page: int = 1,
                       vote_count_gte: int = 100,
                       vote_average_gte: float = 6.0,
                       with_original_language: str = "en",
                       year: Optional[int] = None) -> Optional[Dict]:
        """使用Discover接口发现电影"""
        params = {
            'sort_by': sort_by,
            'language': language,
            'page': page,
            'vote_count.gte': vote_count_gte,
            'vote_average.gte': vote_average_gte,
            'with_original_language': with_original_language,
            'include_adult': False,
            'include_video': False,
        }
        
        if year:
            params['primary_release_year'] = year
        
        return self._make_request("discover/movie", params)
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """获取电影详情"""
        params = {
            'language': 'zh-CN',
            'append_to_response': 'credits,keywords'
        }
        
        return self._make_request(f"movie/{movie_id}", params)
    
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
    
    def save_movie(self, movie_data: Dict) -> bool:
        """保存电影数据到数据库"""
        try:
            movie_id = movie_data.get('id')
            if not movie_id:
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
            
            # 显示进度
            if self.stats['total_collected'] % 100 == 0:
                elapsed = datetime.now() - self.stats['start_time']
                rate = self.stats['total_collected'] / elapsed.total_seconds() * 3600 if elapsed.total_seconds() > 0 else 0
                logger.info(f"已收集 {self.stats['total_collected']} 部电影 | 速率: {rate:.1f} 部/小时")
            
            return True
            
        except Exception as e:
            logger.error(f"保存电影数据失败 (ID: {movie_id}): {e}")
            self.conn.rollback()
            return False
    
    def collect_batch(self, target_total: int = 10000) -> bool:
        """
        批量收集电影数据
        
        Args:
            target_total: 目标电影总数
        
        Returns:
            是否成功
        """
        current_count = self.get_current_movie_count()
        
        if current_count >= target_total:
            logger.info(f"当前已有 {current_count} 部电影，已达到目标 {target_total}")
            return True
        
        target_increase = target_total - current_count
        logger.info(f"开始批量收集，目标新增: {target_increase} 部电影")
        
        try:
            # 策略：按年份收集，从最新到最旧
            years = list(range(2026, 1990, -1))
            
            for year in years:
                if len(self.stats['collected_ids']) >= target_increase:
                    break
                
                logger.info(f"收集 {year} 年的电影...")
                
                # 收集该年份的电影
                self._collect_year_batch(year, target_increase)
            
            # 如果还不够，使用其他策略
            if len(self.stats['collected_ids']) < target_increase:
                logger.info("补充收集高评分电影...")
                self._collect_high_rated(target_increase)
            
            return True
            
        except Exception as e:
            logger.error(f"批量收集过程中出错: {e}")
            return False
    
    def _collect_year_batch(self, year: int, target_increase: int, max_pages: int = 50):
        """按年份收集电影批次"""
        try:
            for page in range(1, max_pages + 1):
                if len(self.stats['collected_ids']) >= target_increase:
                    break
                
                logger.debug(f"获取 {year} 年第 {page} 页...")
                discover_data = self.discover_movies(
                    sort_by="popularity.desc",
                    language="zh-CN",
                    page=page,
                    vote_count_gte=100,
                    vote_average_gte=6.0,
                    with_original_language="en",
                    year=year
                )
                
                if not discover_data or 'results' not in discover_data:
                    logger.warning(f"{year} 年第 {page} 页无数据")
                    break
                
                movies = discover_data['results']
                if not movies:
                    logger.info(f"{year} 年无更多电影数据")
                    break
                
                logger.info(f"{year} 年第 {page} 页获取到 {len(movies)} 部电影")
                
                # 处理本页电影
                for movie_summary in movies:
                    if len(self.stats['collected_ids']) >= target_increase:
                        break
                    
                    movie_id = movie_summary.get('id')
                    if not movie_id or movie_id in self.stats['collected_ids']:
                        continue
                    
                    # 获取电影详情
                    movie_details = self.get_movie_details(movie_id)
                    
                    if not movie_details:
                        logger.warning(f"无法获取电影详情 ID: {movie_id}")
                        continue
                    
                    # 保存电影数据
                    if self.save_movie(movie_details):
                        logger.debug(f"保存电影: {movie_details.get('title')}")
                    
                    # 小延迟，避免过快
                    time.sleep(0.05)
                
                # 显示进度
                progress = len(self.stats['collected_ids']) / target_increase * 100
                elapsed = datetime.now() - self.stats['start_time']
                remaining = target_increase - len(self.stats['collected_ids'])
                
                if remaining > 0 and progress > 0:
                    estimated_time = elapsed.total_seconds() / progress * (100 - progress) / 60
                    logger.info(f"进度: {len(self.stats['collected_ids'])}/{target_increase} ({progress:.1f}%) | 预计剩余: {estimated_time:.1f} 分钟")
                
                # 页间延迟
                if page % 10 == 0:
                    time.sleep(2)
            
        except Exception as e:
            logger.error(f"按年份收集电影失败 (年份: {year}): {e}")
    
    def _collect_high_rated(self, target_increase: int):
        """补充收集高评分电影"""
        try:
            # 按评分排序获取高质量电影
            for page in range(1, 51):  # 最多50页
                if len(self.stats['collected_ids']) >= target_increase:
                    break
                
                logger.info(f"获取高评分电影第 {page} 页...")
                discover_data = self.discover_movies(
                    sort_by="vote_average.desc",
                    language="zh-CN",
                    page=page,
                    vote_count_gte=500,  # 高投票数
                    vote_average_gte=7.5,  # 高评分
                    with_original_language="en"
                )
                
                if not discover_data or 'results' not in discover_data:
                    break
                
                movies = discover_data['results']
                if not movies:
                    break
                
                logger.info(f"高评分电影第 {page} 页获取到 {len(movies)} 部电影")
                
                for movie_summary in movies:
                    if len(self.stats['collected_ids']) >= target_increase:
                        break
                    
                    movie_id = movie_summary.get('id')
                    if not movie_id or movie_id in self.stats['collected_ids']:
                        continue
                    
                    # 获取电影详情
                    movie_details = self.get_movie_details(movie_id)
                    
                    if movie_details and self.save_movie(movie_details):
                        logger.debug(f"补充保存高评分电影: {movie_details.get('title')}")
                    
                    time.sleep(0.05)
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"补充收集高评分电影失败: {e}")
    
    def print_statistics(self):
        """打印统计信息"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.total_seconds() / 3600
        
        print("\n" + "=" * 60)
        print("数据收集统计:")
        print(f"  总收集电影数: {self.stats['total_collected']}")
        print(f"  总API请求数: {self.stats['total_requests']}")
        print(f"  失败请求数: {self.stats['failed_requests']}")
        print(f"  总耗时: {elapsed}")
        print(f"  平均速率: {self.stats['total_collected']/hours if hours > 0 else 0:.1f} 部/小时")
        
        # 年份分布
        if self.stats['movies_by_year']:
            print("\n年份分布 (前10):")
            for year, count in sorted(self.stats['movies_by_year'].items(), key=lambda x: x[0], reverse=True)[:10]:
                print(f"    {year}: {count} 部")
        
        # 类型分布
        if self.stats['movies_by_genre']:
            print("\n类型分布 (前10):")
            for genre, count in sorted(self.stats['movies_by_genre'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"    {genre}: {count} 部")
        
        print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("TMDB批量电影数据收集器（优化版）")
    print("一次性收集约10,000部高质量电影")
    print("速率限制：每秒不超过30个请求")
    print("=" * 60)
    
    # API密钥
    API_KEY = "b569b88efd591d1c673734fca9242588"
    print(f"使用的API密钥: {API_KEY[:8]}...")
    
    # 创建收集器
    collector = TMDBBatchCollector(api_key=API_KEY)
    
    # 连接到数据库
    if not collector.connect_db():
        print("数据库连接失败，请检查数据库配置和运行状态")
        return
    
    try:
        # 获取当前电影数量
        current_count = collector.get_current_movie_count()
        print(f"当前数据库中有 {current_count} 部电影")
        
        # 设置目标总数
        target_total = 10000
        
        if current_count >= target_total:
            print(f"已达到目标电影数量 {target_total}")
        else:
            print(f"\n开始批量收集电影数据...")
            print(f"目标总数: {target_total}")
            print(f"需要新增: {target_total - current_count} 部电影")
            print(f"预计时间: 约 {((target_total - current_count) / 300 * 1.5):.1f} 小时")
            print("\n提示: 按 Ctrl+C 可中断收集过程")
            
            # 开始收集
            success = collector.collect_batch(target_total=target_total)
            
            if success:
                # 获取最终数量
                final_count = collector.get_current_movie_count()
                added_count = final_count - current_count
                
                print("\n" + "=" * 60)
                print("批量数据收集完成!")
                print(f"  新增电影: {added_count} 部")
                print(f"  电影总数: {final_count} 部")
                print("=" * 60)
                
                # 打印详细统计
                collector.print_statistics()
                
                # 建议下一步
                print("\n建议下一步操作:")
                print("1. 运行数据验证: python check_db_direct.py")
                print("2. 如果需要继续收集，可调整目标数量重新运行")
                print("3. 启动后端服务: cd backend && python -m uvicorn app.main:app --reload")
                print("4. 启动前端服务: cd frontend && npm run dev")
            else:
                print("\n数据收集过程中出现问题")
                
                # 打印部分统计
                if collector.stats['total_collected'] > 0:
                    print(f"已成功收集 {collector.stats['total_collected']} 部电影")
                    collector.print_statistics()
        
    except KeyboardInterrupt:
        print("\n\n用户中断收集过程...")
        
        # 打印已收集的统计
        if collector.stats['total_collected'] > 0:
            print(f"已成功收集 {collector.stats['total_collected']} 部电影")
            collector.print_statistics()
        
    except Exception as e:
        print(f"\n程序执行过程中出错: {e}")
        
    finally:
        # 断开数据库连接
        collector.disconnect_db()
        print("\n程序执行完成")


if __name__ == "__main__":
    main()