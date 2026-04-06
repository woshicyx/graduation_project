#!/usr/bin/env python3
"""
检查用户相关表结构
"""

import psycopg2
import sys

def main():
    try:
        # 数据库连接配置
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='movie_recommendation',
            user='postgres',
            password='356921'
        )
        cursor = conn.cursor()
        
        print("=" * 60)
        print("用户系统表结构检查")
        print("=" * 60)
        
        # 检查users表结构
        print("\n1. users表结构:")
        print("-" * 60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        users_columns = cursor.fetchall()
        if not users_columns:
            print("  ⚠️ users表不存在或为空")
        else:
            print(f"  字段数: {len(users_columns)}")
            for col in users_columns:
                print(f"    {col[0].ljust(25)} {col[1].ljust(20)} {col[2]}")
        
        # 检查user_watch_history表结构
        print("\n2. user_watch_history表结构:")
        print("-" * 60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'user_watch_history' 
            ORDER BY ordinal_position;
        """)
        watch_columns = cursor.fetchall()
        if not watch_columns:
            print("  ⚠️ user_watch_history表不存在或为空")
        else:
            print(f"  字段数: {len(watch_columns)}")
            for col in watch_columns:
                print(f"    {col[0].ljust(25)} {col[1].ljust(20)} {col[2]}")
        
        # 检查user_ratings表结构
        print("\n3. user_ratings表结构:")
        print("-" * 60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'user_ratings' 
            ORDER BY ordinal_position;
        """)
        ratings_columns = cursor.fetchall()
        if not ratings_columns:
            print("  ⚠️ user_ratings表不存在或为空")
        else:
            print(f"  字段数: {len(ratings_columns)}")
            for col in ratings_columns:
                print(f"    {col[0].ljust(25)} {col[1].ljust(20)} {col[2]}")
        
        # 检查表数据
        print("\n4. 表数据统计:")
        print("-" * 60)
        
        tables_to_check = ['users', 'user_watch_history', 'user_ratings']
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")
        
        # 检查users表是否有管理员
        print("\n5. 用户角色检查:")
        print("-" * 60)
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role';
        """)
        has_role = cursor.fetchone()
        if has_role:
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role;")
            roles = cursor.fetchall()
            for role, count in roles:
                print(f"  角色 '{role}': {count} 用户")
        else:
            print("  ⚠️ users表没有role字段")
        
        # 检查收藏功能相关表
        print("\n6. 收藏功能检查:")
        print("-" * 60)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('user_favorites', 'favorites', 'user_likes');
        """)
        favorite_tables = cursor.fetchall()
        if favorite_tables:
            for table in favorite_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"  {table[0]}: {count} 条记录")
        else:
            print("  ⚠️ 未找到收藏相关表")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("检查完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()