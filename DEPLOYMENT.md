# ChatGalaxy 部署指南

## 项目概述

ChatGalaxy 是一个基于 Vue3 + FastAPI 的 AI 聊天平台，支持多角色对话、实时通信和用户认证。

## 部署架构

- **前端**: Vercel (已部署)
- **后端**: Render
- **数据库**: Supabase
- **AI服务**: 阿里通义千问

## 前端部署 (Vercel) ✅ 已完成

前端已成功部署到 Vercel:
- **预览地址**: https://traei69dx9j4-yaomh10-1706-sobers.vercel.app
- **配置文件**: `vercel.json`
- **环境变量**: `.env.production`

### 前端环境变量配置

在 Vercel 控制台中设置以下环境变量:

```bash
VITE_API_BASE_URL=https://your-backend-domain.onrender.com
VITE_WS_URL=wss://your-backend-domain.onrender.com/ws
VITE_APP_NAME=ChatGalaxy
VITE_APP_VERSION=1.0.0
VITE_DEV_MODE=false
```

## 后端部署 (Render)

### 1. 准备工作

确保以下文件存在:
- `requirements.txt` - Python 依赖
- `render.yaml` - Render 部署配置
- `.env` - 环境变量模板

### 2. 在 Render 上创建服务

1. 访问 [Render](https://render.com)
2. 连接 GitHub 仓库
3. 选择 "Web Service"
4. 配置构建和启动命令:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. 环境变量配置

在 Render 控制台中设置以下环境变量:

#### 必需的环境变量

```bash
# Supabase 配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT 配置
JWT_SECRET_KEY=your_jwt_secret_key_at_least_32_characters_long

# AI 服务配置
QWEN_API_KEY=your_qwen_api_key

# CORS 配置
CORS_ORIGINS=https://traei69dx9j4-yaomh10-1706-sobers.vercel.app
```

#### 可选的环境变量

```bash
APP_NAME=ChatGalaxy
APP_VERSION=1.0.0
DEBUG=false
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
QWEN_MODEL=qwen-turbo
QWEN_MAX_TOKENS=2000
QWEN_TEMPERATURE=0.7
LOG_LEVEL=INFO
```

## 数据库部署 (Supabase)

### 1. 创建 Supabase 项目

1. 访问 [Supabase](https://supabase.com)
2. 创建新项目
3. 记录项目 URL 和 API 密钥

### 2. 运行数据库迁移

```bash
# 在本地运行迁移脚本
cd supabase/migrations
# 执行 001_initial_schema.sql
# 执行 002_update_schema.sql
```

### 3. 配置 RLS (行级安全)

确保为所有表启用 RLS 并设置适当的策略。

## 环境变量获取指南

### Supabase 配置

1. 登录 Supabase 控制台
2. 选择项目 → Settings → API
3. 复制:
   - Project URL → `SUPABASE_URL`
   - anon public → `SUPABASE_ANON_KEY`
   - service_role secret → `SUPABASE_SERVICE_ROLE_KEY`

### 阿里通义千问 API

1. 访问 [阿里云控制台](https://dashscope.console.aliyun.com/)
2. 开通通义千问服务
3. 获取 API Key → `QWEN_API_KEY`

### JWT 密钥生成

```bash
# 生成安全的 JWT 密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 部署后验证

### 1. 后端健康检查

```bash
curl https://your-backend-domain.onrender.com/api/system/health
```

### 2. 前端访问测试

访问前端地址，测试:
- 页面加载
- 用户注册/登录
- AI 对话功能
- WebSocket 连接

### 3. API 接口测试

```bash
# 测试认证接口
curl -X POST https://your-backend-domain.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# 测试聊天接口
curl -X GET https://your-backend-domain.onrender.com/api/chat/roles
```

## 常见问题

### 1. CORS 错误

确保后端 `CORS_ORIGINS` 包含前端域名:
```bash
CORS_ORIGINS=https://traei69dx9j4-yaomh10-1706-sobers.vercel.app
```

### 2. WebSocket 连接失败

检查前端 WebSocket URL 配置:
```bash
VITE_WS_URL=wss://your-backend-domain.onrender.com/ws
```

### 3. 数据库连接错误

验证 Supabase 配置和网络连接。

### 4. AI 服务调用失败

检查通义千问 API Key 和配额。

## 监控和维护

- **Render**: 查看服务日志和性能指标
- **Vercel**: 监控部署状态和访问统计
- **Supabase**: 监控数据库性能和存储使用

## 更新部署

### 前端更新

1. 推送代码到 GitHub
2. Vercel 自动触发重新部署

### 后端更新

1. 推送代码到 GitHub
2. Render 自动触发重新部署
3. 检查服务状态和日志

---

**部署完成后，ChatGalaxy AI 聊天平台即可正式上线使用！**