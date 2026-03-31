# 智能电影推荐平台 - 后端（FastAPI）

基于 FastAPI 的后端服务，负责电影元数据查询、Hybrid Search（结构化过滤 + 语义检索）以及基于 LLM + RAG 的 AI 推荐。

## 目录结构

```
backend/
├── app/
│   ├── api/
│   │   ├── health.py          # /health 健康检查
│   │   ├── movies.py          # /api/movies* 电影列表、榜单、详情
│   │   ├── search.py          # /api/search/hybrid 混合搜索
│   │   └── recommend.py       # /api/ai/recommend AI 推荐
│   ├── core/
│   │   ├── config.py          # 配置 & 环境变量（pydantic-settings）
│   │   ├── db.py              # PostgreSQL 异步连接（SQLAlchemy + asyncpg）
│   │   └── vector.py          # Qdrant 向量库客户端
│   ├── models.py              # SQLAlchemy ORM 模型（movies / reviews）
│   ├── schemas.py             # Pydantic schema（API 入参与返回体）
│   └── main.py                # FastAPI 入口，注册路由与中间件
└── requirements.txt           # 后端 Python 依赖
```

## 安装依赖

建议在项目根目录使用虚拟环境：

```bash
cd d:\projects\graduation_project
python -m venv .venv
.venv\Scripts\activate

pip install -r backend/requirements.txt
```

## 启动开发服务器

```bash
cd d:\projects\graduation_project
.venv\Scripts\activate

uvicorn app.main:app --reload --app-dir backend
```

默认监听 `http://127.0.0.1:8000`，可访问：

- 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

前端可以将 `NEXT_PUBLIC_API_URL` 指向 `http://127.0.0.1:8000/api`。

