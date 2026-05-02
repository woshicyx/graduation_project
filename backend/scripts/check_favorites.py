import os
os.environ.setdefault('PYTHONPATH', '.')
from app.core.db import Database

# 查看user_favorites表结构
r = Database.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_favorites' ORDER BY ordinal_position")
print('user_favorites表结构:')
for c in r: print(f"  {c['column_name']}: {c['data_type']}")

# 查看user_watch_history表结构
r2 = Database.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_watch_history' ORDER BY ordinal_position")
print('\nuser_watch_history表结构:')
for c in r2: print(f"  {c['column_name']}: {c['data_type']}")
