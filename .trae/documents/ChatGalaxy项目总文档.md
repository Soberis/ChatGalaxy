# AI 互动网站项目文档

> **ChatGalaxy** - 基于2025年主流技术栈的智能AI聊天平台

## 📋 项目概述

本项目采用**2025年中国最流行的技术栈组合**，构建现代化AI互动网站。技术选型完全符合当前行业发展趋势，具备优秀的前瞻性和可维护性。

---

## 1️⃣ 项目需求文档 (PR)

**项目名称**：AI 互动小网站（ChatGalaxy）

**项目目标**：
- 搭建一个基于 Python FastAPI 后端 + Vue3 前端的 AI 聊天网站
- 支持多种聊天角色，实时显示对话，用户可登录保存聊天记录
- 项目可部署上线，用于个人展示和求职加分

**用户目标**：
- 想与 AI 互动娱乐的普通用户
- 需要测试 AI API 的开发者
- 招聘面试展示项目能力

**核心功能**：
1. AI 聊天（REST API + WebSocket）
2. 多角色对话（角色切换）
3. 用户系统（注册、登录、退出）
4. 聊天记录保存（数据库）
5. 实时消息显示（WebSocket 推送）
6. 部署上线（可公网访问）


### 🚀 技术栈架构 (2025年主流趋势)

| 技术层级 | 技术选型 | 2025年趋势说明 |
|---------|---------|----------------|
| **前端框架** | Vue 3 + TypeScript + Vite | Vue3+TS是2025年主流组合，提供响应式API优化与类型安全支持 |
| **UI组件库** | Element Plus + TailwindCSS | 企业级Vue3组件库，中文生态完善，配合TailwindCSS实现高度定制化 |
| **后端框架** | Python FastAPI + Pydantic + uvicorn | FastAPI是2025年热门Python后端框架，异步性能优异 |
| **数据库** | PostgreSQL (Supabase托管) | 企业级关系型数据库，Supabase提供现代化BaaS服务 |
| **AI集成** | 阿里通义千问(Qwen) | 符合国内AI发展趋势，中文理解能力强，合规性好 |
| **部署方案** | Vercel + Render + Supabase | 前后端分离，现代化云原生部署架构 |

#### 🎯 技术选型优势

1. **前端生态成熟**: Vue3在2024年NPM下载量位居第二，TypeScript正在蚕食JavaScript市场份额
2. **后端性能卓越**: FastAPI基于异步ASGI设计，性能优于传统Django框架
3. **AI集成前瞻**: 阿里通义千问在中国AI市场具备技术领先优势和合规保障
4. **开发效率高**: Element Plus提供70+企业级组件，TailwindCSS支持快速UI定制
5. **部署现代化**: 采用Serverless架构，支持自动扩缩容和全球CDN加速

---

## 🎨 UI主题色方案

基于阿里通义千问官网的现代化设计风格，采用以下主题色方案：

| 色彩类型 | 颜色值 | 使用场景 |
|---------|--------|----------|
| **主色调** | `#1677FF` (蓝色) | 主要按钮、链接、品牌色 |
| **辅助色** | `#F0F8FF` (浅蓝) | 背景色、卡片背景 |
| **文本色** | `#262626` (深灰) | 主要文本内容 |
| **次要文本** | `#8C8C8C` (中灰) | 辅助信息、时间戳 |
| **边框色** | `#E8E8E8` (浅灰) | 分割线、输入框边框 |
| **成功色** | `#52C41A` (绿色) | 成功状态、确认操作 |
| **警告色** | `#FAAD14` (橙色) | 警告提示、注意事项 |
| **错误色** | `#FF4D4F` (红色) | 错误状态、删除操作 |

---

## 2️⃣ 产品需求文档 (PRD)

### 一、产品概述

本产品是一个 AI 互动聊天网站，用户可以与 AI 进行实时交流，并选择不同人格设定的 AI 角色。注册用户可保存历史记录并随时查看。

