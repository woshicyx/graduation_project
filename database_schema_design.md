# 智能电影推荐平台 - 数据库架构设计 (增强版)

## 1. 数据源：TMDB 5000 数据集

### 数据集组成
- **tmdb_5000_movies.csv** - 电影核心信息 (4803部电影)
- **tmdb_5000_credits.csv** - 演职员信息

## 2. 数据库架构设计原则

### 2.1 设计目标
1. **性能优化**: 支持快速查询和推荐
2. **数据完整性**: 保持数据关系和一致性
3. **扩展性**: 支持未来功能扩展
4. **查询效率**: 优化常用查询模式

### 2.2 架构选择
- **主数据库**: PostgreSQL (关系型数据)
- **向量数据库**: pgvector (语义搜索和推荐)
- **缓存层**: Redis (可选，用于热门数据缓存)

## 3. 核心表设计

### 3.1 movies 表 (电影核心信息)
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
    homepage VARCHAR(500),
    status VARCHAR(50),
    original_language VARCHAR(10),
    genres TEXT,  -- 存储为JSON字符串: ["Action", "Adventure", "Sci-Fi"]
    keywords TEXT, -- 存储为JSON字符串
    production_companies TEXT, -- 存储为JSON字符串
    production_countries TEXT, -- 存储为JSON字符串
    spoken_languages TEXT, -- 存储为JSON字符串
    director VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 扩展表设计 (规范化)

#### genres 表 (电影类型)
```sql
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### movie_genres 表 (电影-类型关联)
```sql
CREATE TABLE movie_genres (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);
```

#### actors 表 (演员)
```sql
CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    gender INTEGER, -- 0:未知, 1:女性, 2:男性
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### movie_actors 表 (电影-演员关联)
```sql
CREATE TABLE movie_actors (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    actor_id INTEGER REFERENCES actors(id) ON DELETE CASCADE,
    character VARCHAR(500),
    cast_order INTEGER,
    PRIMARY KEY (movie_id, actor_id, character)
);
```

#### directors 表 (导演)
```sql
CREATE TABLE directors (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### movie_directors 表 (电影-导演关联)
```sql
CREATE TABLE movie_directors (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    director_id INTEGER REFERENCES directors(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, director_id)
);
```

### 3.3 用户相关表 (为推荐系统准备)

#### users 表 (用户)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferences JSONB, -- 用户偏好设置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_ratings 表 (用户评分)
```sql
CREATE TABLE user_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    rating FLOAT CHECK (rating >= 0 AND rating <= 10),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);
```

#### user_watch_history 表 (用户观看历史)
```sql
CREATE TABLE user_watch_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    watch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watch_duration INTEGER, -- 观看时长(秒)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. 索引设计

### 4.1 性能优化索引
```sql
-- movies表索引
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_vote_average ON movies(vote_average);
CREATE INDEX idx_movies_popularity ON movies(popularity);
CREATE INDEX idx_movies_revenue ON movies(revenue);
CREATE INDEX idx_movies_runtime ON movies(runtime);
CREATE INDEX idx_movies_vote_count ON movies(vote_count);

-- 复合索引
CREATE INDEX idx_movies_genre_search ON movies USING gin(genres);
CREATE INDEX idx_movies_date_popularity ON movies(release_date DESC, popularity DESC);

-- 关联表索引
CREATE INDEX idx_movie_genres_movie_id ON movie_genres(movie_id);
CREATE INDEX idx_movie_genres_genre_id ON movie_genres(genre_id);
CREATE INDEX idx_movie_actors_movie_id ON movie_actors(movie_id);
CREATE INDEX idx_movie_actors_actor_id ON movie_actors(actor_id);
CREATE INDEX idx_movie_directors_movie_id ON movie_directors(movie_id);
CREATE INDEX idx_movie_directors_director_id ON movie_directors(director_id);

-- 用户相关索引
CREATE INDEX idx_user_ratings_user_id ON user_ratings(user_id);
CREATE INDEX idx_user_ratings_movie_id ON user_ratings(movie_id);
CREATE INDEX idx_user_ratings_rating ON user_ratings(rating);
CREATE INDEX idx_user_watch_history_user_id ON user_watch_history(user_id);
CREATE INDEX idx_user_watch_history_movie_id ON user_watch_history(movie_id);
```

