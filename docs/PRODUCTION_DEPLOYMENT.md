# ChatGalaxy 生产环境部署配置指南

## 📋 概述

本文档详细说明了将ChatGalaxy项目部署到生产服务器时需要调整的配置项，包括环境变量、API端点、数据库连接等关键配置。

## 🔧 前端配置调整

### 环境变量配置

**开发环境 (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=ChatGalaxy
VITE_APP_VERSION=1.0.0
VITE_DEV_MODE=true
```

**生产环境配置**
```bash
# Vercel环境变量设置
VITE_API_BASE_URL=https://your-backend-domain.onrender.com
VITE_WS_URL=wss://your-backend-domain.onrender.com/ws
VITE_APP_NAME=ChatGalaxy
VITE_APP_VERSION=1.0.0
VITE_DEV_MODE=false

# Supabase配置（如果前端直接使用）
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Vercel部署配置

**需要在Vercel控制台设置的环境变量：**
- `VITE_API_BASE_URL`: 后端API的生产环境URL
- `VITE_WS_URL`: WebSocket连接的生产环境URL
- `VITE_SUPABASE_URL`: Supabase项目URL
- `VITE_SUPABASE_ANON_KEY`: Supabase匿名访问密钥

## 🚀 后端配置调整

### 环境变量配置

**关键生产环境变量：**

```bash
# 应用程序配置
APP_NAME=ChatGalaxy
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# 服务器配置
HOST=0.0.0.0
PORT=8000  # Render会自动设置$PORT

# Supabase配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT配置
JWT_SECRET_KEY=your_very_long_and_secure_secret_key_at_least_32_characters
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI服务配置
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-turbo
QWEN_MAX_TOKENS=2000
QWEN_TEMPERATURE=0.7

# 跨域配置（重要！）
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://chatgalaxy.vercel.app

# WebSocket配置
WS_HEARTBEAT_INTERVAL=30
WS_HEARTBEAT_TIMEOUT=60
WS_MAX_CONNECTIONS=1000

# 安全配置
ALLOWED_HOSTS=your-backend-domain.onrender.com
TRUSTED_HOSTS=your-backend-domain.onrender.com

# 限流配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# 监控配置
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true

# 日志配置
LOG_LEVEL=INFO
```

### Render部署配置

**需要在Render控制台设置的环境变量：**
- `SUPABASE_URL`: Supabase项目URL
- `SUPABASE_ANON_KEY`: Supabase匿名访问密钥
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务角色密钥
- `QWEN_API_KEY`: 通义千问API密钥
- `JWT_SECRET_KEY`: JWT签名密钥（建议使用Render自动生成）
- `CORS_ORIGINS`: 前端域名列表

## 🔄 部署流程配置调整

### 1. GitHub Actions密钥配置

**需要在GitHub仓库Settings > Secrets中设置：**

**Vercel相关：**
- `VERCEL_TOKEN`: Vercel访问令牌
- `VERCEL_ORG_ID`: Vercel组织ID
- `VERCEL_PROJECT_ID`: Vercel项目ID

**Render相关：**
- `RENDER_API_KEY`: Render API密钥
- `RENDER_SERVICE_ID`: Render服务ID
- `RENDER_SERVICE_URL`: Render服务URL

**应用配置：**
- `VITE_API_BASE_URL`: 生产环境API地址
- `VITE_SUPABASE_URL`: Supabase项目URL
- `VITE_SUPABASE_ANON_KEY`: Supabase匿名密钥

### 2. 分支保护规则

**main分支保护设置：**
- 要求PR审查（至少1个审查者）
- 要求状态检查通过
- 要求分支为最新状态
- 限制推送到匹配分支
- 要求管理员遵循规则

**develop分支保护设置：**
- 要求状态检查通过
- 要求分支为最新状态

## 🗄️ 数据库配置

### Supabase生产环境配置

1. **RLS策略更新**
   - 确保所有表的行级安全策略适用于生产环境
   - 验证匿名用户和认证用户的权限设置

2. **连接池配置**
   - 调整连接池大小适应生产负载
   - 配置连接超时和重试策略

3. **备份策略**
   - 启用自动备份
   - 设置备份保留期限

## 🔒 安全配置

### 1. HTTPS配置
- 前端：Vercel自动提供HTTPS
- 后端：Render自动提供HTTPS
- 确保所有API调用使用HTTPS

### 2. CORS配置
```python
# 生产环境CORS设置
CORS_ORIGINS = [
    "https://your-frontend-domain.vercel.app",
    "https://chatgalaxy.vercel.app"
]
```

### 3. 密钥管理
- 使用强随机密钥
- 定期轮换API密钥
- 不在代码中硬编码密钥

## 📊 监控和日志

### 1. 应用监控
- 启用健康检查端点
- 配置性能监控
- 设置错误报告

### 2. 日志配置
```python
# 生产环境日志设置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🚀 部署检查清单

### 部署前检查
- [ ] 所有环境变量已正确配置
- [ ] API端点已更新为生产地址
- [ ] CORS配置包含正确的前端域名
- [ ] 数据库连接配置正确
- [ ] SSL证书配置完成
- [ ] 安全密钥已设置

### 部署后验证
- [ ] 前端页面正常加载
- [ ] API接口响应正常
- [ ] WebSocket连接正常
- [ ] 用户认证功能正常
- [ ] AI对话功能正常
- [ ] 数据库读写正常
- [ ] 健康检查端点响应正常

## 🔧 故障排除

### 常见问题

1. **CORS错误**
   - 检查后端CORS_ORIGINS配置
   - 确认前端域名正确

2. **API连接失败**
   - 验证VITE_API_BASE_URL配置
   - 检查后端服务状态

3. **WebSocket连接失败**
   - 确认WSS协议使用
   - 检查防火墙设置

4. **数据库连接问题**
   - 验证Supabase配置
   - 检查网络连接

### 调试工具
- Vercel部署日志
- Render应用日志
- 浏览器开发者工具
- Supabase仪表板

---

**注意：** 部署到生产环境前，建议先在测试环境验证所有配置的正确性。