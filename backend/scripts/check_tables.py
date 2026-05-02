import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import Database

# 检查user_favorites表是否存在
try:
    tables = Database.fetch("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE 'user_%%'
    """)
    print('用户相关表:')
    if tables:
        for t in tables:
            print(f'  - {t["table_name"]}')
    else:
        print('  (无)')
except Exception as e:
    print(f'查询失败: {e}')
    import traceback
    traceback.print_exc()