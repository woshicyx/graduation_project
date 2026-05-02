# 🎬 智能电影推荐平台 - 部署指南

## 📋 部署方案概述

本项目采用 **混合部署方案**：Vercel (前端) + Railway (后端) + Supabase (数据库)

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户浏览器                              │
└─────────────────────────────┬─────────────────────────────────┘
                              │
                    ┌──────────▼──────────┐
                    │    Vercel CDN      │
                    │   (Next.js 前端)   │
                    └──────────┬──────────┘
                              │
                    ┌──────────▼──────────┐
                    │    Railway          │
                    │  (FastAPI 后端)     │
                    └──────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────────┐ ┌───▼────────┐ ┌────▼─────┐
    │   Supabase        │ │  Qdrant    │ │ 智谱AI    │
    │  (PostgreSQL)     │ │  Cloud     │ │ API      │
    │                   │ │ (向量库)   │ │          │
    └───────────────────┘ └────────────┘ └──────────┘
```

### 优点
- ✅ **零成本起步**：Vercel + Railway 免费层足够个人项目使用
- ✅ **自动 HTTPS**：无需配置 SSL 证书
- ✅ **全球 CDN**：Vercel 提供全球边缘网络，访问速度快
- ✅ **自动扩缩容**：流量突增时自动处理
- ✅ **简单的数据库迁移**：Supabase 提供可视化管理

### 缺点
- ⚠️ 免费层有资源限制
- ⚠️ 需要管理多个服务提供商
- ⚠️ 数据存储在各平台，需要备份策略

---

## 🗄️ 第一步：创建 Supabase 数据库

### 1.1 注册 Supabase

1. 访问 [supabase.com](https://supabase.com) 并注册
2. 创建新项目 (New Project)
3. 选择区域（建议选择靠近你用户的区域）
4. 设置数据库密码（**妥善保存**）

### 1.2 获取连接信息

在 Supabase Dashboard → Settings → Database 中找到：

```
Host: db.xxxxx.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: your-db-password
```

### 1.3 初始化数据库表

使用 Supabase SQL Editor 执行以下脚本：

```sql
-- 创建用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建电影收藏表
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL,
    is_liked BOOLEAN DEFAULT true,
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);

-- 创建浏览历史表
CREATE TABLE user_watch_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL,
    watch_duration INTEGER DEFAULT 0,
    progress DECIMAL(5,2) DEFAULT 0,
    interaction_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提升查询性能
CREATE INDEX idx_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_history_user_id ON user_watch_history(user_id);
CREATE INDEX idx_history_movie_id ON user_watch_history(movie_id);
```

### 1.4 获取完整的数据库 URL

格式：`postgresql://postgres:{PASSWORD}@db.{PROJECT}.supabase.co:5432/postgres`

---

## 🚀 第二步：部署后端到 Railway

### 2.1 准备 Railway 部署

Railway 支持直接连接 GitHub 仓库自动部署。