### 二、用户故事

- **访客用户**：可以直接与 AI 聊天，但无法保存历史记录
- **注册用户**：可登录，保存聊天记录，并在个人中心查看历史对话
- **管理员（可选）**：可管理角色配置、封禁用户



## 三、功能需求

### 3.1 核心功能模块

| 功能模块 | 功能描述 | 优先级 | 技术实现 |
|---------|---------|--------|----------|
| **AI智能对话** | 用户发送消息，AI返回智能回答 | ⭐⭐⭐⭐⭐ | 阿里通义千问API + WebSocket实时通信 |
| **多角色切换** | 用户可切换不同性格的AI角色 | ⭐⭐⭐⭐ | 动态Prompt模板 + 角色配置管理 |
| **实时消息显示** | 消息即时出现在聊天界面 | ⭐⭐⭐⭐⭐ | WebSocket双向通信 + Vue3响应式更新 |
| **聊天记录管理** | 登录用户聊天内容持久化存储 | ⭐⭐⭐⭐ | PostgreSQL + 会话管理 |
| **用户认证系统** | 注册、登录、权限管理 | ⭐⭐⭐⭐⭐ | JWT Token + Supabase Auth |

### 3.2 增强功能模块

| 功能模块 | 功能描述 | 优先级 | 实现方案 |
|---------|---------|--------|----------|
| **语音合成** | AI回复转换为语音播放 | ⭐⭐ | Web Speech API / 第三方TTS服务 |
| **多媒体支持** | 支持图片、表情包等富媒体内容 | ⭐⭐ | 文件上传 + CDN存储 |

---



## 四、页面架构设计

### 4.1 核心页面结构

```mermaid
graph TD
    A[首页/聊天界面] --> B[用户认证页面]
    A --> C[个人中心]
    A --> D[角色管理页面]
    C --> E[聊天历史记录]
    C --> F[用户设置]
    D --> G[角色配置]
    D --> H[自定义角色]
```

### 4.2 页面功能说明

| 页面名称 | 核心功能 | UI组件 | 响应式设计 |
|---------|---------|--------|------------|
| **聊天主界面** | AI对话、角色切换、实时消息 | Element Plus Chat组件 + 自定义消息气泡 | 移动端优先，支持触摸操作 |
| **用户认证** | 登录、注册、密码重置 | Element Plus Form + 验证组件 | 居中卡片式布局 |
| **个人中心** | 用户信息、聊天记录、设置 | Element Plus Tabs + Table组件 | 侧边栏 + 主内容区 |
| **角色管理** | 角色选择、自定义配置 | Element Plus Card + Dialog | 网格布局 + 弹窗编辑 |

---



五、接口需求

### 5.1 REST API 接口设计

#### 🔐 用户认证模块

| HTTP方法 | API路径 | 功能描述 | 权限要求 | 请求体示例 |
|---------|---------|---------|----------|------------|
| `POST` | `/api/auth/register` | 用户注册 | 公开访问 | `{"username": "user", "email": "user@example.com", "password": "123456"}` |
| `POST` | `/api/auth/login` | 用户登录 | 公开访问 | `{"email": "user@example.com", "password": "123456"}` |
| `POST` | `/api/auth/logout` | 用户登出 | 需要认证 | `{"refresh_token": "xxx"}` |
| `GET` | `/api/auth/profile` | 获取用户信息 | 需要认证 | - |
| `PUT` | `/api/auth/profile` | 更新用户信息 | 需要认证 | `{"username": "newname", "avatar_url": "xxx"}` |

#### 🤖 AI智能对话模块

