import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.core.db import engine

async def check_tables():
    async with engine.connect() as conn:
        # 检查reviews表是否存在
        result = await conn.execute(text('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'reviews'
            );
        '''))
        exists = result.scalar()
        print(f'Reviews table exists: {exists}')
        
        # 列出所有表
        result = await conn.execute(text('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        '''))
        tables = result.fetchall()
        print('\nAll tables in database:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # 检查movies表结构
        result = await conn.execute(text('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'movies'
            ORDER BY ordinal_position;
        '''))
        columns = result.fetchall()
        print('\nMovies table columns:')
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')

if __name__ == '__main__':
    asyncio.run(check_tables())