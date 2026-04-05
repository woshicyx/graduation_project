#!/usr/bin/env python3
"""
直接检查PostgreSQL数据库表结构
"""

import psycopg2

def check_database():
    """直接检查数据库表结构"""
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'movie_recommendation',
        'user': 'postgres',
        'password': '356921'
    }
    
    try:
        print("连接到数据库...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("连接成功!")
        
        # 检查所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n数据库中的所有表 ({len(tables)} 个):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查movies表结构
        if any('movies' in table[0].lower() for table in tables):
            print("\n检查movies表结构...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'movies'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"movies表有 {len(columns)} 个字段:")
            print(f"{'字段名':<25} {'数据类型':<20} {'可为空':<10}")
            print("-" * 60)
            for col in columns:
                print(f"{col[0]:<25} {col[1]:<20} {col[2]:<10}")
            
            # 检查数据
            cursor.execute("SELECT COUNT(*) FROM movies;")
            count = cursor.fetchone()[0]
            print(f"\nmovies表中的电影数量: {count}")
            
            if count > 0:
                cursor.execute("""
                    SELECT title, release_date, vote_average, revenue 
                    FROM movies 
                    ORDER BY vote_average DESC 
                    LIMIT 5;
                """)
                top_movies = cursor.fetchall()
                print("\n评分最高的5部电影:")
                for movie in top_movies:
                    print(f"  - {movie[0]} ({movie[1]}) - 评分: {movie[2]}, 票房: ${movie[3]:,}")
        
        # 检查reviews表
        if any('reviews' in table[0].lower() for table in tables):
            print("\n检查reviews表结构...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'reviews'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"reviews表有 {len(columns)} 个字段:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'可空' if col[2] == 'YES' else '非空'})")
            
            cursor.execute("SELECT COUNT(*) FROM reviews;")
            count = cursor.fetchone()[0]
            print(f"reviews表中的评论数量: {count}")
        
        cursor.close()
        conn.close()
        print("\n数据库检查完成!")
        
    except Exception as e:
        print(f"数据库连接或查询失败: {e}")
        print("请确保:")
        print("1. PostgreSQL服务正在运行")
        print("2. 数据库 'movie_recommendation' 存在")
        print("3. 用户名/密码正确")

if __name__ == "__main__":
    check_database()