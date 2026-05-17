"""测试filter_first策略是否正常工作"""
import sys
import os

# 添加项目路径
sys.path.insert(0, 'D:/projects/MovieAI/backend')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv('D:/projects/MovieAI/backend/.env')

print("QDRANT_URL:", os.getenv('QDRANT_URL', 'NOT SET'))

from app.services.rag_service_fixed import enhanced_hybrid_search

# 测试带硬性条件的查询
result = enhanced_hybrid_search('想看诺兰导演的科幻片', limit=5)
print('策略:', result.get('strategy'))
print('语义查询:', result.get('semantic_query'))
print('过滤条件:', result.get('filters'))
print('结果数量:', len(result.get('movies', [])))
for m in result.get('movies', [])[:3]:
    print(f'  - {m.get("title")}: {m.get("director")}, 评分{m.get("vote_average")}')

print("\n--- 测试纯语义查询 ---")
result2 = enhanced_hybrid_search('感人至深的爱情故事', limit=5)
print('策略:', result2.get('strategy'))
print('语义查询:', result2.get('semantic_query'))
print('过滤条件:', result2.get('filters'))