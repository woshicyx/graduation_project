# 智能电影推荐平台 - 数据库脚本

本目录包含用于设置、导入、测试和优化数据库的所有脚本。

## 📋 脚本概述

| 脚本名称 | 用途 | 依赖 |
|---------|------|------|
| `setup_database_windows.py` | Windows环境数据库设置 | PostgreSQL, psycopg2 |
| `setup_complete_database.py` | 完整数据库架构设置 | PostgreSQL, psycopg2 |
| `import_tmdb_to_db.py` | 导入TMDB核心电影数据 | TMDB CSV文件, pandas, psycopg2 |
| `import_normalized_data.py` | 导入规范化数据(类型、演员、导演) | TMDB CSV文件, pandas, psycopg2 |
| `test_connection.py` | 测试数据库连接和性能 | psycopg2 |
| `database_optimization.py` | 数据库性能优化和分析 | psycopg2 |

## 🚀 快速开始

### 1. 环境准备

确保已安装以下软件：
- **PostgreSQL 12+** (默认密码: `356921`)
- **Python 3.8+**
- **pip** 包管理器

### 2. 安装Python依赖

```bash
# 进入项目目录
cd d:\projects\graduation_project

# 安装后端依赖
pip install -r backend/requirements.txt

# 或安装核心依赖
pip install psycopg2-binary pandas numpy
```

### 3. 数据库设置流程

#### 选项A: 使用完整设置脚本 (推荐)

```bash
# 1. 创建完整数据库架构
python backend/scripts/setup_complete_database.py

# 2. 导入核心电影数据
python backend/scripts/import_tmdb_to_db.py

# 3. 导入规范化数据
python backend/scripts/import_normalized_data.py

# 4. 测试数据库连接
python backend/scripts/test_connection.py

# 5. 优化数据库性能
python backend/scripts/database_optimization.py --execute
```

#### 选项B: 分步设置

```bash
# 1. 基础数据库设置
python backend/scripts/setup_database_windows.py

# 2. 导入电影数据
python backend/scripts/import_tmdb_to_db.py

# 3. 测试连接
python backend/scripts/test_connection.py
```

## 📊 数据库架构

### 核心表结构

1. **movies** - 电影核心信息表
   - 4803部电影数据
   - 包含评分、票房、类型等字段

2. **genres** - 电影类型表
   - 规范化存储电影类型
   - 与movies表通过movie_genres关联

3. **actors** - 演员表
   - 存储演员信息
   - 与movies表通过movie_actors关联

4. **directors** - 导演表
   - 存储导演信息
   - 与movies表通过movie_directors关联

5. **users** - 用户表 (为推荐系统准备)
6. **user_ratings** - 用户评分表
7. **user_watch_history** - 用户观看历史表

### 索引设计

数据库已预配置以下索引：

- **movies表**: 标题、发布日期、评分、人气、票房等索引
- **关联表**: 外键索引
- **用户表**: 用户ID、电影ID等索引
- **复合索引**: 优化常用查询模式

## 🔧 脚本详细说明

### 1. `setup_complete_database.py`

创建完整的数据库架构，包括：
- 创建数据库 `movie_recommendation`
- 创建所有核心表和关联表
- 创建性能优化索引
- 启用pgvector扩展 (如果已安装)

**用法:**
```bash
python backend/scripts/setup_complete_database.py
```

### 2. `import_tmdb_to_db.py`

导入TMDB 5000数据集的核心电影数据：
- 从当前目录读取 `tmdb_5000_movies.csv` 和 `tmdb_5000_credits.csv`
- 解析JSON字段 (类型、演员、导演)
- 批量导入到movies表
- 数据验证和质量检查

**用法:**
```bash
# 确保CSV文件在当前目录
python backend/scripts/import_tmdb_to_db.py
```

### 3. `import_normalized_data.py`

导入规范化数据：
- 解析并导入电影类型到genres表
- 导入演员数据到actors表
- 导入导演数据到directors表
- 创建所有关联关系
- 更新movies表的director字段

**用法:**
```bash
# 需要先运行 import_tmdb_to_db.py
python backend/scripts/import_normalized_data.py
```

### 4. `test_connection.py`

测试数据库连接和性能：
- 测试数据库连接状态
- 检查表结构和索引
- 测试查询性能
- 显示示例数据

**用法:**
```bash
python backend/scripts/test_connection.py
```

### 5. `database_optimization.py`

数据库性能优化工具：
- 分析数据库健康状况
- 识别未使用的索引
- 检测死行和碎片
- 生成优化建议
- 执行优化操作

**用法:**
```bash
# 生成优化报告
python backend/scripts/database_optimization.py

# 执行优化操作
python backend/scripts/database_optimization.py --execute
```

## 📈 性能优化建议

### 定期维护任务

```bash
# 1. 更新统计信息
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:356921@localhost:5432/movie_recommendation'); cur = conn.cursor(); cur.execute('ANALYZE;'); conn.commit()"

# 2. 执行VACUUM
python backend/scripts/database_optimization.py --execute
```

### 监控指标

1. **查询性能**: 使用 `test_connection.py` 监控查询时间
2. **索引效率**: 使用 `database_optimization.py` 检查索引使用情况
3. **数据增长**: 定期检查表大小和行数

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务是否运行
   - 验证密码是否正确 (默认: `356921`)
   - 检查端口是否被占用 (默认: `5432`)

2. **CSV文件找不到**
   - 确保 `tmdb_5000_movies.csv` 和 `tmdb_5000_credits.csv` 在当前目录
   - 可以从Kaggle下载: https://www.kaggle.com/tmdb/tmdb-movie-metadata

3. **导入速度慢**
   - 使用批量插入优化
   - 确保有足够的系统内存
   - 考虑分批导入数据

4. **内存不足**
   - 减少批量插入的大小
   - 增加系统虚拟内存
   - 使用数据库连接池

### 日志查看

所有脚本都输出详细日志，可以查看：
- 控制台输出
- 脚本运行状态
- 错误信息和警告

## 🎯 最佳实践

### 数据导入
1. 先导入核心数据，再导入规范化数据
2. 使用批量插入提高性能
3. 定期验证数据完整性

### 性能优化
1. 定期运行优化脚本
2. 监控慢查询
3. 根据查询模式调整索引

### 备份策略
1. 定期备份数据库
2. 测试恢复流程
3. 保留多个备份版本

## 📚 相关文档

- [数据库架构设计](../database_schema_design.md)
- [项目设计文档](../DESIGN.md)
- [环境配置](../.env.local)
- [PostgreSQL官方文档](https://www.postgresql.org/docs/)

## 🆘 技术支持

如果遇到问题：
1. 查看脚本输出的错误信息
2. 检查日志文件
3. 验证环境配置
4. 参考相关文档

---

**最后更新**: 2026年3月21日  
**版本**: 1.0.0  
**作者**: 智能电影推荐平台开发团队