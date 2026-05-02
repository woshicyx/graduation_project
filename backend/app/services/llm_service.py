"""
LLM 服务 - 用于生成推荐理由
使用智谱 AI GLM-4 模型
"""
import os
import json
from typing import Optional, List, Dict, Any
from app.core.config import settings

# 尝试导入智谱 SDK
try:
    from zhipuai import ZhipuAI
    ZHIPU_SDK_AVAILABLE = True
except ImportError:
    ZHIPU_SDK_AVAILABLE = False
    ZhipuAI = None


class LLMService:
    """LLM 服务类"""
    
    _client: Optional['ZhipuAI'] = None
    
    @classmethod
    def get_client(cls) -> Optional['ZhipuAI']:
        """获取智谱 AI 客户端"""
        if not ZHIPU_SDK_AVAILABLE:
            print("警告: 智谱 SDK 未安装，推荐理由功能将使用模板生成")
            return None
            
        if cls._client is None:
            api_key = settings.zhipuai_api_key or os.getenv("ZHIPUAI_API_KEY")
            if api_key:
                try:
                    cls._client = ZhipuAI(api_key=api_key)
                except Exception as e:
                    print(f"智谱 AI 客户端初始化失败: {e}")
                    return None
        return cls._client
    
    @classmethod
    def generate_recommendation_reason(
        cls,
        movie: Dict[str, Any],
        user_query: Optional[str] = None,
        user_preferences: Optional[List[str]] = None
    ) -> str:
        """
        为单部电影生成推荐理由
        
        Args:
            movie: 电影信息字典
            user_query: 用户原始查询（可选）
            user_preferences: 用户偏好类型列表（可选）
        
        Returns:
            推荐理由字符串
        """
        # 解析电影信息
        title = movie.get('title', '这部电影')
        genres = movie.get('genres', [])
        if isinstance(genres, str):
            try:
                genres = json.loads(genres)
            except:
                genres = []
        genre_str = '、'.join(genres[:3]) if genres else '综合类型'
        
        rating = movie.get('vote_average')
        rating_str = f"{rating:.1f}分" if rating else "高分"
        
        director = movie.get('director')
        director_str = f"由{director}执导" if director else ""
        
        year = None
        if movie.get('release_date'):
            try:
                year = movie['release_date'][:4]
            except:
                pass
        year_str = f"({year})" if year else ""
        
        # 如果有智谱客户端，尝试使用 LLM 生成
        client = cls.get_client()
        if client and user_query:
            try:
                prompt = f"""用户当前的心情/需求是：「{user_query}」

参考电影信息：
- 电影名: {title} {year_str}
- 类型: {genre_str}
- 评分: {rating_str}
{director_str}

请用1-2句简洁的中文推荐理由，要有同理心，像朋友推荐一样告诉用户为什么这部电影适合他现在的状态。

要求：
- 体现对用户情绪的理解和共鸣
- 简短自然，不超过40字
- 不要生硬罗列参数"""
                
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM 生成推荐理由失败: {e}")
        
        # 降级策略：使用模板生成推荐理由
        return cls._generate_template_reason(
            title, genres, rating, user_query, user_preferences
        )
    
    @classmethod
    def _generate_template_reason(
        cls,
        title: str,
        genres: List[str],
        rating: Optional[float],
        user_query: Optional[str] = None,
        user_preferences: Optional[List[str]] = None
    ) -> str:
        """使用模板生成推荐理由"""
        
        reasons = []
        
        # 基于评分
        if rating:
            if rating >= 8.5:
                reasons.append("豆瓣高分神作")
            elif rating >= 8.0:
                reasons.append("高分佳片")
            elif rating >= 7.0:
                reasons.append("口碑之作")
        
        # 基于类型匹配
        if user_preferences and genres:
            matching = [g for g in genres if g in user_preferences]
            if matching:
                reasons.append(f"符合你偏好的{','.join(matching[:2])}类型")
        elif genres:
            reasons.append(f"{genres[0]}类型力作")
        
        # 基于用户查询 - 情感类词汇优化
        if user_query:
            query_lower = user_query.lower()
            if any(k in query_lower for k in ['失恋', '疗伤', '治愈', '安抚', '温暖', '暖心', '治愈系']):
                reasons.append("温暖治愈，抚慰人心")
            elif any(k in query_lower for k in ['感人', '催泪', '温情', '爱情']):
                reasons.append("情感深刻，催人泪下")
            elif any(k in query_lower for k in ['刺激', '紧张', '悬疑', '惊悚']):
                reasons.append("扣人心弦，紧张刺激")
            elif any(k in query_lower for k in ['搞笑', '喜剧', '欢乐', '幽默', '乐趣', '趣味']):
                reasons.append("轻松欢乐，趣味盎然")
            elif any(k in query_lower for k in ['动作', '打斗', '热血', '燃']):
                reasons.append("动作精彩，热血沸腾")
            elif any(k in query_lower for k in ['科幻', '未来', '科技']):
                reasons.append("科幻佳作，脑洞大开")
            elif any(k in query_lower for k in ['烧脑', '悬疑', '推理']):
                reasons.append("烧脑悬疑，层层反转")
            elif any(k in query_lower for k in ['放松', '休闲', '解压']):
                reasons.append("轻松解压，适合放松")
        
        # 组合理由
        if len(reasons) >= 2:
            return f"{reasons[0]}，{reasons[1]}"
        elif reasons:
            return reasons[0]
        else:
            return "值得一看的佳作"
    
    @classmethod
    def batch_generate_reasons(
        cls,
        movies: List[Dict[str, Any]],
        user_query: Optional[str] = None,
        user_preferences: Optional[List[str]] = None
    ) -> Dict[int, str]:
        """
        批量为多部电影生成推荐理由
        
        Returns:
            {movie_id: reason} 字典
        """
        results = {}
        for movie in movies:
            movie_id = movie.get('id')
            if movie_id:
                reason = cls.generate_recommendation_reason(
                    movie, user_query, user_preferences
                )
                results[movie_id] = reason
        return results


# 全局实例
llm_service = LLMService()
