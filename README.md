# 🎬 智能电影推荐平台

基于 **FastAPI + Next.js + PostgreSQL + Qdrant** 的智能电影推荐系统，集成 RAG（检索增强生成）技术，支持自然语言智能推荐。

## ✨ 项目特点

- **RAG 智能推荐**: 基于向量数据库的自然语言电影搜索和推荐
- **现代化前端**: Next.js 14 + TypeScript + Tailwind CSS
- **高性能 API**: FastAPI 异步 RESTful API
- **海量数据**: 8800+ 部电影完整信息，Qdrant 向量库 7995 个语义向量
- **AI 对话助手**: 智能理解用户需求，返回带推荐理由的个性化结果

## 📁 项目结构

```
MovieAI/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/           # API 路由模块化
│   │   │   ├── auth.py       # 认证 API
│   │   │   ├── health.py     # 健康检查
│   │   │   ├── movies_tmdb.py # 电影 API
│   │   │   ├── recommend.py  # 推荐 API
│   │   │   ├── reviews.py    # 影评 API
│   │   │   ├── search.py     # 搜索 API
│   │   │   └── user.py       # 用户 API
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic 模型
│   │   ├── services/         # 业务服务
│   │   │   └── rag_service.py # RAG 服务
│   │   └── main.py           # FastAPI 应用
│   ├── qdrant_storage/       # 本地 Qdrant 数据
│   └── requirements.txt       # Python 依赖
├── frontend/                  # Next.js 前端
│   ├── app/
│   │   ├── auth/            # 认证页面
│   │   ├── chat/            # AI 对话助手
│   │   ├── movies/[id]/     # 电影详情页
│   │   ├── profile/         # 个人中心
│   │   └── search/          # 搜索结果页
│   ├── components/          # React 组件
│   ├── hooks/              # React Hooks
│   ├── lib/api/            # API 客户端
│   └── types/              # TypeScript 类型
├── .env.example            # 环境变量示例
├── DESIGN.md               # 数据库架构设计
├── PROJECT_SPEC.md         # 项目规格说明
└── RAG_PLAN.md             # RAG 技术方案
```

## 🚀 快速开始

### 后端启动

```powershell
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8015 --reload
```

### 前端启动

```powershell
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8015 |
| API 文档 | http://localhost:8015/docs |
| Qdrant Dashboard | http://localhost:6333 |

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 电影总数 | 8856 |
| 有 RAG 文本 | 8634 |
| Qdrant 向量 | 7995 |
| 向量维度 | 1024 (embedding-2) |

## 🔧 技术栈

### 后端
- **框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + pgvector
- **向量库**: Qdrant Cloud
- **AI**: LangChain + 智谱AI (embedding-2)

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS + Shadcn/UI
- **状态管理**: React Context

## 🔌 API 接口

### 电影 API
- `GET /api/movies` - 电影列表
- `GET /api/movies/{id}` - 电影详情
- `GET /api/movies/random` - 随机推荐
- `GET /api/movies/stats/summary` - 统计信息

### 搜索与推荐
- `GET /api/search` - 混合搜索
- `POST /api/recommend` - AI 智能推荐

### 用户与认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/user/profile` - 获取用户信息

### 影评系统
- `GET /api/reviews` - 影评列表
- `POST /api/reviews` - 发布影评
- `POST /api/reviews/{id}/vote` - 影评投票

## 🔮 RAG 推荐流程

```
用户查询 -> 向量化 -> Qdrant 语义检索 -> PostgreSQL 元数据 -> 混合排序 -> LLM 生成推荐理由
```

## 📝 环境变量

```bash
# 数据库
DB_HOST=localhost
DB_PORT=5432
DB_NAME=movie_recommendation
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256

# Qdrant
QDRANT_URL=https://your-qdrant-cloud.io
QDRANT_API_KEY=your_api_key

# 智谱AI
ZHIPUAI_API_KEY=your_api_key
EMBEDDING_MODEL=embedding-2
EMBEDDING_DIMENSION=1024
```

## 📚 文档

- [设计文档](DESIGN.md) - 数据库架构和系统设计
- [项目规格](PROJECT_SPEC.md) - 功能模块和技术选型
- [RAG 方案](RAG_PLAN.md) - 向量检索和推荐技术方案

## 🎯 功能模块

### 已实现
- ✅ 用户注册/登录
- ✅ 电影浏览和搜索
- ✅ 电影详情页
- ✅ AI 智能推荐 (RAG)
- ✅ AI 对话助手
- ✅ 个人中心
- ✅ 影评系统

### 开发中
- 🔄 个性化推荐 (协同过滤)
- 🔄 用户收藏和浏览历史
- 🔄 管理后台

## 📄 许可证

MIT License