| HTTP方法 | API路径 | 功能描述 | 权限要求 | 请求体示例 |
|---------|---------|---------|----------|------------|
| `POST` | `/api/chat/send` | 发送消息给AI并获取回复 | 需要认证 | `{"message": "你好", "role_id": "assistant", "session_id": "xxx"}` |
| `GET` | `/api/chat/history` | 获取用户聊天历史记录 | 需要认证 | 查询参数: `?page=1&limit=20&session_id=xxx` |
| `DELETE` | `/api/chat/clear` | 清空指定会话聊天记录 | 需要认证 | `{"session_id": "xxx"}` |
| `GET` | `/api/chat/sessions` | 获取用户所有聊天会话 | 需要认证 | - |
| `POST` | `/api/chat/session` | 创建新的聊天会话 | 需要认证 | `{"title": "新对话", "role_id": "assistant"}` |

#### 🎭 AI角色管理模块

| HTTP方法 | API路径 | 功能描述 | 权限要求 | 请求体示例 |
|---------|---------|---------|----------|------------|
| `GET` | `/api/roles` | 获取所有可用AI角色 | 公开访问 | - |
| `GET` | `/api/roles/{role_id}` | 获取特定角色详细信息 | 公开访问 | - |
| `POST` | `/api/roles/switch` | 切换当前对话AI角色 | 需要认证 | `{"role_id": "creative_writer", "session_id": "xxx"}` |

**系统管理**
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /api/system/health | 系统健康检查 | 公开 |
| GET | /api/system/stats | 系统统计信息 | 管理员 |

### 5.2 WebSocket 实时通信设计

#### 🔗 连接配置
- **开发环境**: `ws://localhost:8000/ws/chat/{session_id}`
- **生产环境**: `wss://your-api-domain.com/ws/chat/{session_id}`
- **认证方式**: JWT Token通过查询参数传递 `?token=xxx`

#### 📨 消息协议格式

