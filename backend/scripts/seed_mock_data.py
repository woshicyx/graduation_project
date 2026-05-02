"""
Mock数据生成脚本 - 为协同过滤推荐生成测试数据

使用方法：
    python -m scripts.seed_mock_data

依赖安装：
    pip install faker psycopg2-binary bcrypt

注意：
    - 运行前确保数据库连接配置正确（.env文件）
    - 脚本会生成用户、浏览历史、收藏数据
    - 带有用户画像（Personas）的偏好生成
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import bcrypt
from faker import Faker

# 添加backend路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.db import get_connection, init_db, close_db

# 初始化Faker
fake = Faker(['zh_CN', 'en_US'])
Faker.seed(42)
random.seed(42)


# ==================== 用户画像定义 ====================

class Persona:
    """用户画像基类"""
    name: str = "普通用户"
    genres: List[str] = []  # 偏好类型
    like_probability: float = 0.25  # 喜欢概率
    view_count_range: tuple = (20, 50)  # 浏览数量范围
    
    def should_like(self) -> bool:
        """判断是否喜欢当前电影"""
        return random.random() < self.like_probability
    
    def prefers_genre(self, movie_genres: List[str]) -> bool:
        """判断是否偏好该电影的类型"""
        if not movie_genres:
            return False
        return any(g in self.genres for g in movie_genres)
    
    def genre_weight(self, movie_genres: List[str]) -> float:
        """获取类型匹配权重（0-1）"""
        if not movie_genres or not self.genres:
            return 0.0
        overlap = sum(1 for g in movie_genres if g in self.genres)
        return overlap / len(self.genres)


class SciFiActionFan(Persona):
    """科幻动作迷 - 80%概率只看科幻/动作电影"""
    name = "科幻动作迷"
    genres = ["Science Fiction", "Action", "Adventure", "Fantasy"]
    like_probability = 0.30
    
    def should_view(self, movie_genres: List[str]) -> bool:
        """80%概率选择偏好类型"""
        if self.prefers_genre(movie_genres):
            return random.random() < 0.8
        return random.random() < 0.2  # 20%概率看其他类型


class RomanceDramaLover(Persona):
    """文艺爱情控 - 主要看爱情/剧情类电影"""
    name = "文艺爱情控"
    genres = ["Romance", "Drama", "Music"]
    like_probability = 0.35
    
    def should_view(self, movie_genres: List[str]) -> bool:
        if self.prefers_genre(movie_genres):
            return random.random() < 0.75
        return random.random() < 0.25


class HorrorThrillerFan(Persona):
    """惊悚恐怖迷 - 喜欢恐怖/惊悚"""
    name = "惊悚恐怖迷"
    genres = ["Horror", "Thriller", "Mystery"]
    like_probability = 0.28
    
    def should_view(self, movie_genres: List[str]) -> bool:
        if self.prefers_genre(movie_genres):
            return random.random() < 0.7
        return random.random() < 0.3


class ComedyFan(Persona):
    """喜剧迷 - 喜欢轻松喜剧"""
    name = "喜剧迷"
    genres = ["Comedy", "Family"]
    like_probability = 0.32
    
    def should_view(self, movie_genres: List[str]) -> bool:
        if self.prefers_genre(movie_genres):
            return random.random() < 0.7
        return random.random() < 0.3


class Omnivore(Persona):
    """杂食观众 - 什么都看"""
    name = "杂食观众"
    genres = ["Science Fiction", "Action", "Romance", "Drama", "Comedy", "Horror", "Thriller", "Adventure"]
    like_probability = 0.22
    
    def should_view(self, movie_genres: List[str]) -> bool:
        return True  # 什么都看


# 用户画像池（用于分配给用户）
PERSONAS: List[Persona] = [
    SciFiActionFan(),
    RomanceDramaLover(),
    HorrorThrillerFan(),
    ComedyFan(),
    Omnivore(),
]


# ==================== 辅助函数 ====================

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def random_date(days_back: int = 90) -> datetime:
    """生成过去N天内的随机日期"""
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )


def parse_genres(genres_str: Optional[str]) -> List[str]:
    """解析genres JSON字符串"""
    if not genres_str:
        return []
    try:
        data = json.loads(genres_str)
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return [item.get('name', '') for item in data if item.get('name')]
            return [str(item) for item in data]
    except (json.JSONDecodeError, TypeError):
        pass
    return []


# ==================== 数据生成函数 ====================

def create_mock_users(count: int = 100) -> List[int]:
    """创建模拟用户，返回用户ID列表"""
    print(f"\n📝 正在生成 {count} 个模拟用户...")
    
    user_ids = []
    created = 0
    
    for i in range(count):
        username = f"user_{fake.user_name()}_{random.randint(1000, 9999)}"
        email = f"{username}@example.com"
        password_hash = get_password_hash("password123")
        now = random_date(days_back=180)  # 用户注册时间在6个月内
        
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (username, email, password_hash, display_name, 
                                          role, is_active, is_verified, preferences, 
                                          created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        username,
                        email,
                        password_hash,
                        username,
                        'user',
                        True,
                        False,
                        '{}',
                        now,
                        now
                    ))
                    result = cur.fetchone()
                    user_id = result[0] if result else None
                    
                    if user_id:
                        conn.commit()
                        user_ids.append(user_id)
                        created += 1
                        
                        if created % 10 == 0:
                            print(f"  已创建 {created}/{count} 用户...")
        except Exception as e:
            print(f"  创建用户失败: {username} - {e}")
            continue
    
    print(f"✅ 成功创建 {created} 个用户")
    return user_ids


def get_movies_by_genre() -> Dict[str, List[Dict]]:
    """按类型获取电影"""
    print("\n📚 读取电影数据...")
    
    movies = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, genres, vote_average, popularity
                FROM movies
                WHERE poster_path IS NOT NULL
                AND vote_average >= 6.0
                LIMIT 500
            """)
            for row in cur.fetchall():
                genres = parse_genres(row[2])
                movies.append({
                    'id': row[0],
                    'title': row[1],
                    'genres': genres,
                    'vote_average': row[3] or 0,
                    'popularity': row[4] or 0
                })
    
    # 按类型分组
    genre_movies: Dict[str, List[Dict]] = {}
    for movie in movies:
        if movie['genres']:
            for genre in movie['genres']:
                if genre not in genre_movies:
                    genre_movies[genre] = []
                genre_movies[genre].append(movie)
        else:
            if 'Other' not in genre_movies:
                genre_movies['Other'] = []
            genre_movies['Other'].append(movie)
    
    print(f"  读取到 {len(movies)} 部电影，分组到 {len(genre_movies)} 个类型")
    return genre_movies


