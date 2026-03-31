# 智能电影推荐平台

基于 FastAPI + Next.js + PostgreSQL 的智能电影推荐系统，集成 TMDB 5000 数据集，支持语义搜索和个性化推荐。

## 🎯 项目特点

- **完整数据管道**: 从 TMDB 数据集下载到 PostgreSQL 导入的完整自动化流程
- **高性能 API**: 基于 FastAPI 的异步 RESTful API，支持高级搜索和过滤
- **现代化前端**: 使用 Next.js 14 + TypeScript + Tailwind CSS 构建的响应式界面
- **智能推荐**: 支持基于内容的推荐和语义搜索
- **可扩展架构**: 模块化设计，易于扩展和维护

## 📁 项目结构

```
graduation_project/
├── backend/                    # FastAPI 后端
│   ├── app/                   # 应用代码
│   │   ├── api/              # API 路由
│   │   ├── core/             # 核心配置
│   │   ├── models_tmdb.py    # 数据模型
│   │   ├── schemas_tmdb.py   # Pydantic 模型
│   │   └── main.py           # FastAPI 应用
│   ├── scripts/              # 自动化脚本
│   │   ├── download_tmdb_data.py    # 数据集下载
│   │   ├── import_tmdb_to_db.py     # 数据导入
│   │   ├── setup_database_windows.py # 数据库设置
│   │   ├── test_connection.py       # 连接测试
│   │   └── test_api.py              # API 测试
│   └── requirements.txt      # Python 依赖
├── frontend/                 # Next.js 前端
│   ├── app/                 # Next.js 13+ App Router
│   ├── components/          # React 组件
│   ├── lib/                 # 工具函数
│   └── types/               # TypeScript 类型
├── DESIGN.md               # 设计文档
├── POSTGRES_INSTALL_GUIDE.md # PostgreSQL 安装指南
├── README_DATA_ENGINEERING.md # 数据工程文档
└── .env.local              # 环境配置
```

## 🚀 快速开始

#### 设置项目环境
```bash
# 进入项目目录
cd d:\projects\graduation_project\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# PowerShell:
.\venv\Scripts\Activate.ps1
# CMD:
.\venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置数据库
```bash
# 运行数据库设置脚本
python scripts\setup_database_windows.py

# 测试数据库连接
python scripts\test_connection.py
```

#### 4. 下载和导入数据
```bash
# 下载 TMDB 5000 数据集
python scripts\download_tmdb_data.py

# 导入数据到 PostgreSQL
python scripts\import_tmdb_to_db.py
```

#### 5. 启动服务
```bash
# 启动后端 API 服务器
python -m uvicorn app.main:app --reload

# 在另一个终端启动前端
cd frontend
npm install
npm run dev
```

## 📊 数据统计

项目包含约 4,800 部电影的详细信息：

- **电影核心信息**: 标题、剧情、评分、票房等
- **演职员信息**: 演员、导演等
- **数据质量**: 完整性 >95%，基于 TMDB 官方数据
- **时间跨度**: 1916年至今

## 🔧 API 接口

### 电影相关 API
- `GET /api/movies` - 电影列表/搜索
- `GET /api/movies/top-rated` - 评分最高电影
- `GET /api/movies/top-box-office` - 票房最高电影
- `GET /api/movies/{movie_id}` - 电影详情
- `GET /api/movies/stats/summary` - 电影统计
- `GET /api/movies/random` - 随机电影

### 搜索功能
- 关键字搜索（标题、剧情、导演）
- 类型筛选
- 评分范围筛选
- 票房范围筛选
- 上映日期范围筛选

### API 文档
启动服务后访问: http://localhost:8000/docs

### 单独运行 PostgreSQL
```bash
docker run --name movie-postgres \
  -e POSTGRES_PASSWORD=postgres123 \
  -e POSTGRES_DB=movie_recommendation \
  -p 5432:5432 \
  -d postgres:15-alpine
```

## 🔍 故障排除

### PostgreSQL 连接失败
```bash
# 检查服务状态
Get-Service postgresql*

# 启动服务
Start-Service postgresql-x64-15

# 检查防火墙
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
```

### Python 依赖安装失败
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 conda
conda create -n movie-recommendation python=3.11
conda activate movie-recommendation
conda install -c conda-forge fastapi uvicorn sqlalchemy asyncpg psycopg2

### 查询优化
- 使用 EXPLAIN ANALYZE 分析查询计划
- 合理使用 JOIN 和子查询
- 实现分页查询

## 🔮 扩展功能

### 向量数据库集成
```sql
-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建电影向量表
CREATE TABLE movie_vectors (
    movie_id INTEGER PRIMARY KEY REFERENCES movies(id),
    embedding vector(1536),
    text_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 语义搜索
```sql
-- 语义相似度搜索
SELECT m.*, 1 - (mv.embedding <=> '[0.1, 0.2, ...]') as similarity
FROM movies m
JOIN movie_vectors mv ON m.id = mv.movie_id
ORDER BY mv.embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

## 📚 文档

- [设计文档](DESIGN.md) - 数据库架构和系统设计
- [API 文档](http://localhost:8000/docs) - 交互式 API 文档