**客户端发送消息**:
```json
{
  "type": "user_message",
  "data": {
    "message": "你好，请介绍一下Vue3的新特性",
    "role_id": "tech_expert",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

**服务端响应消息**:
```json
{
  "type": "ai_response",
  "data": {
    "message": "Vue3的主要新特性包括Composition API...",
    "role_name": "技术专家",
    "message_id": "msg_123",
    "timestamp": "2025-01-01T12:00:01Z",
    "status": "completed"
  }
}
```

**系统状态消息**:
```json
{
  "type": "system_status",
  "data": {
    "status": "typing",
    "message": "AI正在思考中..."
  }
}
```

---

## 六、数据库架构设计

### 6.1 核心数据表结构

#### 👤 用户信息表 (users)

| 字段名 | 数据类型 | 字段说明 | 约束条件 | 索引 |
|--------|----------|----------|----------|------|
| `id` | `UUID` | 用户唯一标识 | `PRIMARY KEY` | 主键索引 |
| `username` | `VARCHAR(50)` | 用户昵称 | `UNIQUE, NOT NULL` | 唯一索引 |
| `email` | `VARCHAR(100)` | 用户邮箱 | `UNIQUE, NOT NULL` | 唯一索引 |
| `password_hash` | `VARCHAR(255)` | 密码哈希值 | `NOT NULL` | - |
| `avatar_url` | `TEXT` | 用户头像链接 | `NULL` | - |
| `is_active` | `BOOLEAN` | 账户状态 | `DEFAULT TRUE` | 普通索引 |
| `last_login_at` | `TIMESTAMP` | 最后登录时间 | `NULL` | 普通索引 |
| `created_at` | `TIMESTAMP` | 账户创建时间 | `DEFAULT NOW()` | 普通索引 |
| `updated_at` | `TIMESTAMP` | 信息更新时间 | `DEFAULT NOW()` | - |

**AI角色配置表（ai_roles）**
| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 角色唯一标识 |
| name | VARCHAR(100) | NOT NULL | 角色名称 |
| description | TEXT | NULL | 角色描述 |
| system_prompt | TEXT | NOT NULL | 系统提示词 |
| avatar_url | VARCHAR(500) | NULL | 角色头像URL |
| personality | JSONB | NULL | 性格特征配置 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| sort_order | INTEGER | DEFAULT 0 | 排序权重 |
| created_by | UUID | FOREIGN KEY | 创建者ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**用户会话表（chat_sessions）**
| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 会话唯一标识 |
| user_id | UUID | FOREIGN KEY | 用户ID（可为空，支持匿名） |
| role_id | UUID | FOREIGN KEY | AI角色ID |
| title | VARCHAR(200) | NULL | 会话标题 |
| is_active | BOOLEAN | DEFAULT TRUE | 会话是否活跃 |
| message_count | INTEGER | DEFAULT 0 | 消息数量 |
| last_message_at | TIMESTAMP | NULL | 最后消息时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

#### 💬 聊天消息表 (chat_messages)

| 字段名 | 数据类型 | 字段说明 | 约束条件 | 索引 |
|--------|----------|----------|----------|------|
| `id` | `UUID` | 消息唯一标识 | `PRIMARY KEY` | 主键索引 |
| `session_id` | `UUID` | 会话ID | `NOT NULL` | 普通索引 |
| `user_id` | `UUID` | 用户ID | `FOREIGN KEY REFERENCES users(id)` | 外键索引 |
| `message_type` | `ENUM` | 消息类型 | `('user', 'assistant', 'system')` | 普通索引 |
| `content` | `TEXT` | 消息内容 | `NOT NULL` | 全文索引 |
| `role_id` | `VARCHAR(50)` | AI角色标识 | `NULL` | 普通索引 |
| `tokens_used` | `INTEGER` | 消耗Token数量 | `DEFAULT 0` | - |
| `response_time` | `INTEGER` | 响应时间(毫秒) | `NULL` | - |
| `created_at` | `TIMESTAMP` | 消息创建时间 | `DEFAULT NOW()` | 时间索引 |

#### 🎭 AI角色配置表 (ai_roles)

| 字段名 | 数据类型 | 字段说明 | 约束条件 | 索引 |
|--------|----------|----------|----------|------|
| `id` | `VARCHAR(50)` | 角色唯一标识 | `PRIMARY KEY` | 主键索引 |
| `name` | `VARCHAR(100)` | 角色显示名称 | `NOT NULL` | - |
| `description` | `TEXT` | 角色描述 | `NULL` | - |
| `system_prompt` | `TEXT` | 系统提示词 | `NOT NULL` | - |
| `avatar_url` | `TEXT` | 角色头像链接 | `NULL` | - |
| `is_active` | `BOOLEAN` | 是否启用 | `DEFAULT TRUE` | 普通索引 |
| `sort_order` | `INTEGER` | 显示排序 | `DEFAULT 0` | 普通索引|
| `created_at` | `TIMESTAMP` | 创建时间 | `DEFAULT NOW()` | - |

#### 📝 用户会话表 (chat_sessions)

| 字段名 | 数据类型 | 字段说明 | 约束条件 | 索引 |
|--------|----------|----------|----------|------|
| `id` | `UUID` | 会话唯一标识 | `PRIMARY KEY` | 主键索引 |
| `user_id` | `UUID` | 用户ID | `FOREIGN KEY REFERENCES users(id)` | 外键索引 |
| `title` | `VARCHAR(200)` | 会话标题 | `NOT NULL` | - |
| `role_id` | `VARCHAR(50)` | 当前AI角色 | `FOREIGN KEY REFERENCES ai_roles(id)` | 外键索引 |
| `message_count` | `INTEGER` | 消息总数 | `DEFAULT 0` | - |
| `last_message_at` | `TIMESTAMP` | 最后消息时间 | `NULL` | 时间索引 |
| `is_archived` | `BOOLEAN` | 是否归档 | `DEFAULT FALSE` | 普通索引 |
| `created_at` | `TIMESTAMP` | 会话创建时间 | `DEFAULT NOW()` | 时间索引 |

### 6.2 数据库性能优化

#### 🚀 核心索引策略

```sql
-- 用户表性能索引
CREATE INDEX idx_users_email ON users(email);                    -- 登录查询优化
CREATE INDEX idx_users_active_login ON users(is_active, last_login_at DESC); -- 活跃用户统计
CREATE INDEX idx_users_created_at ON users(created_at DESC);      -- 用户注册趋势

