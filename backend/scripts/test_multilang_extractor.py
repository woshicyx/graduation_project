"""
测试多语种需求提取功能

使用方法:
    cd backend
    python -m scripts.test_multilang_extractor
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.requirement_extractor import extract_requirements, normalize_genre


def test_queries():
    """测试用例 - 中英混合"""
    test_queries = [
        # 中文查询
        "想看一部科幻电影",
        "诺兰导演的电影",
        "评分8分以上的动作片",
        "想看诺兰导演的科幻片，评分8分以上",
        "2020年以后的恐怖片",
        
        # 英文查询
        "Find me a comedy movie",
        "Nolan's sci-fi movies",
        "Action movies with rating above 8",
        "Comedy with Christopher Nolan",
        
        # 中英混合查询
        "想看搞笑片，comedy movie",
        "诺兰导演的 action movie",
        "科幻片推荐，sci-fi please",
        
        # 口语化
        "有什么好看的恐怖片吗",
        "给我推荐几部搞笑的电影",
        "show me funny movies",
    ]
    
    print("=" * 70)
    print("多语种需求提取测试")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] 查询: {query}")
        print("-" * 50)
        
        try:
            result = extract_requirements(query)
            
            # 检测语言
            is_chinese = any('\u4e00' <= c <= '\u9fff' for c in query)
            query_lang = "中文" if is_chinese else "英文"
            
            print(f"  检测语言: {query_lang}")
            print(f"  语义查询: {result.get('semantic_query', '')}")
            print(f"  LLM解析: {'✓' if result.get('llm_used') else '✗ (降级)'}")
            
            filters = result.get('filters', {})
            if filters:
                print(f"  过滤条件:")
                for key, value in filters.items():
                    print(f"    - {key}: {value}")
            else:
                print(f"  过滤条件: (无)")
                
        except Exception as e:
            print(f"  错误: {e}")
    
    print("\n" + "=" * 70)
    print("类型映射测试")
    print("=" * 70)
    
    test_genres = [
        "Comedy", "comedy", "Action", "Sci-Fi", 
        "搞笑", "恐怖片", "科幻片", "funny movie"
    ]
    
    for genre in test_genres:
        normalized = normalize_genre(genre)
        print(f"  {genre:20} -> {normalized}")


if __name__ == "__main__":
    test_queries()
