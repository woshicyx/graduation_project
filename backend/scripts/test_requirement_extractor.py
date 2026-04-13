"""
测试 LLM 需求提取功能

使用方法:
    cd backend
    python -m scripts.test_requirement_extractor
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.requirement_extractor import extract_requirements


def test_cases():
    """测试用例"""
    test_queries = [
        # 基础测试
        "想看一部科幻电影",
        "诺兰导演的电影",
        "评分8分以上的动作片",
        
        # 复杂测试
        "想看诺兰导演的科幻片，评分8分以上",
        "2020年以后的恐怖片",
        "120分钟以内的喜剧",
        "轻松搞笑的动画电影",
        
        # 边界测试
        "随便看看",
        "有什么好片推荐吗",
        
        # 英文混合
        "Christopher Nolan's sci-fi movies",
    ]
    
    print("=" * 60)
    print("LLM 需求提取测试")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] 查询: {query}")
        print("-" * 40)
        
        try:
            result = extract_requirements(query)
            print(f"  语义查询: {result.get('semantic_query', '')}")
            print(f"  过滤条件:")
            filters = result.get('filters', {})
            if filters:
                for key, value in filters.items():
                    print(f"    - {key}: {value}")
            else:
                print("    (无过滤条件)")
        except Exception as e:
            print(f"  错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_cases()