-- 聊天消息表复合索引
CREATE INDEX idx_messages_session_time ON chat_messages(session_id, created_at DESC); -- 会话消息查询
CREATE INDEX idx_messages_user_type ON chat_messages(user_id, message_type, created_at DESC); -- 用户消息历史
CREATE INDEX idx_messages_role_time ON chat_messages(role_id, created_at DESC); -- 角色使用统计

-- 会话表查询优化
CREATE INDEX idx_sessions_user_active ON chat_sessions(user_id, is_archived, last_message_at DESC); -- 用户活跃会话
CREATE INDEX idx_sessions_role_count ON chat_sessions(role_id, message_count DESC); -- 角色热度统计

-- 全文搜索索引（PostgreSQL）
CREATE INDEX idx_messages_content_search ON chat_messages USING gin(to_tsvector('chinese', content)); -- 中文消息搜索
```

#### 📊 数据库分区策略

```sql
-- 按时间分区聊天消息表（月度分区）
CREATE TABLE chat_messages_y2025m01 PARTITION OF chat_messages
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE chat_messages_y2025m02 PARTITION OF chat_messages
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```



七、安全性设计

### 7.1 身份认证与授权
- **JWT Token认证**：使用RS256算法签名，设置合理的过期时间
- **刷新Token机制**：实现Token自动刷新，提升用户体验
- **权限控制**：基于角色的访问控制（RBAC），区分普通用户和管理员
- **会话管理**：支持多设备登录检测和强制下线功能

### 7.2 API安全防护
- **请求限流**：基于IP和用户的API调用频率限制
- **输入验证**：严格的参数校验和数据清洗
- **XSS防护**：对用户输入进行HTML转义和内容过滤
- **CSRF防护**：使用CSRF Token验证请求来源
- **SQL注入防护**：使用参数化查询和ORM框架

### 7.3 数据安全
- **密码加密**：使用bcrypt进行密码哈希存储
- **敏感数据加密**：对API密钥等敏感信息进行加密存储
- **数据备份**：定期自动备份数据库
- **访问日志**：记录所有API访问和操作日志

---

八、错误处理与异常管理

### 8.1 错误分类
- **客户端错误（4xx）**：参数错误、权限不足、资源不存在等
- **服务器错误（5xx）**：系统异常、第三方服务异常、数据库连接失败等
- **业务逻辑错误**：AI服务调用失败、消息发送失败等

### 8.2 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "参数验证失败",
    "details": {
      "field": "username",
      "reason": "用户名长度必须在3-50个字符之间"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456789"
}
```

### 8.3 异常监控
- **日志记录**：结构化日志记录，便于问题排查
- **错误上报**：集成错误监控服务（如Sentry）
- **性能监控**：API响应时间和系统资源监控
- **告警机制**：关键错误实时告警通知

---

九、性能优化方案

### 9.1 缓存策略
- **Redis缓存**：用户会话、AI角色配置、热门对话缓存
- **浏览器缓存**：静态资源缓存策略设置
- **CDN加速**：全球内容分发网络加速
- **数据库查询缓存**：频繁查询结果缓存

### 9.2 数据库优化
- **索引优化**：为常用查询字段创建合适索引
- **分页查询**：大数据量查询使用游标分页
- **连接池管理**：合理配置数据库连接池大小
- **读写分离**：高并发场景下的主从数据库架构

### 9.3 API性能优化
- **异步处理**：AI对话使用异步处理提升响应速度
- **请求合并**：批量操作接口减少网络请求
- **响应压缩**：启用Gzip压缩减少传输数据量
- **负载均衡**：多实例部署和负载均衡配置

