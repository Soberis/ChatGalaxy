-- ChatGalaxy AI聊天平台 - 数据库结构更新
-- 创建时间: 2025-01-15
-- 描述: 更新现有表结构以匹配项目文档要求

-- 更新users表，添加缺失字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- 更新ai_roles表结构
-- 先备份现有数据
CREATE TEMP TABLE ai_roles_backup AS SELECT * FROM ai_roles;

-- 删除现有ai_roles表并重新创建
DROP TABLE IF EXISTS ai_roles CASCADE;
CREATE TABLE ai_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    avatar_url VARCHAR(500),
    personality JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 更新chat_sessions表，添加缺失字段
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS role_id UUID;
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0;
ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP WITH TIME ZONE;

-- 更新chat_messages表结构
-- 创建消息类型枚举（如果不存在）
DO $$ BEGIN
    CREATE TYPE message_type AS ENUM ('user', 'assistant', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 重命名和调整chat_messages表字段
DO $$ BEGIN
    -- 检查并重命名message列为content
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'message') THEN
        ALTER TABLE chat_messages RENAME COLUMN message TO content;
    END IF;
END $$;

-- 删除is_ai列（如果存在）
ALTER TABLE chat_messages DROP COLUMN IF EXISTS is_ai;

-- 添加新字段
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS message_type message_type;
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS tokens_used INTEGER DEFAULT 0;
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS response_time INTEGER;

-- 处理role_id字段类型转换
DO $$ BEGIN
    -- 如果role_id列存在且不是UUID类型，先删除再重新创建
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'chat_messages' AND column_name = 'role_id' 
               AND data_type != 'uuid') THEN
        ALTER TABLE chat_messages DROP COLUMN role_id;
        ALTER TABLE chat_messages ADD COLUMN role_id UUID;
    ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'chat_messages' AND column_name = 'role_id') THEN
        ALTER TABLE chat_messages ADD COLUMN role_id UUID;
    END IF;
END $$;

-- 设置默认的message_type值
UPDATE chat_messages SET message_type = 'user' WHERE message_type IS NULL;
ALTER TABLE chat_messages ALTER COLUMN message_type SET NOT NULL;

-- 创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_active_login ON users(is_active, last_login_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_roles_active ON ai_roles(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_roles_sort ON ai_roles(sort_order);
CREATE INDEX IF NOT EXISTS idx_ai_roles_created_by ON ai_roles(created_by);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active ON chat_sessions(is_active, last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_role ON chat_sessions(role_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_type ON chat_messages(message_type);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role_id);

-- 全文搜索索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_content_search ON chat_messages USING gin(to_tsvector('english', content));

-- 启用RLS（如果未启用）
ALTER TABLE ai_roles ENABLE ROW LEVEL SECURITY;

-- 创建或更新RLS策略
DROP POLICY IF EXISTS "Users can view own data" ON users;
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own data" ON users;
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can view own sessions" ON chat_sessions;
CREATE POLICY "Users can view own sessions" ON chat_sessions FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Users can create sessions" ON chat_sessions;
CREATE POLICY "Users can create sessions" ON chat_sessions FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Users can update own sessions" ON chat_sessions;
CREATE POLICY "Users can update own sessions" ON chat_sessions FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view own messages" ON chat_messages;
CREATE POLICY "Users can view own messages" ON chat_messages FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Users can create messages" ON chat_messages;
CREATE POLICY "Users can create messages" ON chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Anyone can view active roles" ON ai_roles;
CREATE POLICY "Anyone can view active roles" ON ai_roles FOR SELECT USING (is_active = true);

-- 创建触发器函数（如果不存在）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 添加触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ai_roles_updated_at ON ai_roles;
CREATE TRIGGER update_ai_roles_updated_at BEFORE UPDATE ON ai_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_chat_sessions_updated_at ON chat_sessions;
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建会话统计触发器函数
CREATE OR REPLACE FUNCTION update_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE chat_sessions 
        SET message_count = message_count + 1,
            last_message_at = NEW.created_at
        WHERE id = NEW.session_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE chat_sessions 
        SET message_count = GREATEST(message_count - 1, 0)
        WHERE id = OLD.session_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- 添加统计触发器
DROP TRIGGER IF EXISTS update_session_stats_trigger ON chat_messages;
CREATE TRIGGER update_session_stats_trigger
    AFTER INSERT OR DELETE ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_stats();

-- 插入AI角色数据
INSERT INTO ai_roles (name, description, system_prompt, is_active, sort_order) VALUES
('智能助手', '专业的AI助手，可以回答各种问题', '你是一个专业、友好的AI助手，请用简洁明了的语言回答用户问题。你具备广泛的知识储备，能够帮助用户解决各种问题。请保持礼貌和耐心，提供准确有用的信息。', true, 1),
('创意作家', '富有创意的写作助手', '你是一个富有创意的作家，擅长创作故事、诗歌和各种文学作品。你有丰富的想象力和优美的文笔，能够根据用户的需求创作出引人入胜的内容。请用生动有趣的语言与用户交流。', true, 2),
('技术专家', '专业的技术顾问', '你是一个资深的技术专家，精通各种编程语言和技术框架。你能够提供专业的技术建议，解答编程问题，并帮助用户解决技术难题。请用准确的技术术语和清晰的解释来回答问题。', true, 3),
('轻松聊天', '轻松愉快的聊天伙伴', '你是一个幽默风趣的聊天伙伴，喜欢用轻松的语调与用户交流。你善于活跃气氛，能够让对话变得有趣和愉快。请保持友好和幽默的态度，让用户感到轻松愉快。', true, 4);

-- 添加外键约束
ALTER TABLE chat_sessions ADD CONSTRAINT fk_chat_sessions_role_id FOREIGN KEY (role_id) REFERENCES ai_roles(id);
ALTER TABLE chat_messages ADD CONSTRAINT fk_chat_messages_role_id FOREIGN KEY (role_id) REFERENCES ai_roles(id);

-- 创建实用函数
CREATE OR REPLACE FUNCTION get_user_chat_stats(user_uuid UUID)
RETURNS TABLE(
    total_sessions INTEGER,
    total_messages INTEGER,
    active_sessions INTEGER,
    last_chat_time TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT cs.id)::INTEGER as total_sessions,
        COALESCE(SUM(cs.message_count), 0)::INTEGER as total_messages,
        COUNT(DISTINCT CASE WHEN cs.is_active THEN cs.id END)::INTEGER as active_sessions,
        MAX(cs.last_message_at) as last_chat_time
    FROM chat_sessions cs
    WHERE cs.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION cleanup_anonymous_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM chat_sessions 
    WHERE user_id IS NULL 
    AND created_at < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;