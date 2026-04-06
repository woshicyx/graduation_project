#!/usr/bin/env python3
"""
创建剩余的表和触发器
"""

import psycopg2
import sys

def main():
    """主函数"""
    print("=" * 60)
    print("创建剩余数据库表")
    print("=" * 60)
    
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'movie_recommendation',
        'user': 'postgres',
        'password': '356921'
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 1. 创建user_favorites表
        print("\n1. 创建user_favorites表...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    is_liked BOOLEAN DEFAULT true,
                    tags JSONB DEFAULT '[]',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                    
                    CONSTRAINT unique_user_movie_favorite UNIQUE (user_id, movie_id)
                )
            """)
            print("  ✅ user_favorites表创建成功")
        except Exception as e:
            print(f"  ⚠️ user_favorites表创建失败（可能已存在）: {e}")
        
        # 2. 为user_favorites表添加索引
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_favorites_movie_id ON user_favorites(movie_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_favorites_created_at ON user_favorites(created_at)")
            print("  ✅ user_favorites表索引创建成功")
        except Exception as e:
            print(f"  ⚠️ user_favorites表索引创建失败: {e}")
        
        # 3. 创建user_search_history表
        print("\n2. 创建user_search_history表...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_search_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    session_id VARCHAR(100),
                    query VARCHAR(500) NOT NULL,
                    search_type VARCHAR(50) DEFAULT 'keyword',
                    filters JSONB DEFAULT '{}',
                    result_count INTEGER DEFAULT 0,
                    result_ids JSONB DEFAULT '[]',
                    click_count INTEGER DEFAULT 0,
                    is_successful BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT NOW(),
                    
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            print("  ✅ user_search_history表创建成功")
        except Exception as e:
            print(f"  ⚠️ user_search_history表创建失败（可能已存在）: {e}")
        
        # 4. 为user_search_history表添加索引
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON user_search_history(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_session_id ON user_search_history(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON user_search_history(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_query ON user_search_history(query)")
            print("  ✅ user_search_history表索引创建成功")
        except Exception as e:
            print(f"  ⚠️ user_search_history表索引创建失败: {e}")
        
        # 5. 创建admin_audit_logs表
        print("\n3. 创建admin_audit_logs表...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_audit_logs (
                    id SERIAL PRIMARY KEY,
                    admin_id INTEGER,
                    action_type VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(100) NOT NULL,
                    resource_id VARCHAR(100),
                    old_data JSONB,
                    new_data JSONB,
                    changes JSONB,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    
                    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            print("  ✅ admin_audit_logs表创建成功")
        except Exception as e:
            print(f"  ⚠️ admin_audit_logs表创建失败（可能已存在）: {e}")
        
        # 6. 为admin_audit_logs表添加索引
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON admin_audit_logs(admin_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON admin_audit_logs(action_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON admin_audit_logs(created_at)")
            print("  ✅ admin_audit_logs表索引创建成功")
        except Exception as e:
            print(f"  ⚠️ admin_audit_logs表索引创建失败: {e}")
        
        # 7. 创建system_statistics表
        print("\n4. 创建system_statistics表...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_statistics (
                    id SERIAL PRIMARY KEY,
                    stat_date TIMESTAMP NOT NULL,
                    stat_type VARCHAR(100) NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    
                    CONSTRAINT unique_stat_metric UNIQUE (stat_date, stat_type, metric_name)
                )
            """)
            print("  ✅ system_statistics表创建成功")
        except Exception as e:
            print(f"  ⚠️ system_statistics表创建失败（可能已存在）: {e}")
        
        # 8. 为system_statistics表添加索引
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_stats_stat_date ON system_statistics(stat_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_stats_stat_type ON system_statistics(stat_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_stats_metric_name ON system_statistics(metric_name)")
            print("  ✅ system_statistics表索引创建成功")
        except Exception as e:
            print(f"  ⚠️ system_statistics表索引创建失败: {e}")
        
        # 9. 创建popular_search_terms表
        print("\n5. 创建popular_search_terms表...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS popular_search_terms (
                    id SERIAL PRIMARY KEY,
                    term VARCHAR(200) NOT NULL,
                    search_count INTEGER DEFAULT 1,
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    related_movie_ids JSONB DEFAULT '[]',
                    categories JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("  ✅ popular_search_terms表创建成功")
        except Exception as e:
            print(f"  ⚠️ popular_search_terms表创建失败（可能已存在）: {e}")
        
        # 10. 为popular_search_terms表添加索引
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_popular_terms_term ON popular_search_terms(term)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_popular_terms_period_start ON popular_search_terms(period_start)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_popular_terms_period_end ON popular_search_terms(period_end)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_popular_terms_search_count ON popular_search_terms(search_count)")
            print("  ✅ popular_search_terms表索引创建成功")
        except Exception as e:
            print(f"  ⚠️ popular_search_terms表索引创建失败: {e}")
        
        # 11. 更新user_watch_history表
        print("\n6. 更新user_watch_history表...")
        try:
            cursor.execute("ALTER TABLE user_watch_history ADD COLUMN IF NOT EXISTS progress FLOAT DEFAULT 0.0")
            cursor.execute("ALTER TABLE user_watch_history ADD COLUMN IF NOT EXISTS interaction_score INTEGER DEFAULT 1")
            print("  ✅ user_watch_history表更新成功")
        except Exception as e:
            print(f"  ⚠️ user_watch_history表更新失败: {e}")
        
        # 12. 更新user_ratings表
        print("\n7. 更新user_ratings表...")
        try:
            cursor.execute("ALTER TABLE user_ratings ADD COLUMN IF NOT EXISTS sentiment_score FLOAT")
            cursor.execute("ALTER TABLE user_ratings ADD COLUMN IF NOT EXISTS keywords JSONB DEFAULT '[]'")
            print("  ✅ user_ratings表更新成功")
        except Exception as e:
            print(f"  ⚠️ user_ratings表更新失败: {e}")
        
        # 13. 创建更新时间函数
        print("\n8. 创建更新时间函数...")
        try:
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            """)
            print("  ✅ 更新时间函数创建成功")
        except Exception as e:
            print(f"  ⚠️ 更新时间函数创建失败: {e}")
        
        # 14. 为用户表添加触发器
        print("\n9. 为users表添加触发器...")
        try:
            cursor.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
            cursor.execute("""
                CREATE TRIGGER update_users_updated_at 
                    BEFORE UPDATE ON users 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column()
            """)
            print("  ✅ users表触发器创建成功")
        except Exception as e:
            print(f"  ⚠️ users表触发器创建失败: {e}")
        
        # 15. 为用户收藏表添加触发器
        print("\n10. 为user_favorites表添加触发器...")
        try:
            cursor.execute("DROP TRIGGER IF EXISTS update_user_favorites_updated_at ON user_favorites")
            cursor.execute("""
                CREATE TRIGGER update_user_favorites_updated_at 
                    BEFORE UPDATE ON user_favorites 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column()
            """)
            print("  ✅ user_favorites表触发器创建成功")
        except Exception as e:
            print(f"  ⚠️ user_favorites表触发器创建失败（表可能不存在）: {e}")
        
        # 16. 为用户评分表添加触发器
        print("\n11. 为user_ratings表添加触发器...")
        try:
            cursor.execute("DROP TRIGGER IF EXISTS update_user_ratings_updated_at ON user_ratings")
            cursor.execute("""
                CREATE TRIGGER update_user_ratings_updated_at 
                    BEFORE UPDATE ON user_ratings 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column()
            """)
            print("  ✅ user_ratings表触发器创建成功")
        except Exception as e:
            print(f"  ⚠️ user_ratings表触发器创建失败: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 数据库表创建完成!")
        
        # 验证结果
        print("\n📊 验证结果:")
        try:
            conn2 = psycopg2.connect(**db_config)
            cursor2 = conn2.cursor()
            
            cursor2.execute("""
                SELECT table_name
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name IN ('user_favorites', 'user_search_history', 'admin_audit_logs', 'system_statistics', 'popular_search_terms')
                ORDER BY table_name;
            """)
            
            tables = cursor2.fetchall()
            print(f"已创建的表 ({len(tables)}/5):")
            for table in tables:
                print(f"  {table[0]}")
            
            cursor2.execute("""
                SELECT tgname
                FROM pg_trigger
                WHERE tgname IN ('update_users_updated_at', 'update_user_favorites_updated_at', 'update_user_ratings_updated_at')
                ORDER BY tgname;
            """)
            
            triggers = cursor2.fetchall()
            print(f"已创建的触发器 ({len(triggers)}/3):")
            for trigger in triggers:
                print(f"  {trigger[0]}")
            
            cursor2.close()
            conn2.close()
            
        except Exception as e:
            print(f"验证失败: {e}")
        
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        sys.exit(1)
    
    print("\n✅ 用户系统数据库架构已准备就绪!")
    print("\n📋 下一步:")
    print("1. 测试后端API: 启动后端服务")
    print("2. 测试前端: 启动前端服务")
    print("3. 访问 http://localhost:3000/auth 进行用户注册和登录测试")

if __name__ == "__main__":
    main()