---

## 十、部署架构与上线要求

### 10.1 🌐 生产环境部署方案

| 服务层级 | 部署平台 | 技术栈 | 2025年优势 |
|---------|---------|--------|------------|
| **前端应用** | Vercel | Vue3 + Vite + TypeScript | Edge网络加速，全球CDN分发 |
| **后端API** | Render | Python + FastAPI + uvicorn | 自动扩容，容器化部署 |
| **数据库** | Supabase | PostgreSQL + 实时订阅 | 托管服务，自动备份恢复 |
| **AI服务** | 阿里云 | 通义千问API | 国内低延迟，合规性保障 |

### 10.2 🔧 环境变量配置清单

#### 后端服务配置 (.env)
```bash
# 数据库连接
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# JWT认证配置
JWT_SECRET_KEY=your-super-secret-jwt-key-2025
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 阿里通义千问API配置
ALI_QWEN_API_KEY=sk-your-qwen-api-key
ALI_QWEN_MODEL=qwen-turbo  # 2025年推荐模型
ALI_QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1/

# 跨域与安全配置
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
ALLOWED_HOSTS=your-backend.render.com
ENVIRONMENT=production
```

#### 前端应用配置 (.env.production)
```bash
# API服务地址
VITE_API_BASE_URL=https://your-backend.render.com
VITE_WS_BASE_URL=wss://your-backend.render.com

# Supabase客户端配置
VITE_SUPABASE_URL=https://[project].supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key

# 应用配置
VITE_APP_TITLE=AI智能聊天平台
VITE_APP_VERSION=1.0.0
```

---

十一、开发流程与测试

### 11.1 开发流程
1. **需求分析**：明确功能需求和技术方案
2. **接口设计**：定义API接口和数据结构
3. **数据库设计**：设计表结构和关系
4. **前后端开发**：并行开发前端和后端功能
5. **集成测试**：前后端联调和功能测试
6. **部署上线**：生产环境部署和监控

### 11.2 测试策略
**单元测试**
- 后端API接口测试
- 数据库操作测试
- 工具函数测试

**集成测试**
- 前后端接口联调
- 第三方服务集成测试
- 数据库事务测试

**端到端测试**
- 用户注册登录流程
- AI对话完整流程
- 聊天记录管理功能

### 11.3 质量保证
- **代码审查**：Pull Request代码审查机制
- **自动化测试**：CI/CD流水线集成测试
- **性能测试**：API响应时间和并发测试
- **安全测试**：漏洞扫描和渗透测试

---

### 10.3 🔍 监控与运维体系

#### 性能监控矩阵
| 监控维度 | 工具方案 | 关键指标 | 2025年特色 |
|---------|---------|---------|------------|
| **前端性能** | Vercel Analytics + Web Vitals | LCP, FID, CLS, 页面加载时间 | 实时用户体验监控 |
| **后端性能** | Render Metrics + FastAPI内置 | 响应时间, QPS, 错误率 | 自动扩容触发监控 |
| **数据库性能** | Supabase Dashboard | 连接数, 查询性能, 存储使用 | 实时查询分析 |
| **AI服务监控** | 阿里云监控 | Token消耗, 调用延迟, 成功率 | 智能成本优化建议 |

#### 日志与告警策略
```python
# 结构化日志配置 (Python)
import structlog

logger = structlog.get_logger()
logger.info(
    "ai_chat_request",
    user_id=user_id,
    role_id=role_id,
    tokens_used=tokens,
    response_time_ms=response_time,
    timestamp=datetime.utcnow().isoformat()
)
```

---

## 📁 项目目录结构

### 🎯 整体项目架构

