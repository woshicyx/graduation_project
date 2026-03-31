#!/usr/bin/env python3
"""
API测试脚本
测试数据导入和API访问功能
"""

import asyncio
import sys
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.db import SessionLocal
from backend.app.models_tmdb import Base, Movie
from sqlalchemy import select

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APITester:
    """API测试器"""
    
    def __init__(self):
        self.client = TestClient(app)
    
    def test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        try:
            logger.info("测试健康检查端点...")
            response = self.client.get("/health")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"健康检查响应: {data}")
                return True
            else:
                logger.error(f"健康检查失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"健康检查测试失败: {e}")
            return False
    
    def test_movies_endpoint(self) -> bool:
        """测试电影端点"""
        try:
            logger.info("测试电影列表端点...")
            
            # 测试获取电影列表
            response = self.client.get("/api/movies")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"电影列表响应: 共 {data['total']} 部电影")
                logger.info(f"当前页: {len(data['items'])} 部电影")
                
                if data['total'] > 0:
                    logger.info("电影列表测试成功")
                    return True
                else:
                    logger.warning("数据库中没有电影数据")
                    return False
            else:
                logger.error(f"电影列表请求失败: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"电影列表测试失败: {e}")
            return False
    
    def test_top_rated_endpoint(self) -> bool:
        """测试评分最高电影端点"""
        try:
            logger.info("测试评分最高电影端点...")
            
            response = self.client.get("/api/movies/top-rated?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"评分最高电影: 共 {len(data['items'])} 部")
                
                if data['items']:
                    for i, movie in enumerate(data['items'][:3], 1):
                        logger.info(f"  {i}. {movie['title']} - 评分: {movie['vote_average']}")
                    return True
                else:
                    logger.warning("没有找到评分最高的电影")
                    return False
            else:
                logger.error(f"评分最高电影请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"评分最高电影测试失败: {e}")
            return False
    
    def test_top_box_office_endpoint(self) -> bool:
        """测试票房最高电影端点"""
        try:
            logger.info("测试票房最高电影端点...")
            
            response = self.client.get("/api/movies/top-box-office?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"票房最高电影: 共 {len(data['items'])} 部")
                
                if data['items']:
                    for i, movie in enumerate(data['items'][:3], 1):
                        revenue = movie.get('revenue', 0)
                        revenue_str = f"${revenue:,}" if revenue else "未知"
                        logger.info(f"  {i}. {movie['title']} - 票房: {revenue_str}")
                    return True
                else:
                    logger.warning("没有找到票房最高的电影")
                    return False
            else:
                logger.error(f"票房最高电影请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"票房最高电影测试失败: {e}")
            return False
    
    def test_movie_stats_endpoint(self) -> bool:
        """测试电影统计端点"""
        try:
            logger.info("测试电影统计端点...")
            
            response = self.client.get("/api/movies/stats/summary")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"电影统计信息:")
                logger.info(f"  - 总电影数: {data['total_movies']}")
                logger.info(f"  - 有预算的电影: {data['movies_with_budget']}")
                logger.info(f"  - 有票房的电影: {data['movies_with_revenue']}")
                logger.info(f"  - 有评分的电影: {data['movies_with_rating']}")
                logger.info(f"  - 平均评分: {data['avg_rating']:.2f}")
                logger.info(f"  - 平均票房: ${data['avg_revenue']:,.0f}")
                return True
            else:
                logger.error(f"电影统计请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"电影统计测试失败: {e}")
            return False
    
    def test_random_movie_endpoint(self) -> bool:
        """测试随机电影端点"""
        try:
            logger.info("测试随机电影端点...")
            
            response = self.client.get("/api/movies/random")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"随机电影: {data['title']}")
                logger.info(f"  - 评分: {data['vote_average']}")
                logger.info(f"  - 类型: {', '.join(data['genres'])}")
                logger.info(f"  - 导演: {data['director']}")
                return True
            elif response.status_code == 404:
                logger.warning("随机电影端点返回404，可能数据库为空")
                return False
            else:
                logger.error(f"随机电影请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"随机电影测试失败: {e}")
            return False
    
    def test_search_functionality(self) -> bool:
        """测试搜索功能"""
        try:
            logger.info("测试搜索功能...")
            
            # 测试关键字搜索
            response = self.client.get("/api/movies?q=star&page_size=5")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"搜索 'star' 结果: {data['total']} 部电影")
                
                if data['items']:
                    for i, movie in enumerate(data['items'], 1):
                        logger.info(f"  {i}. {movie['title']}")
                    return True
                else:
                    logger.warning("搜索没有返回结果")
                    return False
            else:
                logger.error(f"搜索请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"搜索功能测试失败: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("=" * 60)
        print("API 测试工具")
        print("=" * 60)
        
        tests = [
            ("健康检查", self.test_health_endpoint),
            ("电影列表", self.test_movies_endpoint),
            ("评分最高电影", self.test_top_rated_endpoint),
            ("票房最高电影", self.test_top_box_office_endpoint),
            ("电影统计", self.test_movie_stats_endpoint),
            ("随机电影", self.test_random_movie_endpoint),
            ("搜索功能", self.test_search_functionality),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n测试: {test_name}")
            try:
                success = test_func()
                status = "✅ 通过" if success else "❌ 失败"
                print(f"结果: {status}")
                results.append(success)
            except Exception as e:
                print(f"结果: ❌ 异常: {e}")
                results.append(False)
        
        # 统计结果
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 60)
        print(f"测试完成: {passed}/{total} 通过")
        print("=" * 60)
        
        if passed == total:
            print("\n🎉 所有测试通过！")
            print("\n下一步:")
            print("1. 启动后端服务器:")
            print("   cd backend && python -m uvicorn app.main:app --reload")
            print("\n2. 访问API文档:")
            print("   http://localhost:8000/docs")
            print("\n3. 启动前端应用:")
            print("   cd frontend && npm run dev")
        else:
            print("\n⚠️  部分测试失败")
            print("\n请检查:")
            print("1. 数据库是否已设置并包含数据")
            print("2. 后端依赖是否已安装")
            print("3. 数据库连接配置是否正确")
        
        return passed == total

async def check_database():
    """检查数据库状态"""
    try:
        logger.info("检查数据库状态...")
        
        async with SessionLocal() as session:
            # 检查电影表
            result = await session.execute(select(Movie))
            movies = result.scalars().all()
            
            logger.info(f"数据库中的电影数量: {len(movies)}")
            
            if movies:
                # 显示前3部电影
                for i, movie in enumerate(movies[:3], 1):
                    logger.info(f"  {i}. {movie.title} (ID: {movie.id})")
                
                # 统计信息
                with_budget = sum(1 for m in movies if m.budget and m.budget > 0)
                with_revenue = sum(1 for m in movies if m.revenue and m.revenue > 0)
                with_rating = sum(1 for m in movies if m.vote_average and m.vote_average > 0)
                
                logger.info(f"有预算的电影: {with_budget}")
                logger.info(f"有票房的电影: {with_revenue}")
                logger.info(f"有评分的电影: {with_rating}")
                
                return True
            else:
                logger.warning("数据库中没有电影数据")
                return False
                
    except Exception as e:
        logger.error(f"数据库检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("智能电影推荐平台 - API测试工具")
    print("=" * 60)
    
    # 检查数据库
    print("\n1. 检查数据库状态...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        db_ok = loop.run_until_complete(check_database())
        loop.close()
        
        if not db_ok:
            print("❌ 数据库检查失败")
            print("\n请先运行数据导入脚本:")
            print("  python backend/scripts/setup_database.py")
            print("  python backend/scripts/download_tmdb_data.py")
            print("  python backend/scripts/import_tmdb_to_db.py")
            return False
        else:
            print("✅ 数据库检查通过")
    except Exception as e:
        print(f"❌ 数据库检查异常: {e}")
        return False
    
    # 运行API测试
    print("\n2. 运行API测试...")
    tester = APITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)