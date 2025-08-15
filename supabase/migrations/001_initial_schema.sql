-- ChatGalaxy AI聊天平台 - 初始数据库架构
-- 创建时间: 2025-01-15
-- 描述: 创建用户、AI角色、聊天会话和消息表

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建消息类型枚举
CREATE TYPE message_type AS ENUM ('user', 'assistant', 'system');

-- 用户表 (users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI角色表 (ai_roles)
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

-- 聊天会话表 (chat_sessions)
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES ai_roles(id),
    title VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 聊天消息表 (chat_messages)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    message_type message_type NOT NULL,
    content TEXT NOT NULL,
    role_id UUID REFERENCES ai_roles(id),
    tokens_used INTEGER DEFAULT 0,
    response_time INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引优化查询性能
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_active_login ON users(is_active, last_login_at DESC);

-- AI角色表索引
CREATE INDEX idx_ai_roles_active ON ai_roles(is_active);
CREATE INDEX idx_ai_roles_sort ON ai_roles(sort_order);
CREATE INDEX idx_ai_roles_created_by ON ai_roles(created_by);

-- 聊天会话表索引
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, created_at DESC);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(is_active, last_message_at DESC);
CREATE INDEX idx_chat_sessions_role ON chat_sessions(role_id);

-- 聊天消息表索引
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at DESC);
CREATE INDEX idx_chat_messages_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_chat_messages_type ON chat_messages(message_type);
CREATE INDEX idx_chat_messages_role ON chat_messages(role_id);

-- 全文搜索索引（支持中文搜索）
CREATE INDEX idx_chat_messages_content_search ON chat_messages USING gin(to_tsvector('chinese', content));

-- 启用行级安全策略 (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- 用户表RLS策略
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

-- 聊天会话表RLS策略
CREATE POLICY "Users can view own sessions" ON chat_sessions FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can create sessions" ON chat_sessions FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can update own sessions" ON chat_sessions FOR UPDATE USING (auth.uid() = user_id);

-- 聊天消息表RLS策略
CREATE POLICY "Users can view own messages" ON chat_messages FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can create messages" ON chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- AI角色表公开访问策略（所有用户都可以查看角色）
CREATE POLICY "Anyone can view active roles" ON ai_roles FOR SELECT USING (is_active = true);

-- 创建触发器函数：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加updated_at触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_roles_updated_at BEFORE UPDATE ON ai_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建触发器函数：自动更新会话消息计数和最后消息时间
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

-- 为消息表添加统计触发器
CREATE TRIGGER update_session_stats_trigger
    AFTER INSERT OR DELETE ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_stats();

-- 插入默认AI角色数据
INSERT INTO ai_roles (name, description, system_prompt, is_active, sort_order) VALUES
('智能助手', '专业的AI助手，可以回答各种问题', '你是一个专业、友好的AI助手，请用简洁明了的语言回答用户问题。你具备广泛的知识储备，能够帮助用户解决各种问题。请保持礼貌和耐心，提供准确有用的信息。', true, 1),
('创意作家', '富有创意的写作助手', '你是一个富有创意的作家，擅长创作故事、诗歌和各种文学作品。你有丰富的想象力和优美的文笔，能够根据用户的需求创作出引人入胜的内容。请用生动有趣的语言与用户交流。', true, 2),
('技术专家', '专业的技术顾问', '你是一个资深的技术专家，精通各种编程语言和技术框架。你能够提供专业的技术建议，解答编程问题，并帮助用户解决技术难题。请用准确的技术术语和清晰的解释来回答问题。', true, 3),
('轻松聊天', '轻松愉快的聊天伙伴', '你是一个幽默风趣的聊天伙伴，喜欢用轻松的语调与用户交流。你善于活跃气氛，能够让对话变得有趣和愉快。请保持友好和幽默的态度，让用户感到轻松愉快。', true, 4);

-- 创建数据库函数：获取用户聊天统计
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

-- 创建数据库函数：清理过期的匿名会话
CREATE OR REPLACE FUNCTION cleanup_anonymous_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 删除7天前创建的匿名会话（user_id为NULL）
    DELETE FROM chat_sessions 
    WHERE user_id IS NULL 
    AND created_at < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;