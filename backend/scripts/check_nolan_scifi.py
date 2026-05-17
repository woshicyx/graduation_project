"""检查星际穿越和盗梦空间"""
import sys
sys.path.insert(0, 'D:/projects/MovieAI/backend')
from dotenv import load_dotenv
load_dotenv('D:/projects/MovieAI/backend/.env')

from app.core.db import Database

# 检查盗梦空间和星际穿越
query = """
SELECT id, title, director, genres 
FROM movies 
WHERE title ILIKE %s OR title ILIKE %s
"""
rows = Database.fetch(query, '%Inception%', '%星际穿越%')
print("=== 盗梦空间/星际穿越 ===")
for row in rows:
    print(f"ID: {row['id']}, Title: {row['title']}, Director: {row['director']}, Genres: {row['genres']}")

# 检查数据库中是否有诺兰的科幻片
query2 = """
SELECT id, title, director, genres 
FROM movies 
WHERE director = 'Christopher Nolan' 
  AND (genres ILIKE '%Science Fiction%' OR genres ILIKE '%Sci-Fi%')
"""
rows2 = Database.fetch(query2)
print("\n=== 诺兰的科幻片 ===")
for row in rows2:
    print(f"ID: {row['id']}, Title: {row['title']}, Genres: {row['genres']}")
if not rows2:
    print("没有找到诺兰的科幻片！")