#!/usr/bin/env python3
"""
数据库设置脚本
创建PostgreSQL数据库和用户，准备数据库环境
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """数据库设置类"""
    
    def __init__(self):
        self.db_name = "movie_recommendation"
        self.db_user = "postgres"
        self.db_password = "postgres"
        self.db_host = "localhost"
        self.db_port = 5432
    
    def check_postgresql_installed(self) -> bool:
        """检查PostgreSQL是否安装"""
        try:
            logger.info("检查PostgreSQL是否安装...")
            
            # 尝试连接PostgreSQL
            import psycopg2
            try:
                conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password
                )
                conn.close()
                logger.info("PostgreSQL连接成功")
                return True
            except psycopg2.OperationalError as e:
                logger.warning(f"PostgreSQL连接失败: {e}")
                return False
                
        except ImportError:
            logger.error("psycopg2未安装，请先安装: pip install psycopg2-binary")
            return False
    
    def create_database(self) -> bool:
        """创建数据库"""
        try:
            logger.info(f"创建数据库: {self.db_name}")
            
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # 连接到默认数据库
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # 检查数据库是否已存在
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.db_name}'")
            exists = cursor.fetchone()
            
            if exists:
                logger.info(f"数据库 {self.db_name} 已存在")
            else:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE {self.db_name}")
                logger.info(f"数据库 {self.db_name} 创建成功")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            logger.info("测试数据库连接...")
            
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            
            # 执行简单查询
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            
            logger.info(f"PostgreSQL版本: {version}")
            logger.info(f"当前数据库: {db_name}")
            
            cursor.close()
            conn.close()
            
            logger.info("数据库连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def install_requirements(self) -> bool:
        """安装Python依赖"""
        try:
            logger.info("安装Python依赖...")
            
            requirements_file = Path(__file__).parent.parent / "requirements.txt"
            if not requirements_file.exists():
                logger.error(f"requirements.txt文件不存在: {requirements_file}")
                return False
            
            # 安装依赖
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Python依赖安装成功")
                return True
            else:
                logger.error(f"Python依赖安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"安装Python依赖失败: {e}")
            return False
    
    def setup(self) -> bool:
        """执行完整的数据库设置"""
        print("=" * 60)
        print("数据库设置工具")
        print("=" * 60)
        
        steps = [
            ("检查PostgreSQL安装", self.check_postgresql_installed),
            ("安装Python依赖", self.install_requirements),
            ("创建数据库", self.create_database),
            ("测试数据库连接", self.test_connection)
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ {step_name}失败")
                success = False
                break
            else:
                print(f"✅ {step_name}成功")
        
        if success:
            print("\n" + "=" * 60)
            print("数据库设置完成！")
            print("=" * 60)
            print("\n下一步:")
            print("1. 下载TMDB数据集:")
            print("   python backend/scripts/download_tmdb_data.py")
            print("\n2. 导入数据到数据库:")
            print("   python backend/scripts/import_tmdb_to_db.py")
            print("\n3. 启动后端服务器:")
            print("   cd backend && python -m uvicorn app.main:app --reload")
        else:
            print("\n" + "=" * 60)
            print("数据库设置失败")
            print("=" * 60)
            print("\n请检查:")
            print("1. PostgreSQL是否安装并运行")
            print("2. 数据库配置是否正确")
            print("3. Python依赖是否安装")
        
        return success

def main():
    """主函数"""
    setup = DatabaseSetup()
    setup.setup()

if __name__ == "__main__":
    main()