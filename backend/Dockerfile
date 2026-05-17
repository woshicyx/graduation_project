# 使用多阶段构建优化镜像大小
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（pgvector 需要）
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码 - 保持 app 目录结构
COPY backend/requirements.txt ./requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码到 /app
COPY backend/app/ ./app/

# 暴露端口
EXPOSE 8000

# 启动命令
ENV PORT=8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]