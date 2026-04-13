"""
重建中文电影向量索引脚本

功能：
1. 删除旧的中英文混合 collection
2. 使用翻译服务生成中文 RAG 文本
3. 重新建立向量索引

使用方法:
    cd backend
    python -m scripts.rebuild_chinese_index
"""
import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import Database
from app.services.rag_service import (
    build_movie_rag_text,
    embed_text,
    ensure_collection_exists,
    _parse_json_field,
    COLLECTION_NAME,
    BATCH_SIZE,
    get_qdrant_client,
)


def delete_collection():
    """删除旧的 collection"""
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME in collection_names:
            client.delete_collection(collection_name=COLLECTION_NAME)
            print(f"✓ 已删除旧 collection: {COLLECTION_NAME}")
            return True
        else:
            print(f"Collection {COLLECTION_NAME} 不存在，无需删除")
            return True
            
    except Exception as e:
        print(f"删除 collection 失败: {e}")
        return False


def update_rag_text(movie_id: int, rag_text: str) -> bool:
    """更新单部电影的 rag_text"""
    try:
        Database.execute(
            "UPDATE movies SET rag_text = %s WHERE id = %s",
            rag_text,
            movie_id
        )
        return True
    except Exception as e:
        print(f"更新电影 {movie_id} rag_text 失败: {e}")
        return False


def main():
    print("=" * 60)
    print("重建中文电影向量索引")
    print("=" * 60)
    
    # 1. 检查配置
    qdrant_url = os.getenv("QDRANT_URL")
    zhipuai_key = os.getenv("ZHIPUAI_API_KEY")
    
    print("\n[配置检查]")
    if not qdrant_url:
        print("✗ QDRANT_URL 未配置")
        return
    
    if not zhipuai_key or zhipuai_key == "your-zhipuai-api-key-here":
        print("✗ ZHIPUAI_API_KEY 未配置")
        print("  请在 backend/.env 中添加智谱 API Key")
        return
    
    print(f"✓ QDRANT_URL: {qdrant_url}")
    print(f"✓ ZHIPUAI_API_KEY: {'*' * 20}{zhipuai_key[-10:]}")
    
    # 2. 确认操作
    print("\n⚠️  警告：此操作将删除现有向量索引并重建！")
    confirm = input("是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消操作")
        return
    
    # 3. 删除旧 collection
    print("\n[1/5] 删除旧 collection...")
    if not delete_collection():
        print("✗ 删除失败")
        return
    print("✓ 删除完成")
    
    # 4. 创建新 collection
    print("\n[2/5] 创建新 collection...")
    if not ensure_collection_exists():
        print("✗ Collection 创建失败")
        return
    print("✓ Collection 创建完成")
    
    # 5. 读取电影数据
    print("\n[3/5] 从 PostgreSQL 读取电影数据...")
    query = """
        SELECT id, title, original_title, overview, tagline, genres, 
               keywords, director, original_language, vote_average, popularity
        FROM movies
        WHERE overview IS NOT NULL AND overview != ''
        ORDER BY id
    """
    movies = Database.fetch(query)
    print(f"✓ 共读取 {len(movies)} 部电影")
    
    if not movies:
        print("✗ 没有电影数据可处理")
        return
    
    movies = [dict(row) for row in movies]
    
    # 6. 生成中文 RAG 文本并索引
    print("\n[4/5] 生成中文 RAG 文本...")
    total_success = 0
    total_fail = 0
    total_fail_ids = []
    points = []
    
    # 批量处理
    for i, movie in enumerate(movies):
        movie_id = movie.get("id")
        
        # 生成中文 RAG 文本
        rag_text = build_movie_rag_text(movie, target_lang="zh")
        
        # 更新数据库
        if update_rag_text(movie_id, rag_text):
            total_success += 1
        else:
            total_fail += 1
            total_fail_ids.append(movie_id)
        
        # 生成向量
        vector = embed_text(rag_text)
        if vector:
            points.append({
                "id": movie_id,
                "vector": vector,
                "payload": {
                    "movie_id": movie_id,
                    "title": movie.get("title", ""),
                    "original_title": movie.get("original_title", ""),
                    "genres": _parse_json_field(movie.get("genres"), extract_name=True),
                    "keywords": _parse_json_field(movie.get("keywords"), extract_name=True),
                    "vote_average": movie.get("vote_average", 0) or 0,
                    "popularity": movie.get("popularity", 0) or 0,
                    "director": movie.get("director", "") or "",
                    "language": movie.get("original_language", "") or "",
                    "language_version": "zh",
                }
            })
        else:
            print(f"  警告: 电影 {movie_id} 向量生成失败")
        
        # 批量写入
        if len(points) >= BATCH_SIZE:
            try:
                client = get_qdrant_client()
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                print(f"  批量写入 {len(points)} 条完成")
                points = []
            except Exception as e:
                print(f"  批量写入失败: {e}")
        
        # 进度显示
        if (i + 1) % 50 == 0 or i + 1 == len(movies):
            print(f"  进度: {i + 1}/{len(movies)}, rag_text更新: {total_success}, 向量准备: {len(points)}")
        
        # 避免 API 限流
        time.sleep(0.05)
    
    # 写入剩余数据
    if points:
        try:
            client = get_qdrant_client()
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"  批量写入 {len(points)} 条完成")
        except Exception as e:
            print(f"  批量写入失败: {e}")
    
    # 7. 完成汇总
    print(f"\n{'='*60}")
    print("重建完成汇总")
    print(f"{'='*60}")
    print(f"  总电影数: {len(movies)}")
    print(f"  rag_text 更新: 成功 {total_success}, 失败 {total_fail}")
    print(f"  向量索引: 成功 {len(movies) - total_fail}, 失败 {total_fail}")
    
    if total_fail_ids:
        print(f"\n  失败的电影ID (前10个): {total_fail_ids[:10]}")
        if len(total_fail_ids) > 10:
            print(f"  ... 共 {len(total_fail_ids)} 个")
    
    print(f"\n✓ 中文向量索引重建完成!")
    print(f"\n下一步:")
    print(f"  1. 测试 API: POST /api/ai/recommend")
    print(f"  2. 测试查询: '想看诺兰导演的科幻片'")


if __name__ == "__main__":
    main()
