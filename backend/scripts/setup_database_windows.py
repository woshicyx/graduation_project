#!/usr/bin/env python3
"""
Windows 环境下的数据库设置脚本
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_postgresql_installation():
    """检查 PostgreSQL 是否已安装"""
    try:
        # 尝试连接 PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="356921",
            database="postgres"
        )
        conn.close()
        logger.info("✅ PostgreSQL 连接成功")
        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL 连接失败: {e}")
        logger.info("请确保:")
        logger.info("1. PostgreSQL 已安装并运行")
        logger.info("2. 密码正确 (当前配置: 356921)")
        logger.info("3. 服务正在运行")
        return False

def create_database():
    """创建电影推荐数据库"""
    try:
        # 连接到默认数据库
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="356921",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 检查数据库是否已存在
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'movie_recommendation'")
        exists = cursor.fetchone()
        
        if not exists:
            # 创建数据库
            cursor.execute(sql.SQL("CREATE DATABASE movie_recommendation"))
            logger.info("✅ 数据库 'movie_recommendation' 创建成功")
        else:
            logger.info("✅ 数据库 'movie_recommendation' 已存在")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库创建失败: {e}")
        return False

def install_python_dependencies():
    """安装 Python 依赖"""
    try:
        requirements_file = "requirements.txt"
        
        if os.path.exists(requirements_file):
            logger.info("安装 requirements.txt 中的依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        else:
            logger.info("安装核心依赖...")
            dependencies = [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "asyncpg",
                "psycopg2-binary",
                "pydantic",
                "python-dotenv",
                "pandas",
                "numpy"
            ]
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
        
        logger.info("✅ Python 依赖安装成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 依赖安装失败: {e}")
        return False

def create_env_file():
    """创建环境配置文件"""
    try:
        env_content = """# PostgreSQL 数据库配置
DATABASE_URL=postgresql://postgres:356921@localhost:5432/movie_recommendation

# 开发环境配置
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production
"""
        
        env_file = ".env.local"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        
        logger.info(f"✅ 环境配置文件 '{env_file}' 创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建环境文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("智能电影推荐平台 - 数据库设置工具 (Windows)")
    print("=" * 60)
    
    # 检查 PostgreSQL
    if not check_postgresql_installation():
        print("\n请先安装 PostgreSQL:")
        print("1. 下载: https://www.postgresql.org/download/windows/")
        print("2. 安装时设置密码: 356921")
        print("3. 确保服务正在运行")
        return False
    
    # 创建数据库
    if not create_database():
        return False
    
    # 创建环境文件
    if not create_env_file():
        return False
    
    # 安装依赖
    if not install_python_dependencies():
        return False
    
    print("\n" + "=" * 60)
    print("✅ 数据库设置完成!")
    print("\n下一步:")
    print("1. 下载数据集:")
    print("   python backend/scripts/download_tmdb_data.py")
    print("\n2. 导入数据:")
    print("   python backend/scripts/import_tmdb_to_db.py")
    print("\n3. 测试API:")
    print("   python backend/scripts/test_api.py")
    print("\n4. 启动开发服务器:")
    print("   python -m uvicorn app.main:app --reload")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)