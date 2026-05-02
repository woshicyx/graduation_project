# 智能电影推荐平台 - 项目规格

## 1. 项目概述

本项目旨在构建一个融合 LLM、RAG（检索增强生成）技术与传统推荐算法的现代化电影推荐平台。系统支持自然语言智能搜索、个性化推荐和 AI 对话助手功能。

### 1.1 核心目标

- **RAG 智能推荐**: 基于向量数据库的自然语言电影检索和推荐
- **海量数据**: 8800+ 部电影完整信息
- **AI 对话**: 智能理解用户需求，返回带推荐理由的结果
- **可解释推荐**: 每部推荐电影都有AI生成的推荐理由
- **沉浸式UI**: 虚化电影背景、流畅轮播、得意黑字体

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
| 字体 | 得意黑 (Smiley Sans) | 全局字体 |

## 3. 功能模块

### 3.1 用户系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户注册 | ✅ | 邮箱 + 密码 |
| 用户登录 | ✅ | JWT Token |
| 用户信息 | ✅ | 基础信息展示 |
| 用户收藏 | ✅ | 收藏/取消收藏电影 |
| 浏览历史 | ✅ | 自动记录+手动删除 |

### 3.2 电影系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 电影列表 | ✅ | 分页展示 |
| 电影详情 | ✅ | 完整信息 + 海报 |
| 随机推荐 | ✅ | 随机 N 部高分电影 |
| 电影统计 | ✅ | 总数、评分、票房分布 |
| 电影浏览页 | ✅ | 布满电影的沉浸式界面 |

### 3.3 搜索系统

| 功能 | 状态 | 说明 |
|------|------|------|
| 关键字搜索 | ✅ | 标题、剧情、导演 |
| 混合搜索 | ✅ | 向量 + 结构化 |
| 多维度筛选 | ✅ | 类型、评分、年份标签 |

### 3.4 推荐系统

| 功能 | 状态 | 说明 |
|------|------|------|
| RAG 语义推荐 | ✅ | 自然语言查询 |
| AI 推荐理由 | ✅ | LLM 生成可解释理由 |
| 协同过滤推荐 | ✅ | 基于用户相似度的"猜你喜欢" |
| Top50 轮播 | ✅ | 票房/评分/热度自动轮换 |

### 3.5 AI 对话助手

| 功能 | 状态 | 说明 |
|------|------|------|
| 对话页面 | ✅ | Next.js 页面 |
| 流式输出 | ✅ | 智谱AI 流式 |
| 可解释推荐 | ✅ | 每部电影附带推荐理由 |
| Top5 精简推荐 | ✅ | 重排后只返回5部 |

## 4. 页面规划

```
/
├── 首页 (/)
│   ├── 搜索栏
│   ├── 虚化电影背景
│   ├── 猜你喜欢 (协同过滤)
│   ├── 票房排行榜 (Top50轮播)
│   ├── 评分排行榜 (Top50轮播)
│   ├── 热门电影 (Top50轮播)
│   └── 底部设计
│
├── 电影浏览 (/movies)
│   ├── 虚化电影背景
│   ├── 网格展示
│   ├── 类型/评分/年份筛选
│   └── 无限滚动
│
├── 搜索结果 (/search)
│   ├── 侧边栏筛选
│   └── 电影网格
│
├── 电影详情 (/movies/[id])
│   ├── 海报 + 基本信息
│   ├── 剧情简介
│   ├── 相似电影
│   └── 收藏/观看按钮
│
├── AI 对话 (/chat)
│   ├── 对话历史
│   └── 推荐卡片 + 理由
│
├── 个人中心 (/profile)
│   ├── 用户信息
│   ├── 收藏列表 (/favorites)
│   └── 浏览历史 (/history)
│
└── 认证 (/auth)
    ├── 登录
    └── 注册
```

## 5. UI设计规范

### 5.1 主题配色
| 用途 | 色值 |
|------|------|
| 背景 | `#0a0a0f` (深黑) |
| 主色调 | `#dc2626` (红色-600) |
| 强调色 | `#f97316` (橙色) |
| 文字 | `#ffffff` (白色) / `#ffffffb3` (70%透明度) |
| 边框 | `rgba(255,255,255,0.1)` (10%透明度) |

### 5.2 背景效果
- **主页/电影页**: 布满虚化电影海报作为背景
- **玻璃拟态**: `backdrop-blur-xl` + 半透明卡片
- **渐变光晕**: 红色/橙色渐变光晕点缀

### 5.3 字体
- **全局字体**: 得意黑 (Smiley Sans)
- **备用字体**: system-ui, sans-serif

### 5.4 轮播功能
- **Top50轮播**: 票房/评分/热度模块各显示Top50
- **随机展示**: 每次进入随机抽取10部
- **自动轮换**: 每5秒自动切换一组

## 6. API 设计

### 6.1 认证 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |

### 6.2 电影 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/movies` | GET | 电影列表 |
| `/api/movies/{id}` | GET | 电影详情 |
| `/api/movies/random` | GET | 随机推荐 |
| `/api/movies/top-rated` | GET | 评分Top50 |
| `/api/movies/top-popular` | GET | 热门Top50 |
| `/api/movies/top-box-office` | GET | 票房Top50 |
| `/api/movies/stats/summary` | GET | 统计信息 |

### 6.3 搜索与推荐 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search` | GET | 混合搜索 |
| `/api/recommend` | POST | AI智能推荐(带理由,Top5) |

### 6.4 个性化 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/personalized` | GET | 协同过滤推荐 |
| `/api/users/me/favorites` | GET/POST | 收藏列表/添加 |
| `/api/users/me/watch-history` | GET/POST | 浏览历史 |

## 7. 数据库设计

### 7.1 movies 表

```sql
id, title, overview, tagline, budget, revenue, popularity
release_date, runtime, vote_average, vote_count
genres, keywords, director, rag_text
```

### 7.2 users 表

```sql
id, username, email, password_hash, display_name, role
is_active, is_verified, preferences, created_at
```

### 7.3 user_favorites 表

```sql
id, user_id, movie_id, is_liked, notes, tags, created_at, updated_at
```

### 7.4 user_watch_history 表

```sql
id, user_id, movie_id, watch_duration, progress, interaction_score, created_at
```

## 8. 开发进度

### 已完成 ✅

- [x] 项目结构重构
- [x] 用户认证系统
- [x] 电影浏览和详情
- [x] RAG 向量索引 (7995 条)
- [x] AI 智能推荐 API
- [x] 个人中心页面
- [x] 用户收藏功能
- [x] 浏览历史功能
- [x] 协同过滤推荐算法
- [x] 主页"猜你喜欢"模块
- [x] 得意黑字体配置
- [x] 虚化电影背景
- [x] Top50轮播功能
- [x] 首页底部设计

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
| 后端 API | 8000 |
| Qdrant Dashboard | 6333 |

## 10. 数据统计

| 指标 | 数值 |
|------|------|
| 电影总数 | 8856 |
| 有 rag_text | 8634 |
| Qdrant 向量 | 7995 |
| 向量维度 | 1024 |