```
ChatGalaxy/
├── frontend/                    # Vue3 前端项目
│   ├── public/                  # 静态资源
│   │   ├── favicon.ico
│   │   └── index.html
│   ├── src/                     # 源代码目录
│   │   ├── assets/              # 静态资源
│   │   │   ├── images/          # 图片资源
│   │   │   ├── icons/           # 图标文件
│   │   │   └── styles/          # 全局样式
│   │   │       ├── main.css     # 主样式文件
│   │   │       ├── variables.css # CSS变量定义
│   │   │       └── themes.css   # 主题色方案
│   │   ├── components/          # 公共组件
│   │   │   ├── common/          # 通用组件
│   │   │   │   ├── Header.vue   # 页面头部
│   │   │   │   ├── Footer.vue   # 页面底部
│   │   │   │   └── Loading.vue  # 加载组件
│   │   │   ├── chat/            # 聊天相关组件
│   │   │   │   ├── ChatWindow.vue    # 聊天窗口
│   │   │   │   ├── MessageBubble.vue # 消息气泡
│   │   │   │   ├── InputBox.vue      # 输入框
│   │   │   │   └── RoleSelector.vue  # 角色选择器
│   │   │   └── user/            # 用户相关组件
│   │   │       ├── LoginForm.vue     # 登录表单
│   │   │       ├── RegisterForm.vue  # 注册表单
│   │   │       └── UserProfile.vue   # 用户资料
│   │   ├── views/               # 页面视图
│   │   │   ├── Home.vue         # 首页/聊天界面
│   │   │   ├── Login.vue        # 登录页面
│   │   │   ├── Register.vue     # 注册页面
│   │   │   ├── Profile.vue      # 个人中心
│   │   │   └── History.vue      # 聊天历史
│   │   ├── router/              # 路由配置
│   │   │   └── index.ts         # 路由定义
│   │   ├── store/               # 状态管理
│   │   │   ├── index.ts         # Pinia store入口
│   │   │   ├── auth.ts          # 用户认证状态
│   │   │   ├── chat.ts          # 聊天状态管理
│   │   │   └── ui.ts            # UI状态管理
│   │   ├── services/            # API服务
│   │   │   ├── api.ts           # API基础配置
│   │   │   ├── auth.ts          # 认证相关API
│   │   │   ├── chat.ts          # 聊天相关API
│   │   │   └── websocket.ts     # WebSocket连接
│   │   ├── utils/               # 工具函数
│   │   │   ├── request.ts       # HTTP请求封装
│   │   │   ├── storage.ts       # 本地存储工具
│   │   │   └── validators.ts    # 表单验证
│   │   ├── types/               # TypeScript类型定义
│   │   │   ├── api.ts           # API接口类型
│   │   │   ├── user.ts          # 用户相关类型
│   │   │   └── chat.ts          # 聊天相关类型
│   │   ├── App.vue              # 根组件
│   │   └── main.ts              # 应用入口
│   ├── package.json             # 依赖配置
│   ├── vite.config.ts           # Vite配置
│   ├── tsconfig.json            # TypeScript配置
│   ├── tailwind.config.js       # TailwindCSS配置
│   └── .env.example             # 环境变量示例
├── backend/                     # FastAPI 后端项目
│   ├── app/                     # 应用核心代码
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── chat.py          # 聊天模型
│   │   │   └── role.py          # 角色模型
│   │   ├── schemas/             # Pydantic数据验证
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # 用户数据结构
│   │   │   ├── chat.py          # 聊天数据结构
│   │   │   └── auth.py          # 认证数据结构
│   │   ├── api/                 # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证相关API
│   │   │   ├── chat.py          # 聊天相关API
│   │   │   ├── roles.py         # 角色管理API
│   │   │   └── websocket.py     # WebSocket处理
│   │   ├── services/            # 业务逻辑服务
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # 认证服务
│   │   │   ├── chat_service.py  # 聊天服务
│   │   │   └── ai_service.py    # AI集成服务
│   │   ├── utils/               # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── security.py      # 安全相关工具
│   │   │   ├── dependencies.py  # 依赖注入
│   │   │   └── exceptions.py    # 异常处理
│   │   └── middleware/          # 中间件
│   │       ├── __init__.py
│   │       ├── cors.py          # 跨域处理
│   │       └── auth.py          # 认证中间件
│   ├── tests/                   # 测试文件
│   │   ├── __init__.py
│   │   ├── test_auth.py         # 认证测试
│   │   ├── test_chat.py         # 聊天测试
│   │   └── conftest.py          # 测试配置
│   ├── alembic/                 # 数据库迁移
│   │   ├── versions/            # 迁移版本
│   │   ├── env.py               # 迁移环境
│   │   └── alembic.ini          # 迁移配置
│   ├── requirements.txt         # Python依赖
│   ├── Dockerfile               # Docker配置
│   ├── .env.example             # 环境变量示例
│   └── README.md                # 后端说明文档
├── database/                    # 数据库相关
│   ├── migrations/              # 数据库迁移文件
│   ├── seeds/                   # 初始数据
│   │   ├── roles.sql            # AI角色初始数据
│   │   └── users.sql            # 测试用户数据
│   └── schema.sql               # 数据库结构
├── docs/                        # 项目文档
│   ├── api.md                   # API文档
│   ├── deployment.md            # 部署指南
│   └── development.md           # 开发指南
├── docker-compose.yml           # Docker编排
├── .gitignore                   # Git忽略文件
├── README.md                    # 项目说明
└── LICENSE                      # 开源协议
```

