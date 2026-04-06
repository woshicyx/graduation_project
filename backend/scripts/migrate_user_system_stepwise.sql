-- 用户系统数据库迁移脚本（分步执行）
-- 基于现有表结构，添加缺失的字段和表

-- 步骤1: 为users表添加缺失的字段
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS github_id VARCHAR(100);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS google_id VARCHAR(100);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- 步骤2: 为github_id和google_id添加唯一索引（如果字段存在的话）
-- 注意：这些索引需要字段已经存在，所以我们在添加字段后创建
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'github_id') THEN
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_github_id ON users(github_id) WHERE github_id IS NOT NULL;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'google_id') THEN
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;
    END IF;
END $$;

-- 步骤3: 创建user_favorites表（收藏功能）
CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    is_liked BOOLEAN DEFAULT true,
    tags JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    
    -- 确保一个用户对同一电影只有一个收藏记录
    CONSTRAINT unique_user_movie_favorite UNIQUE (user_id, movie_id)
);

-- 步骤4: 为user_favorites表添加索引
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_movie_id ON user_favorites(movie_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_created_at ON user_favorites(created_at);

-- 步骤5: 创建user_search_history表（搜索历史）
CREATE TABLE IF NOT EXISTS user_search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(100),
    query VARCHAR(500) NOT NULL,
    search_type VARCHAR(50) DEFAULT 'keyword',
    filters JSONB DEFAULT '{}',
    result_count INTEGER DEFAULT 0,
    result_ids JSONB DEFAULT '[]',
    click_count INTEGER DEFAULT 0,
    is_successful BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 步骤6: 为user_search_history表添加索引
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON user_search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_session_id ON user_search_history(session_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON user_search_history(created_at);
CREATE INDEX IF NOT EXISTS idx_search_history_query ON user_search_history(query);

-- 步骤7: 创建admin_audit_logs表（管理员审计日志）
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER,
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    old_data JSONB,
    new_data JSONB,
    changes JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 步骤8: 为admin_audit_logs表添加索引
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON admin_audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON admin_audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON admin_audit_logs(created_at);

-- 步骤9: 创建system_statistics表（系统统计）
CREATE TABLE IF NOT EXISTS system_statistics (
    id SERIAL PRIMARY KEY,
    stat_date TIMESTAMP NOT NULL,
    stat_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_stat_metric UNIQUE (stat_date, stat_type, metric_name)
);

-- 步骤10: 为system_statistics表添加索引
CREATE INDEX IF NOT EXISTS idx_system_stats_stat_date ON system_statistics(stat_date);
CREATE INDEX IF NOT EXISTS idx_system_stats_stat_type ON system_statistics(stat_type);
CREATE INDEX IF NOT EXISTS idx_system_stats_metric_name ON system_statistics(metric_name);

-- 步骤11: 创建popular_search_terms表（热门搜索词）
CREATE TABLE IF NOT EXISTS popular_search_terms (
    id SERIAL PRIMARY KEY,
    term VARCHAR(200) NOT NULL,
    search_count INTEGER DEFAULT 1,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    related_movie_ids JSONB DEFAULT '[]',
    categories JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 步骤12: 为popular_search_terms表添加索引
CREATE INDEX IF NOT EXISTS idx_popular_terms_term ON popular_search_terms(term);
CREATE INDEX IF NOT EXISTS idx_popular_terms_period_start ON popular_search_terms(period_start);
CREATE INDEX IF NOT EXISTS idx_popular_terms_period_end ON popular_search_terms(period_end);
CREATE INDEX IF NOT EXISTS idx_popular_terms_search_count ON popular_search_terms(search_count);

-- 步骤13: 更新user_watch_history表，添加缺失字段
ALTER TABLE user_watch_history 
ADD COLUMN IF NOT EXISTS progress FLOAT DEFAULT 0.0;

ALTER TABLE user_watch_history 
ADD COLUMN IF NOT EXISTS interaction_score INTEGER DEFAULT 1;

-- 步骤14: 更新user_ratings表，添加情感分析和关键词字段
ALTER TABLE user_ratings 
ADD COLUMN IF NOT EXISTS sentiment_score FLOAT;

ALTER TABLE user_ratings 
ADD COLUMN IF NOT EXISTS keywords JSONB DEFAULT '[]';

-- 步骤15: 创建初始管理员账户（如果users表为空且没有管理员）
DO $$
DECLARE
    admin_count INTEGER;
    total_users INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM users WHERE role = 'admin';
    SELECT COUNT(*) INTO total_users FROM users;
    
    IF admin_count = 0 AND total_users = 0 THEN
        -- 创建初始管理员账户
        INSERT INTO users (
            username, 
            email, 
            password_hash, 
            display_name, 
            role, 
            is_active, 
            is_verified,
            created_at,
            updated_at
        ) VALUES (
            'admin',
            'admin@movieai.com',
            -- 密码: admin123 (使用bcrypt哈希，这里需要在实际应用中生成)
            '$2b$12$YOUR_BCRYPT_HASH_HERE',
            '系统管理员',
            'admin',
            true,
            true,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE '已创建初始管理员账户: admin/admin123 (请在生产环境中修改密码)';
    END IF;
END $$;

-- 步骤16: 创建函数：更新updated_at时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 步骤17: 为相关表添加触发器
DO $$
BEGIN
    -- 为users表添加触发器
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
        CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 为user_favorites表添加触发器
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_favorites') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_favorites_updated_at') THEN
            CREATE TRIGGER update_user_favorites_updated_at 
                BEFORE UPDATE ON user_favorites 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        END IF;
    END IF;
    
    -- 为user_ratings表添加触发器
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_ratings_updated_at') THEN
        CREATE TRIGGER update_user_ratings_updated_at 
            BEFORE UPDATE ON user_ratings 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 为system_statistics表添加触发器
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_statistics') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_system_statistics_updated_at') THEN
            CREATE TRIGGER update_system_statistics_updated_at 
                BEFORE UPDATE ON system_statistics 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        END IF;
    END IF;
    
    -- 为popular_search_terms表添加触发器
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'popular_search_terms') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_popular_search_terms_updated_at') THEN
            CREATE TRIGGER update_popular_search_terms_updated_at 
                BEFORE UPDATE ON popular_search_terms 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        END IF;
    END IF;
END $$;

-- 输出迁移结果
SELECT '用户系统数据库迁移完成' as message;