## 5. 向量数据库集成 (pgvector)

### 5.1 启用pgvector扩展
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5.2 电影向量表
```sql
CREATE TABLE movie_vectors (
    movie_id INTEGER PRIMARY KEY REFERENCES movies(id),
    embedding vector(1536),  -- OpenAI text-embedding-3-small维度
    text_content TEXT,       -- 用于生成向量的文本(标题+简介+标签)
    embedding_type VARCHAR(50) DEFAULT 'openai',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建向量索引
CREATE INDEX idx_movie_vectors_embedding 
ON movie_vectors 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 5.3 用户偏好向量
```sql
CREATE TABLE user_preference_vectors (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    embedding vector(1536),  -- 用户偏好向量
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 6. 数据导入策略

### 6.1 分阶段导入
1. **阶段1**: 导入核心电影数据到movies表
2. **阶段2**: 解析并导入规范化数据(类型、演员、导演)
3. **阶段3**: 生成向量嵌入
4. **阶段4**: 创建索引和优化

### 6.2 数据质量保证
- 数据验证和清洗
- 重复数据检测
- 缺失值处理
- 数据类型转换

## 7. 查询优化策略

### 7.1 常用查询模式
```sql
-- 1. 按评分排序
SELECT * FROM movies 
WHERE vote_average > 7.0 
ORDER BY vote_average DESC 
LIMIT 20;

-- 2. 按票房排序
SELECT * FROM movies 
WHERE revenue > 100000000 
ORDER BY revenue DESC 
LIMIT 20;

-- 3. 按类型筛选
SELECT m.* FROM movies m
JOIN movie_genres mg ON m.id = mg.movie_id
JOIN genres g ON mg.genre_id = g.id
WHERE g.name = 'Action'
ORDER BY m.popularity DESC 
LIMIT 20;

-- 4. 按导演筛选
SELECT m.* FROM movies m
JOIN movie_directors md ON m.id = md.movie_id
JOIN directors d ON md.director_id = d.id
WHERE d.name LIKE '%Nolan%'
ORDER BY m.release_date DESC;

-- 5. 语义搜索
SELECT m.*, 
       1 - (mv.embedding <=> '[0.1, 0.2, ...]') as similarity
FROM movies m
JOIN movie_vectors mv ON m.id = mv.movie_id
ORDER BY mv.embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

### 7.2 性能监控
- 使用EXPLAIN ANALYZE分析查询计划
- 监控慢查询日志
- 定期更新统计信息
- 索引维护和优化

## 8. 数据库维护

### 8.1 定期维护任务
```sql
-- 更新统计信息
ANALYZE movies;
ANALYZE genres;
ANALYZE actors;
ANALYZE directors;

-- 重建索引
REINDEX TABLE movies;
REINDEX TABLE movie_vectors;

-- 清理旧数据
VACUUM ANALYZE;
```

### 8.2 备份策略
- 每日全量备份
- 实时WAL日志备份
- 定期测试恢复流程

## 9. 安全考虑

### 9.1 访问控制
- 最小权限原则
- 角色分离
- 连接限制

### 9.2 数据加密
- 传输层加密(SSL/TLS)
- 敏感数据加密存储
- 密码哈希存储

## 10. 扩展性设计

### 10.1 读写分离
- 主库负责写操作
- 从库负责读操作
- 自动故障转移

### 10.2 分片策略
- 按电影ID范围分片
- 按用户ID哈希分片
- 跨分片查询优化

---

## 实施步骤

1. **环境准备**: 安装PostgreSQL和pgvector扩展
2. **数据库创建**: 创建数据库和用户
3. **架构部署**: 执行上述SQL创建表结构
4. **数据导入**: 使用Python脚本导入TMDB数据
5. **索引创建**: 创建所有必要的索引
6. **向量生成**: 生成电影向量嵌入
7. **性能测试**: 测试查询性能并进行优化
8. **监控部署**: 设置数据库监控和告警

这个增强版数据库架构为智能电影推荐平台提供了坚实的基础，支持复杂的查询、语义搜索和个性化推荐功能。