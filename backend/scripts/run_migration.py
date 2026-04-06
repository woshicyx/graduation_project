#!/usr/bin/env python3
"""
运行用户系统数据库迁移脚本
"""

import psycopg2
import os
import sys

def run_migration():
    """执行数据库迁移"""
    try:
        # 数据库连接配置
        db_config = {
            'host': 'localhost',
            port=5432,
            'database': 'movie_recommendation',
            'user': 'postgres',
            'password': '356921'
        }
        
        print("正在连接到数据库...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True  # 启用自动提交
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 读取迁移SQL文件
        migration_file = os.path.join(os.path.dirname(__file__), 'migrate_user_system.sql')
        
        if not os.path.exists(migration_file):
            print(f"❌ 迁移文件不存在: {migration_file}")
            return False
        
        print(f"📋 正在执行迁移脚本: {migration_file}")
        
        # 读取SQL文件内容
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 按分号分割SQL语句（简单处理）
        sql_statements = sql_content.split(';')
        
        # 执行每个SQL语句
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"  执行语句 {i+1}/{len(sql_statements)}: 成功")
                except Exception as e:
                    print(f"  执行语句 {i+1}/{len(sql_statements)}: 失败 - {e}")
        
        # 验证迁移结果
        print("\n📊 迁移结果验证:")
        cursor.execute("""
            SELECT table_name, COUNT(*) as column_count
            FROM information_schema.columns 
            WHERE table_name IN (
                'users', 'user_favorites', 'user_search_history', 
                'admin_audit_logs', 'system_statistics', 'popular_search_terms'
            )
            GROUP BY table_name
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("表结构统计:")
        for table_name, column_count in tables:
            print(f"  {table_name}: {column_count} 个字段")
        
        # 检查users表是否包含新字段
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('role', 'is_active', 'is_verified', 'display_name', 'avatar_url')
            ORDER BY column_name;
        """)
        
        new_fields = cursor.fetchall()
        print("\nusers表新增字段:")
        if new_fields:
            for field_name, data_type in new_fields:
                print(f"  {field_name}: {data_type}")
        else:
            print("  ⚠️ 未找到新增字段")
        
        # 检查管理员账户
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';")
        admin_count = cursor.fetchone()[0]
        print(f"\n管理员账户数量: {admin_count}")
        
        if admin_count == 0:
            print("⚠️ 警告: 未找到管理员账户，请手动创建")
        
        cursor.close()
        conn.close()
        
        print("\n✅ 数据库迁移完成!")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("用户系统数据库迁移工具")
    print("=" * 60)
    
    # 询问用户确认
    response = input("\n⚠️  即将执行数据库迁移，可能会修改现有表结构。是否继续? (y/N): ")
    
    if response.lower() != 'y':
        print("已取消迁移操作")
        return
    
    success = run_migration()
    
    if success:
        print("\n🎉 迁移成功完成!")
        print("下一步:")
        print("1. 启动后端服务: cd backend && uvicorn app.main:app --reload")
        print("2. 启动前端服务: cd frontend && npm run dev")
        print("3. 访问 http://localhost:3000/auth 进行测试")
    else:
        print("\n❌ 迁移失败，请检查错误信息")

if __name__ == "__main__":
    main()