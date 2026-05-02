"""直接测试LLM服务（不依赖app导入）"""
import os
import json
import sys

# 模拟配置
class MockSettings:
    zhipuai_api_key = os.getenv("ZHIPUAI_API_KEY")
    openai_api_key = None
    openai_api_base_url = None

settings = MockSettings()

# 尝试导入智谱 SDK
try:
    from zhipuai import ZhipuAI
    ZHIPU_SDK_AVAILABLE = True
except ImportError:
    ZHIPU_SDK_AVAILABLE = False
    ZhipuAI = None
    print("警告: 智谱 SDK 未安装，将使用模板生成")

class LLMService:
    _client = None
    
    @classmethod
    def get_client(cls):
        if not ZHIPU_SDK_AVAILABLE:
            return None
        if cls._client is None:
            api_key = settings.zhipuai_api_key
            if api_key:
                try:
                    cls._client = ZhipuAI(api_key=api_key)
                except Exception as e:
                    print(f"初始化失败: {e}")
        return cls._client
    
    @classmethod
    def generate_recommendation_reason(cls, movie, user_query=None, user_preferences=None):
        title = movie.get('title', '这部电影')
        genres = movie.get('genres', [])
        if isinstance(genres, str):
            try:
                genres = json.loads(genres)
            except:
                genres = []
        genre_str = '、'.join(genres[:3]) if genres else '综合类型'
        
        rating = movie.get('vote_average')
        
        # 尝试使用LLM
        client = cls.get_client()
        if client and user_query:
            try:
                prompt = f"""用户想找: "{user_query}"
电影: {title}, 类型: {genre_str}, 评分: {rating}分
生成1-2句简洁中文推荐理由，不超过50字。"""
                
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.7
                )
                
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM调用失败: {e}")
        
        # 模板降级
        return cls._generate_template_reason(title, genres, rating, user_query)
    
    @classmethod
    def _generate_template_reason(cls, title, genres, rating, user_query):
        reasons = []
        if rating:
            if rating >= 8.5:
                reasons.append("豆瓣高分神作")
            elif rating >= 8.0:
                reasons.append("高分佳片")
            elif rating >= 7.0:
                reasons.append("口碑之作")
        
        if genres:
            reasons.append(f"{genres[0]}类型力作")
        
        if user_query:
            q = user_query.lower()
            if any(k in q for k in ['感人', '催泪', '爱情']):
                reasons.append("情感深刻")
            elif any(k in q for k in ['刺激', '紧张', '悬疑']):
                reasons.append("扣人心弦")
            elif any(k in q for k in ['搞笑', '喜剧']):
                reasons.append("轻松欢乐")
            elif any(k in q for k in ['科幻']):
                reasons.append("科幻佳作")
        
        if len(reasons) >= 2:
            return f"{reasons[0]}，{reasons[1]}"
        elif reasons:
            return reasons[0]
        return "值得一看的佳作"
    
    @classmethod
    def batch_generate_reasons(cls, movies, user_query=None, user_preferences=None):
        results = {}
        for movie in movies:
            mid = movie.get('id')
            if mid:
                results[mid] = cls.generate_recommendation_reason(movie, user_query, user_preferences)
        return results

# 测试
print("=" * 50)
print("LLM 推荐理由生成测试")
print("=" * 50)

movie1 = {"id": 1, "title": "盗梦空间", "genres": ["科幻", "动作", "惊悚"], "vote_average": 9.3}
movie2 = {"id": 2, "title": "星际穿越", "genres": ["科幻", "冒险"], "vote_average": 9.1}
movie3 = {"id": 3, "title": "你好，李焕英", "genres": ["喜剧", "温情"], "vote_average": 8.0}

movies = [movie1, movie2, movie3]

print("\n测试1: 科幻电影查询")
reasons = LLMService.batch_generate_reasons(movies, "推荐一部好看的科幻电影")
for mid, reason in reasons.items():
    print(f"  {mid}: {reason}")

print("\n测试2: 温情喜剧查询")
reasons = LLMService.batch_generate_reasons(movies, "想看一部温情的喜剧电影")
for mid, reason in reasons.items():
    print(f"  {mid}: {reason}")

print("\n测试完成!")
