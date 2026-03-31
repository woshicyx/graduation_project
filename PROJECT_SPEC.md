# 项目名称：智能电影推荐平台

## 1. 项目概述
构建一个融合了 LLM 与 RAG 技术的电影推荐网站。结合传统结构化数据检索与非结构化语义检索，提供精美的 UI 体验和智能对话推荐。

## 2. 技术栈推荐
- **前端**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/UI (用于精美组件), Framer Motion (动画).
- **后端**: Python FastAPI (处理 AI 逻辑与 RAG) 或 Next.js API Routes.
- **数据库**: 
  - 关系型：PostgreSQL (存储电影元数据：标题、导演、票房、评分等).
  - 向量库：Qdrant 或 Pinecone (存储电影剧情、影评的 Embedding).
- **AI/LLM**: OpenAI API (或兼容接口), LangChain / LlamaIndex (RAG 流程).
- **数据源**: TMDB API 或 爬虫采集 (用于初始化数据).

## 3. 核心功能模块
### 3.1 搜索系统 (Hybrid Search)
- 支持字段：电影名、类型、导演、评分范围、票房范围、上映时间。
- 实现：Elasticsearch 或 PostgreSQL 全文检索 + 向量相似度搜索。

### 3.2 推荐系统
- **传统推荐**: 基于 SQL 查询 (Top 50 票房，Top 50 评分，实时热度)。
- **AI 推荐**: 基于用户对话意图，通过 RAG 检索数据库，由 LLM 生成推荐列表及理由。

### 3.3 电影详情页
- 展示：海报、基本信息、剧情简介、预告片。
- 数据：5-10 条精选影评（用于 RAG 检索源）。

### 3.4 AI 智能助手
- 界面：悬浮按钮或独立页面。
- 功能：多轮对话，理解用户模糊需求（如“我想看一部类似《星际穿越》的烧脑电影”），返回推荐卡片。

## 4. 页面规划
1. **Home**: 大搜索栏（带标签筛选）、推荐轮播、榜单入口（票房/评分）。
2. **Search Result**: 筛选侧边栏、电影网格列表。
3. **Movie Detail**: 详细信息、影评区、"猜你喜欢"。
4. **AI Chat**: 对话界面，支持点击推荐电影直接跳转详情。

## 5. 数据流程 (RAG Pipeline)
1. 采集电影元数据 + 剧情简介 + 影评。
2. 清洗数据，文本分块 (Chunking)。
3. 调用 Embedding 模型生成向量，存入向量库。
4. 用户 Query -> Embedding -> 向量检索 -> 召回 Top K 电影 -> LLM 生成最终回答。