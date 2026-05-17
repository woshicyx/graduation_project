"""检查数据库中诺兰导演的电影"""
import sys
import os

sys.path.insert(0, 'D:/projects/MovieAI/backend')
from dotenv import load_dotenv
load_dotenv('D:/projects/MovieAI/backend/.env')

from app.core.db import Database

# 检查诺兰导演的电影
query = """
SELECT id, title, director, genres 
FROM movies 
WHERE director ILIKE %s
LIMIT 10
"""
rows = Database.fetch(query, '%nolan%')
print("=== 诺兰导演的电影 ===")
for row in rows:
    print(f"ID: {row['id']}, Title: {row['title']}, Director: {row['director']}, Genres: {row['genres']}")

# 检查科幻类型的电影
query2 = """
SELECT id, title, director, genres 
FROM movies 
WHERE genres ILIKE %s
LIMIT 10
"""
rows2 = Database.fetch(query2, '%science fiction%')
print("\n=== 科幻类型的电影 ===")
for row in rows2:
    print(f"ID: {row['id']}, Title: {row['title']}, Director: {row['director']}, Genres: {row['genres']}")

# 测试fetch_filtered_movie_ids
from app.services.rag_service_fixed import fetch_filtered_movie_ids

print("\n=== 测试fetch_filtered_movie_ids ===")
# 测试导演过滤
director_ids = fetch_filtered_movie_ids({"director": "Christopher Nolan"}, limit=100)
print(f"Christopher Nolan导演电影数量: {len(director_ids)}")

# 测试类型过滤
scifi_ids = fetch_filtered_movie_ids({"genre": "科幻"}, limit=100)
print(f"科幻类型电影数量: {len(scifi_ids)}")

# 测试组合过滤
both_ids = fetch_filtered_movie_ids({"director": "Christopher Nolan", "genre": "科幻"}, limit=100)
print(f"诺兰+科幻电影数量: {len(both_ids)}")