def get_all_movies() -> List[Dict]:
    """获取所有电影"""
    movies = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, genres, vote_average, popularity
                FROM movies
                WHERE poster_path IS NOT NULL
                LIMIT 1000
            """)
            for row in cur.fetchall():
                genres = parse_genres(row[2])
                movies.append({
                    'id': row[0],
                    'title': row[1],
                    'genres': genres,
                    'vote_average': row[3] or 0,
                    'popularity': row[4] or 0
                })
    return movies


def select_movies_for_user(persona: Persona, all_movies: List[Dict], count: int) -> List[Dict]:
    """根据用户画像选择电影"""
    selected = []
    remaining = []
    
    # 分类电影
    for movie in all_movies:
        if persona.prefers_genre(movie['genres']):
            remaining.append(movie)
        else:
            remaining.append(movie)
    
    random.shuffle(remaining)
    
    # 根据画像选择
    for movie in remaining:
        if len(selected) >= count:
            break
        
        # 优先选择偏好类型的电影
        if persona.prefers_genre(movie['genres']) and random.random() < 0.8:
            selected.append(movie)
        elif random.random() < 0.2:  # 20%概率选择其他类型
            selected.append(movie)
    
    # 如果不够，随机补充
    while len(selected) < count and remaining:
        movie = random.choice(remaining)
        if movie not in selected:
            selected.append(movie)
    
    return selected


def create_watch_history(user_id: int, persona: Persona, all_movies: List[Dict]):
    """为用户生成浏览历史和收藏"""
    view_count = random.randint(*persona.view_count_range)
    movies = select_movies_for_user(persona, all_movies, view_count)
    
    history_records = []
    favorite_records = []
    
    for movie in movies:
        view_time = random_date(days_back=90)
        
        # 浏览历史
        history_records.append({
            'user_id': user_id,
            'movie_id': movie['id'],
            'watch_duration': random.randint(300, 7200),  # 5分钟到2小时
            'progress': random.uniform(0.1, 1.0),
            'interaction_score': random.randint(1, 10),
            'created_at': view_time
        })
        
        # 根据画像决定是否收藏
        if persona.should_like():
            favorite_records.append({
                'user_id': user_id,
                'movie_id': movie['id'],
                'is_liked': True,
                'created_at': view_time + timedelta(hours=random.randint(1, 48)),  # 收藏时间晚于浏览
            })
    
    return history_records, favorite_records


def batch_insert_history(records: List[Dict], table: str, batch_size: int = 100):
    """批量插入记录"""
    total = len(records)
    inserted = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                if table == 'user_watch_history':
                    for record in batch:
                        cur.execute("""
                            INSERT INTO user_watch_history 
                            (user_id, movie_id, watch_duration, progress, interaction_score, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            record['user_id'],
                            record['movie_id'],
                            record['watch_duration'],
                            record['progress'],
                            record['interaction_score'],
                            record['created_at']
                        ))
                elif table == 'user_favorites':
                    for record in batch:
                        cur.execute("""
                            INSERT INTO user_favorites 
                            (user_id, movie_id, is_liked, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            record['user_id'],
                            record['movie_id'],
                            record['is_liked'],
                            record['created_at'],
                            record['created_at']  # updated_at同created_at
                        ))
            conn.commit()
        
        inserted += len(batch)
        print(f"  {table}: {inserted}/{total} 条记录已插入...")
    
    return inserted


def clear_existing_mock_data():
    """清除现有的模拟数据（可选）"""
    print("\n🗑️ 清除现有的模拟数据...")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 删除模拟用户（用户名以user_开头）
            cur.execute("""
                DELETE FROM users 
                WHERE username LIKE 'user_%%' 
                AND created_at > NOW() - INTERVAL '1 day'
            """)
            deleted_users = cur.rowcount
            
            # 清除浏览历史（被删除用户的）
            cur.execute("DELETE FROM user_watch_history WHERE user_id NOT IN (SELECT id FROM users)")
            
            # 清除收藏
            cur.execute("DELETE FROM user_favorites WHERE user_id NOT IN (SELECT id FROM users)")
            
            conn.commit()
    
    print(f"  已删除 {deleted_users} 个模拟用户及相关数据")


def main():
    """主函数"""
    print("=" * 60)
    print("🎬 MovieAI Mock数据生成脚本")
    print("=" * 60)
    
    # 初始化数据库连接
    print("\n🔌 初始化数据库连接...")
    if not init_db():
        print("❌ 数据库连接失败！")
        return
    
    # 可选：清除旧数据
    if input("\n是否清除现有的模拟数据? (y/N): ").lower() == 'y':
        clear_existing_mock_data()
    
    # 获取电影数据
    all_movies = get_all_movies()
    if len(all_movies) < 50:
        print(f"❌ 电影数据不足（当前 {len(all_movies)} 部），请先运行电影数据导入脚本")
        return
    
    # 生成用户
    user_count = int(input(f"\n请输入要生成的模拟用户数量 (默认100): ") or "100")
    
    # 分配画像
    persona_distribution = {
        '科幻动作迷': 25,
        '文艺爱情控': 20,
        '惊悚恐怖迷': 15,
        '喜剧迷': 15,
        '杂食观众': 25
    }
    
    print("\n🎭 用户画像分布:")
    for name, count in persona_distribution.items():
        print(f"  - {name}: {count}%")
    
    # 创建用户并分配画像
    print(f"\n📝 开始生成 {user_count} 个用户及行为数据...")
    
    total_history = 0
    total_favorites = 0
    
    # 分批处理用户
    batch_size = 10
    for batch_start in range(0, user_count, batch_size):
        batch_end = min(batch_start + batch_size, user_count)
        batch_count = batch_end - batch_start
        
        # 创建用户
        user_ids = create_mock_users(batch_count)
        
        if not user_ids:
            print(f"  ❌ 批次 {batch_start}-{batch_end} 用户创建失败")
            continue
        
        # 为每个用户分配画像并生成数据
        for user_id in user_ids:
            # 随机分配画像
            persona = random.choices(PERSONAS, weights=[0.25, 0.20, 0.15, 0.15, 0.25])[0]
            
            # 生成浏览历史和收藏
            history, favorites = create_watch_history(user_id, persona, all_movies)
            
            # 批量插入
            batch_insert_history(history, 'user_watch_history')
            batch_insert_history(favorites, 'user_favorites')
            
            total_history += len(history)
            total_favorites += len(favorites)
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 数据生成完成！")
    print("=" * 60)
    print(f"  • 用户数量: {user_count}")
    print(f"  • 浏览历史: {total_history} 条")
    print(f"  • 收藏记录: {total_favorites} 条")
    print(f"  • 平均收藏率: {total_favorites/total_history*100:.1f}%" if total_history > 0 else "  • 平均收藏率: N/A")
    
    print("\n🎉 测试账号:")
    print("  用户名: user_test_1 (或其他以user_开头的用户名)")
    print("  密码: password123")
    
    # 关闭数据库连接
    close_db()
    
    print("\n✅ 脚本执行完成！")


if __name__ == "__main__":
    main()
