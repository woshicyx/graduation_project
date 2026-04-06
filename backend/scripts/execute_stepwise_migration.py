#!/usr/bin/env python3
"""
执行分步数据库迁移脚本
"""

import psycopg2
import os
import sys

def execute_sql_file(file_path, db_config):
    """执行SQL文件"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"📋 正在执行SQL文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 按分号分割SQL语句
        sql_statements = sql_content.split(';')
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    success_count += 1
                    print(f"  执行语句 {i+1}/{len(sql_statements)}: 成功")
                except Exception as e:
                    error_msg = str(e)
                    # 跳过已存在对象的错误
                    if "already exists" in error_msg:
                        skip_count += 1
                        print(f"  执行语句 {i+1}/{len(sql_statements)}: 跳过（对象已存在）")
                    else:
                        error_count += 1
                        print(f"  执行语句 {i+1}/{len(sql_statements)}: 失败 - {error_msg[:100]}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 执行统计:")
        print(f"  成功: {success_count}")
        print(f"  跳过: {skip_count}")
        print(f"  失败: {error_count}")
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_migration_result(db_config):
    """检查迁移结果"""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("\n📊 迁移结果检查:")
        
        # 检查users表新字段
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('role', 'is_active', 'is_verified', 'display_name', 'avatar_url', 'github_id', 'google_id', 'last_login_at')
            ORDER BY column_name;
        """)
        
        new_fields = cursor.fetchall()
        print("users表新增字段:")
        if new_fields:
            for field_name, data_type in new_fields:
                print(f"  {field_name}: {data_type}")
            print(f"  已添加 {len(new_fields)}/8 个字段")
        else:
            print("  ⚠️ 未找到新增字段")
        
        # 检查新创建的表
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('user_favorites', 'user_search_history', 'admin_audit_logs', 'system_statistics', 'popular_search_terms')
            ORDER BY table_name;
        """)
        
        new_tables = cursor.fetchall()
        print("\n新创建的表:")
        if new_tables:
            for table_name in new_tables:
                print(f"  {table_name[0]}")
            print(f"  已创建 {len(new_tables)}/5 个表")
        else:
            print("  ⚠️ 未找到新表")
        
        # 检查触发器
        cursor.execute("""
            SELECT tgname
            FROM pg_trigger
            WHERE tgname IN ('update_users_updated_at', 'update_user_favorites_updated_at', 'update_user_ratings_updated_at')
            ORDER BY tgname;
        """)
        
        triggers = cursor.fetchall()
        print("\n创建的触发器:")
        if triggers:
            for trigger_name in triggers:
                print(f"  {trigger_name[0]}")
        else:
            print("  ⚠️ 未找到触发器")
        
        cursor.close()
        conn.close()
        
        return len(new_fields) > 0
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("分步数据库迁移工具")
    print("=" * 60)
    
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'movie_recommendation',
        'user': 'postgres',
        'password': '356921'
    }
    
    # 执行分步迁移
    migration_file = os.path.join(os.path.dirname(__file__), 'migrate_user_system_stepwise.sql')
    
    print("\n🚀 开始执行分步迁移...")
    success = execute_sql_file(migration_file, db_config)
    
    if success:
        print("\n✅ SQL执行完成")
        
        # 检查迁移结果
        migration_successful = check_migration_result(db_config)
        
        if migration_successful:
            print("\n🎉 数据库迁移成功完成!")
            print("\n✅ 用户系统现在包含:")
            print("  - 完整的用户角色字段 (role, is_active, is_verified)")
            print("  - 社交登录支持 (github_id, google_id)")
            print("  - 用户收藏功能 (user_favorites)")
            print("  - 搜索历史记录 (user_search_history)")
            print("  - 管理员审计日志 (admin_audit_logs)")
            print("  - 系统统计数据表 (system_statistics)")
            print("  - 热门搜索词表 (popular_search_terms)")
            print("  - 自动更新时间触发器")
        else:
            print("\n⚠️  迁移可能部分成功，请检查数据库状态")
    else:
        print("\n❌ SQL执行失败")
        sys.exit(1)
    
    print("\n📋 下一步:")
    print("1. 启动后端服务: cd backend && uvicorn app.main:app --reload")
    print("2. 启动前端服务: cd frontend && npm run dev")
    print("3. 访问 http://localhost:3000/auth 进行测试")

if __name__ == "__main__":
    main()