### 🔧 核心配置文件说明

#### 前端配置 (frontend/)
- **vite.config.ts**: Vite构建工具配置，包含代理设置和构建优化
- **tailwind.config.js**: TailwindCSS配置，定义主题色和响应式断点
- **tsconfig.json**: TypeScript编译配置，严格类型检查
- **.env.production**: 生产环境变量，API地址和Supabase配置

#### 后端配置 (backend/)
- **app/config.py**: 应用配置管理，环境变量读取和验证
- **requirements.txt**: Python依赖包列表，包含FastAPI、SQLAlchemy等
- **alembic.ini**: 数据库迁移工具配置
- **Dockerfile**: 容器化部署配置

---

## 🎯 2025年技术栈优势总结

### ✅ 技术选型前瞻性验证

本项目采用的技术栈完全符合**2025年中国主流技术趋势**：

1. **🔥 前端技术领先性**
   - **Vue 3 + TypeScript**: 2025年企业级前端首选，Composition API提供更好的逻辑复用
   - **Element Plus**: 中文生态最完善的Vue3组件库，企业级项目标配
   - **TailwindCSS**: 原子化CSS框架，2025年设计系统构建趋势

2. **⚡ 后端架构现代化**
   - **Python + FastAPI**: AI时代最热门组合，异步性能媲美Node.js
   - **Pydantic**: 数据验证与序列化标准，类型安全保障
   - **Supabase**: 现代化BaaS服务，PostgreSQL + 实时功能

3. **🤖 AI集成本土化**
   - **阿里通义千问**: 国产AI大模型领军者，中文理解能力卓越
   - **合规性优势**: 符合国内数据安全法规要求
   - **成本效益**: 相比国外服务更具价格优势

4. **🚀 部署方案云原生**
   - **Vercel + Render**: 全球化部署，自动扩容
   - **前后端分离**: 技术栈独立演进，团队协作高效
   - **容器化就绪**: 支持Docker部署，云原生架构

### 📈 市场前景与技术价值

- **技术生态成熟度**: Vue3生态在2025年已完全成熟，社区活跃度高
- **人才市场匹配**: Python+Vue技术栈人才储备充足，招聘成本可控
- **长期维护性**: 所选技术均为长期支持版本，技术债务风险低
- **扩展能力**: 架构设计支持微服务拆分，业务增长适应性强

**结论**: 本项目技术选型具备2025年主流技术的所有特征，既保证了技术先进性，又确保了项目的可持续发展能力。
