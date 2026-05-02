from app.core.db import fetch_all

# 检查user_favorites表结构
result = fetch_all('''
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = %s
    ORDER BY ordinal_position
''', 'user_favorites')
print('user_favorites表结构:')
for row in result:
    print(f"  {row['column_name']}: {row['data_type']}")

# 检查表是否存在
print()
tables = fetch_all('SELECT tablename FROM pg_tables WHERE schemaname = %s', 'public')
print('所有用户相关表:')
for t in tables:
    name = t['tablename']
    if 'user' in name or 'favorite' in name or 'watch' in name or 'history' in name:
        print(f"  {name}")