1. 访问 [railway.app](https://railway.app) 并注册
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择 `MovieAI` 仓库
4. 选择 `backend` 文件夹作为根目录

### 2.2 配置环境变量

在 Railway Dashboard → Variables 中添加：

```env
# 应用配置
APP_NAME=movie-recommender-backend
ENVIRONMENT=prod
DEBUG=false

# 数据库 (Supabase)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# 向量数据库 (Qdrant Cloud)
QDRANT_URL=https://your-project.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# 智谱 AI
ZHIPUAI_API_KEY=your-zhipuai-api-key

# TMDB API
TMDB_API_KEY=your-tmdb-api-key

# JWT (重要：生产环境请使用强密钥)
JWT_SECRET_KEY=generate-a-strong-random-string-here-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 前端 URL (用于 CORS)
NEXT_PUBLIC_API_URL=https://your-frontend.vercel.app
```

### 2.3 配置启动命令

Railway 会自动检测 `Procfile`，如果需要手动设置：

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 2.4 等待部署完成

Railway 会自动检测依赖并安装。部署完成后，你会获得一个 URL，例如：

```
https://movie-recommender-backend.up.railway.app
```

### 2.5 验证后端部署

访问 `https://movie-recommender-backend.up.railway.app/api/health` 检查健康状态。

---

## 🌐 第三步：部署前端到 Vercel

### 3.1 准备前端配置

我已经创建了 `frontend/vercel.json` 配置文件。

编辑 `frontend/.env.production`：

```env
# 后端 API 地址（替换为你的 Railway URL）
NEXT_PUBLIC_API_URL=https://movie-recommender-backend.up.railway.app/api
```

### 3.2 连接 Vercel

1. 访问 [vercel.com](https://vercel.com) 并注册（建议用 GitHub 账号）
2. 点击 "Add New..." → "Project"
3. 导入 `MovieAI` 仓库
4. 设置 **Root Directory** 为 `frontend`
5. 在 **Environment Variables** 中添加：

```env
NEXT_PUBLIC_API_URL=https://movie-recommender-backend.up.railway.app/api
```

6. 点击 "Deploy"

### 3.3 配置自定义域名（可选）

在 Vercel Dashboard → Settings → Domains 中可以添加自定义域名。

---

## 🔧 第四步：配置 Qdrant Cloud（向量数据库）

### 4.1 注册 Qdrant Cloud

1. 访问 [qdrant.tech](https://qdrant.tech) 或 [cloud.qdrant.io](https://cloud.qdrant.io)
2. 创建免费集群
3. 记录集群 URL 和 API Key

### 4.2 创建向量集合

通过 Qdrant Dashboard 或 API 创建：

```bash
curl -X PUT "https://your-cluster.qdrant.io/collections/movies" \
  -H "Content-Type: application/json" \
  -H "api-key: your-api-key" \
  -d '{
    "vectors": {
      "size": 1024,
      "distance": "Cosine"
    }
  }'
```

---

## 🔄 第五步：迁移数据

### 5.1 迁移电影数据到 Supabase

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 运行数据库迁移脚本（需要先安装依赖）
python -m pip install -r requirements.txt

# 导入电影数据
python scripts/seed_mock_data.py
```

### 5.2 重新索引向量到 Qdrant

如果之前有本地数据需要重新上传：

```bash
# 需要重新生成电影文本的 embedding
# 运行向量索引脚本
python scripts/vector_index.py
```

---

## ✅ 部署后检查清单

- [ ] Supabase 数据库创建成功，可以连接
- [ ] Railway 后端部署成功，`/api/health` 返回 200
- [ ] Vercel 前端部署成功，可以访问
- [ ] CORS 配置正确，前端可以调用后端 API
- [ ] JWT 密钥已更新为安全的随机字符串
- [ ] 智谱 AI API Key 已配置
- [ ] Qdrant 向量库已配置

---

## 🌊 常见问题排查

### Q1: CORS 错误
检查后端 `main.py` 中的 `allowed_origins` 是否包含你的 Vercel 域名。

### Q2: 数据库连接失败
确认 `DATABASE_URL` 格式正确，密码没有特殊字符需要 URL 编码。

### Q3: Railway 部署失败
检查 `requirements.txt` 是否有语法错误，确保所有依赖版本兼容。

### Q4: 前端无法访问后端 API
检查 `NEXT_PUBLIC_API_URL` 是否正确，注意不要加错 `/api` 后缀。

### Q5: 向量搜索不工作
确认 Qdrant 集合已创建，且向量维度为 1024。

---

## 📊 监控和维护

### Railway 监控
- 查看日志：Railway Dashboard → Deployment → Logs
- 性能指标：Railway Dashboard → Metrics

### Vercel 监控
- 查看分析：Vercel Dashboard → Analytics
- 函数日志：Vercel Dashboard → Logs

### Supabase 管理
- 数据库管理：Supabase Dashboard → Table Editor
- SQL 查询：Supabase Dashboard → SQL Editor

---

## 🔄 更新部署

每次推送到 GitHub，Railway 和 Vercel 都会自动重新部署。

如果你只想更新其中一个：
- Railway：推送到 `backend/` 目录
- Vercel：推送到 `frontend/` 目录

---

## 💰 成本预估

| 服务 | 免费层限制 | 超出费用 |
|------|-----------|---------|
| Vercel | 100GB 带宽/月 | 按使用量计费 |
| Railway | 500小时/月 | $5/100小时 |
| Supabase | 500MB 数据库 | $25/500MB |
| Qdrant Cloud | 1GB 向量存储 | 按使用量计费 |

**个人项目推荐**：免费层足够使用 🎉

---

## 📚 相关资源

- [Vercel 文档](https://vercel.com/docs)
- [Railway 文档](https://docs.railway.app)
- [Supabase 文档](https://supabase.com/docs)
- [Qdrant 文档](https://qdrant.tech/documentation/)
- [智谱 AI 文档](https://open.bigmodel.cn/dev/api)

如有问题，请查看项目的 `README.md` 或提交 Issue。