# 智能电影推荐平台 - 项目规格

## 1. 项目概述

本项目旨在构建一个融合 LLM、RAG（检索增强生成）技术与传统推荐算法的现代化电影推荐平台。系统支持自然语言智能搜索、个性化推荐和 AI 对话助手功能。

### 1.1 核心目标

- **RAG 智能推荐**: 基于向量数据库的自然语言电影检索和推荐
- **海量数据**: 8800+ 部电影完整信息
- **AI 对话**: 智能理解用户需求，返回带推荐理由的结果

## 2. 技术栈

| 组件 | 技术 | 版本/说明 |
|------|------|----------|
| 前端框架 | Next.js 14 | App Router, TypeScript |
| UI 样式 | Tailwind CSS | Shadcn/UI 组件库 |
| 后端框架 | FastAPI | Python 3.11+ |
| 关系数据库 | PostgreSQL | 电影、用户、影评数据 |
| 向量数据库 | Qdrant Cloud | 7995 个语义向量 |
| AI Embedding | 智谱AI | embedding-2 (1024维) |
| 认证 | JWT | bcrypt 密码哈希 |

## 3. 功能模块

### 3.1 用户系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册 | ✅ | 邮箱 + 密码 |
| 用户登录 | ✅ | JWT Token |
| 用户信息 | ✅ | 基础信息展示 |

### 3.2 电影系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 电影列表 | ✅ | 分页展示 |
| 电影详情 | ✅ | 完整信息 + 海报 |
| 随机推荐 | ✅ | 随机 N 部高分电影 |
| 电影统计 | ✅ | 总数、评分、票房分布 |

### 3.3 搜索系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 关键字搜索 | ✅ | 标题、剧情、导演 |
| 混合搜索 | ✅ | 向量 + 结构化 |

### 3.4 推荐系统

| 功能 | 状态 | 说明 |
|------|------|------|
| RAG 语义推荐 | ✅ | 自然语言查询 |
| AI 推荐理由 | 🔄 | LLM 生成说明 |

### 3.5 影评系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 发布影评 | ✅ | 评分 + 内容 |
| 影评列表 | ✅ | 支持排序 |
| 影评投票 | ✅ | 有帮助/无帮助 |

### 3.6 AI 对话助手

| 功能 | 状态 | 说明 |
|------|------|------|
| 对话页面 | ✅ | Next.js 页面 |
| 流式输出 | 🔄 | 智谱AI 流式 |

## 4. 页面规划

```
/
├── 首页 (/)
│   ├── 搜索栏
│   ├── 热门电影轮播
│   └── 票房排行榜
|   |__ 评分排行榜
│
├── 搜索结果 (/search)
│   ├── 侧边栏筛选
│   └── 电影网格
│
├── 电影详情 (/movies/[id])
│   ├── 海报 + 基本信息
│   ├── 剧情简介
│   ├── 相似电影
│   └── 影评区
│
├── AI 对话 (/chat)
│   ├── 对话历史
│   └── 推荐卡片
│
├── 个人中心 (/profile)
│   └── 用户信息
│
└── 认证 (/auth)
    ├── 登录
    └── 注册
```

## 5. API 设计

### 5.1 认证 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |

### 5.2 电影 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/movies` | GET | 电影列表 |
| `/api/movies/{id}` | GET | 电影详情 |
| `/api/movies/random` | GET | 随机推荐 |
| `/api/movies/stats/summary` | GET | 统计信息 |

### 5.3 搜索与推荐 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search` | GET | 混合搜索 |
| `/api/recommend` | POST | AI 智能推荐 |

### 5.4 影评 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/reviews` | GET/POST | 影评列表/发布 |
| `/api/reviews/{id}/vote` | POST | 投票 |
| `/api/reviews/stats/{movie_id}` | GET | 统计 |

### 5.5 用户 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/user/profile` | GET | 用户信息 |

## 6. 数据库设计

### 6.1 movies 表

```sql
-- 核心电影信息
id, title, overview, tagline, budget, revenue, popularity
release_date, runtime, vote_average, vote_count
genres, keywords, director, rag_text
```

### 6.2 users 表

```sql
-- 用户信息
id, username, email, password_hash
```

### 6.3 reviews 表

```sql
-- 影评
id, user_id, movie_id, rating, title, content
helpful_count, unhelpful_count
```

### 6.4 review_votes 表

```sql
-- 影评投票
id, user_id, review_id, is_helpful
```

## 7. 向量检索设计

### 7.1 Qdrant Collection

```python
collection_name = "movie_semantic"
vector_size = 1024
distance = "Cosine"
```

### 7.2 rag_text 模板

```text
Title: {title}
Overview: {overview}
Genres: {genres}
Director: {director}
Rating: {vote_average}
```

### 7.3 推荐公式

```text
final_score = 0.70 × vector_score + 0.20 × rating_score + 0.10 × popularity_score
```

## 8. 开发进度

### 已完成 ✅

- [x] 项目结构重构
- [x] 用户认证系统
- [x] 电影浏览和详情
- [x] RAG 向量索引 (7995 条)
- [x] AI 智能推荐 API
- [x] 影评系统
- [x] AI 对话页面
- [x] 个人中心页面

### 开发中 🔄

- [ ] 个性化推荐 (协同过滤)
- [ ] 用户收藏功能
- [ ] 浏览历史记录
- [ ] LLM 推荐理由生成

### 待开发 📋

- [ ] 管理后台
- [ ] 用户行为分析
- [ ] 推荐系统优化

## 9. 环境配置

### 开发环境

```bash
# 后端
DB_HOST=localhost
DB_PORT=5432
DB_NAME=movie_recommendation
DB_USER=postgres
DB_PASSWORD=xxx

# Qdrant
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=xxx

# 智谱AI
ZHIPUAI_API_KEY=xxx
```

### 端口配置

| 服务 | 端口 |
|------|------|
| 前端 | 3000 |
| 后端 API | 8015 |
| Qdrant Dashboard | 6333 |

## 10. 数据统计

| 指标 | 数值 |
|------|------|
| 电影总数 | 8856 |
| 有 rag_text | 8634 |
| Qdrant 向量 | 7995 |
| 向量维度 | 1024 |
