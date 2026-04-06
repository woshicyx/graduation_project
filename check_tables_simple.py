#!/usr/bin/env python3
"""
简单检查用户表结构
"""
import sys
import os

# 添加backend到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import psycopg2
    print("✅ psycopg2已安装")
except ImportError as e:
    print(f"❌ psycopg2未安装: {e}")
    print("请运行: pip install psycopg2-binary")
    sys.exit(1)

def main():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='movie_recommendation',
            user='postgres',
            password='356921'
        )
        cursor = conn.cursor()
        
        print("✅ 数据库连接成功")
        
        # 检查users表
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users';
        """)
        users_cols = cursor.fetchall()
        print(f"\n📋 users表字段 ({len(users_cols)}个):")
        for col in users_cols:
            print(f"  - {col[0]}: {col[1]}")
        
        # 检查user_watch_history表
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_watch_history';
        """)
        watch_cols = cursor.fetchall()
        print(f"\n📋 user_watch_history表字段 ({len(watch_cols)}个):")
        for col in watch_cols:
            print(f"  - {col[0]}: {col[1]}")
        
        # 检查user_ratings表
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_ratings';
        """)
        ratings_cols = cursor.fetchall()
        print(f"\n📋 user_ratings表字段 ({len(ratings_cols)}个):")
        for col in ratings_cols:
            print(f"  - {col[0]}: {col[1]}")
        
        # 检查表数据量
        tables = ['users', 'user_watch_history', 'user_ratings']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"\n📊 {table}: {count} 条记录")
        
        # 检查是否有收藏表
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('user_favorites', 'favorites', 'user_likes', 'likes')
            AND table_schema = 'public';
        """)
        fav_tables = cursor.fetchall()
        print(f"\n❤️  收藏相关表:")
        if fav_tables:
            for table in fav_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} 条记录")
        else:
            print("  - 无收藏相关表")
        
        conn.close()
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()