import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import Database

# 检查user_search_history表结构
try:
    t = Database.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_search_history' 
        ORDER BY ordinal_position
    """)
    print('user_search_history 表结构:')
    if t:
        for r in t:
            print(f"  {r['column_name']}: {r['data_type']}")
    else:
        print('  (表不存在)')
except Exception as e:
    print(f'查询失败: {e}')

# 检查user_ratings表结构
try:
    t = Database.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_ratings' 
        ORDER BY ordinal_position
    """)
    print('\nuser_ratings 表结构:')
    if t:
        for r in t:
            print(f"  {r['column_name']}: {r['data_type']}")
    else:
        print('  (表不存在)')
except Exception as e:
    print(f'查询失败: {e}')
