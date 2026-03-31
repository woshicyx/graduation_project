# 智能电影推荐平台 - 数据库架构设计

## 1. 数据源：TMDB 5000 数据集

### 数据集组成
- **tmdb_5000_movies.csv** - 电影核心信息 (4803部电影)
  - id: 电影唯一ID (INT, 主键)
  - title: 电影标题 (VARCHAR)
  - original_title: 原始标题 (VARCHAR)
  - overview: 剧情简介 (TEXT)
  - budget: 制作预算 (BIGINT, 美元)
  - revenue: 票房收入 (BIGINT, 美元)
  - genres: 类型列表 (JSON数组)
  - original_language: 原始语言 (VARCHAR)
  - popularity: 流行度 (FLOAT)
  - release_date: 上映日期 (DATE)
  - runtime: 片长 (INT, 分钟)
  - vote_average: 平均评分 (FLOAT)
  - vote_count: 评分人数 (INT)
  - poster_path: 海报路径 (VARCHAR)
  - homepage: 官方主页 (VARCHAR)
  - status: 发行状态 (VARCHAR)
  - tagline: 宣传语 (TEXT)

- **tmdb_5000_credits.csv** - 演职员信息
  - movie_id: 关联电影ID (INT, 外键)
  - title: 电影标题 (VARCHAR)
  - cast: 演员列表 (JSON数组)
  - crew: 制作人员列表 (JSON数组)

## 2. 数据库架构 (PostgreSQL)

### 2.1 核心表设计

#### movies 表 (电影核心信息)
```sql
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
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
    genres TEXT,  -- 存储为JSON字符串: ["Action", "Adventure", "Sci-Fi"]
    director VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 索引设计
```sql
-- 性能优化索引
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_vote_average ON movies(vote_average);
CREATE INDEX idx_movies_popularity ON movies(popularity);
CREATE INDEX idx_movies_revenue ON movies(revenue);
```

### 2.2 扩展表设计 (可选)

#### genres 表 (电影类型)
```sql
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
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
    id INTEGER PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
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
    id INTEGER PRIMARY KEY,
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

## 3. 数据导入流程
1. **下载数据集**: `python backend/scripts/download_tmdb_data.py`
   - 从GitHub下载TMDB 5000数据集
   - 验证数据完整性
   - 创建示例数据（如下载失败）

2. **数据库设置**: `python backend/scripts/setup_database.py`
   - 检查PostgreSQL安装
   - 创建数据库和用户
   - 安装Python依赖

3. **数据导入**: `python backend/scripts/import_tmdb_to_db.py`
   - 创建数据库架构
   - 解析CSV文件
   - 批量导入数据
   - 数据质量验证


## 4. 查询优化策略

### 4.1 常用查询模式
```sql
-- 按评分排序
SELECT * FROM movies 
WHERE vote_average > 7.0 
ORDER BY vote_average DESC 
LIMIT 20;

-- 按票房排序
SELECT * FROM movies 
WHERE revenue > 100000000 
ORDER BY revenue DESC 
LIMIT 20;

-- 按类型筛选
SELECT * FROM movies 
WHERE genres LIKE '%"Action"%' 
ORDER BY popularity DESC 
LIMIT 20;

-- 按导演筛选
SELECT * FROM movies 
WHERE director LIKE '%Nolan%' 
ORDER BY release_date DESC;

-- 综合搜索
SELECT * FROM movies 
WHERE title ILIKE '%star%' 
   OR overview ILIKE '%space%' 
ORDER BY popularity DESC 
LIMIT 20;
```

### 4.2 性能优化
- **索引策略**: 为常用查询字段创建索引
- **查询优化**: 使用EXPLAIN ANALYZE分析查询计划
- **连接优化**: 合理使用JOIN和子查询
- **分页优化**: 使用OFFSET/LIMIT进行分页

## 5. 向量数据库集成 (pgvector)

### 5.1 向量化存储
```sql
-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建电影向量表
CREATE TABLE movie_vectors (
    movie_id INTEGER PRIMARY KEY REFERENCES movies(id),
    embedding vector(1536),  -- OpenAI text-embedding-3-small维度
    text_content TEXT,       -- 用于生成向量的文本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建向量索引
CREATE INDEX idx_movie_vectors_embedding 
ON movie_vectors 
USING ivfflat (embedding vector_cosine_ops);
```

### 5.2 语义搜索
```sql
-- 语义相似度搜索
SELECT m.*, 
       1 - (mv.embedding <=> '[0.1, 0.2, ...]') as similarity
FROM movies m
JOIN movie_vectors mv ON m.id = mv.movie_id
ORDER BY mv.embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

## 6. 数据统计与分析
- 电影总数: ~4,800部
- 平均评分分布: 0-10分
- 票房分布: 0-2.7亿美元
- 类型分布: 20+种电影类型
- 时间跨度: 1916年至今
