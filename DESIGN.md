# 智能电影推荐平台 - 系统设计

## 1. 系统架构

### 1.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Next.js 14 | App Router, TypeScript, Tailwind CSS |
| 后端 | FastAPI | Python 3.11+, 异步 API |
| 数据库 | PostgreSQL | 电影数据、用户数据、影评数据 |
| 向量库 | Qdrant Cloud | 7995 个电影语义向量 |
| AI | 智谱AI | embedding-2 (1024维) |

### 1.2 架构图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端      │────▶│   FastAPI   │────▶│ PostgreSQL  │
│  Next.js    │◀────│   Backend   │◀────│  数据库      │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Qdrant    │
                    │  向量数据库   │
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   智谱AI    │
                    │  Embedding  │
                    └─────────────┘
```

## 2. 数据库架构 (PostgreSQL)

### 2.1 movies 表 (电影核心信息)

```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    overview TEXT,
    tagline TEXT,
    budget BIGINT,
    revenue BIGINT,
    popularity FLOAT,
    release_date DATE,
    runtime INTEGER,
    vote_average FLOAT,
    vote_count INTEGER,
    poster_path VARCHAR(500),
    status VARCHAR(50),
    original_language VARCHAR(10),
    genres TEXT,           -- JSON 字符串
    keywords TEXT,         -- JSON 字符串
    production_companies TEXT,
    production_countries TEXT,
    spoken_languages TEXT,
    director VARCHAR(500),
    rag_text TEXT,         -- RAG 检索文本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 性能索引
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_vote_average ON movies(vote_average);
CREATE INDEX idx_movies_popularity ON movies(popularity);
CREATE INDEX idx_movies_rag_text ON movies(rag_text) WHERE rag_text IS NOT NULL;
```

### 2.2 users 表 (用户信息)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 reviews 表 (影评)

```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    movie_id INTEGER REFERENCES movies(id),
    rating FLOAT NOT NULL CHECK (rating >= 1 AND rating <= 10),
    title VARCHAR(255),
    content TEXT,
    helpful_count INTEGER DEFAULT 0,
    unhelpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 review_votes 表 (影评投票)

```sql
CREATE TABLE review_votes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    review_id INTEGER REFERENCES reviews(id),
    is_helpful BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, review_id)
);
```

## 3. 向量数据库 (Qdrant)

### 3.1 Collection 配置

```python
collection_name = "movie_semantic"
vector_size = 1024  # embedding-2 维度
distance = "Cosine"
```

### 3.2 Point 结构

```json
{
  "id": 680,
  "vector": [0.123, ...],  // 1024 维
  "payload": {
    "movie_id": 680,
    "title": "Inception",
    "genres": ["Action", "Sci-Fi"],
    "director": "Christopher Nolan",
    "vote_average": 8.4,
    "popularity": 220.3
  }
}
```

### 3.3 rag_text 模板

```text
Title: Inception
Original title: Inception
Overview: A thief who steals corporate secrets through dream-sharing technology...
Tagline: Your mind is the scene of the crime.
Genres: Action, Science Fiction, Adventure
Keywords: dream, subconscious, heist
Director: Christopher Nolan
Original language: en
Release year: 2010
Runtime: 148 minutes
Vote average: 8.4
```

## 4. API 设计

### 4.1 RESTful API

```
/api
├── /health              GET    健康检查
├── /auth
│   ├── /register       POST   用户注册
│   └── /login          POST   用户登录
├── /movies
│   ├── /{id}           GET    电影详情
│   ├── /random         GET    随机推荐
│   └── /stats/summary  GET    统计信息
├── /search             GET    混合搜索
├── /recommend          POST   AI 智能推荐
├── /reviews
│   ├── /{id}/vote      POST   影评投票
│   └── /stats/{movie_id} GET  影评统计
├── /user
│   └── /profile        GET    用户信息
```

### 4.2 响应格式

```json
// 成功响应
{
  "data": {...},
  "message": "success"
}

// 错误响应
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

## 5. RAG 推荐流程

### 5.1 离线索引

```
PostgreSQL (movies) → rag_text 生成 → 智谱AI Embedding → Qdrant upsert
```

### 5.2 在线推荐

```
用户查询 → 智谱AI Embedding → Qdrant 语义检索 → PostgreSQL 元数据
    → 混合排序 (0.7*语义 + 0.2*评分 + 0.1*热度) → 智谱AI LLM → 推荐结果
```

## 6. 安全设计

### 6.1 认证

- JWT Token 认证
- Token 有效期: 24 小时
- 密码 bcrypt 哈希存储

### 6.2 CORS

```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # 开发环境
]
```

### 6.3 速率限制

- 开发环境: 无限制
- 生产环境: 100 请求/15分钟

## 7. 性能优化

### 7.1 数据库

- 连接池: 1-10 个连接
- 索引优化: 查询字段索引
- 分页: 默认 20 条/页

### 7.2 向量检索

- Qdrant HNSW 索引
- top-k 召回: 10-20 个

### 7.3 前端

- 图片懒加载
- API 响应缓存
- 代码分割

## 8. 环境配置

| 环境 | 数据库 | Qdrant |
|------|--------|--------|
| 开发 | localhost:5432 | localhost:6333 |
| 生产 | 云端 PostgreSQL | Qdrant Cloud |

## 9. 数据统计

| 指标 | 数值 |
|------|------|
| 电影总数 | 8856 |
| 有 rag_text | 8634 |
| Qdrant 向量 | 7995 |
| 向量维度 | 1024 |
