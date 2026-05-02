"""测试推荐理由生成"""
import sys
sys.path.insert(0, '.')

from app.services.llm_service import LLMService

# 测试数据
movie = {
    "id": 1,
    "title": "盗梦空间",
    "genres": ["科幻", "动作", "惊悚"],
    "vote_average": 9.3,
    "director": "克里斯托弗·诺兰",
    "release_date": "2010-09-01"
}

# 测试推荐理由生成
print("测试 LLM 推荐理由生成...")
print("-" * 50)

# 测试模板生成
reason = LLMService.generate_recommendation_reason(
    movie, 
    user_query="推荐一部好看的科幻电影",
    user_preferences=["科幻", "动作"]
)
print(f"电影: {movie['title']}")
print(f"推荐理由: {reason}")
print("-" * 50)

# 测试批量生成
movies = [
    {"id": 1, "title": "盗梦空间", "genres": ["科幻", "动作"], "vote_average": 9.3},
    {"id": 2, "title": "星际穿越", "genres": ["科幻", "冒险"], "vote_average": 9.1},
    {"id": 3, "title": "火星救援", "genres": ["科幻", "冒险"], "vote_average": 8.6},
]

print("\n批量测试:")
reasons = LLMService.batch_generate_reasons(movies, "科幻电影")
for mid, reason in reasons.items():
    print(f"  电影ID {mid}: {reason}")

print("\n测试完成!")
