<div align="center">
  <h1>🌌 ChatGalaxy</h1>
  <p><strong>基于2025年主流技术栈的智能AI聊天平台</strong></p>
  
  <!-- 技术栈徽章 -->
  <p>
    <img src="https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=flat-square&logo=vue.js" alt="Vue.js">
    <img src="https://img.shields.io/badge/TypeScript-5.8-3178C6?style=flat-square&logo=typescript" alt="TypeScript">
    <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-17-336791?style=flat-square&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License">
  </p>
  
  <!-- CI/CD 状态徽章 -->
  <p>
    <img src="https://github.com/Soberis/ChatGalaxy/workflows/Frontend%20CI/badge.svg" alt="Frontend CI">
    <img src="https://github.com/Soberis/ChatGalaxy/workflows/Backend%20CI/badge.svg" alt="Backend CI">
    <img src="https://github.com/Soberis/ChatGalaxy/workflows/Deploy/badge.svg" alt="Deploy">
    <img src="https://github.com/Soberis/ChatGalaxy/workflows/Quality%20Checks/badge.svg" alt="Quality">
    <img src="https://github.com/Soberis/ChatGalaxy/workflows/Security%20Scanning/badge.svg" alt="Security">
  </p>
  
  <!-- 代码质量和部署状态 -->
  <p>
    <img src="https://codecov.io/gh/Soberis/ChatGalaxy/branch/main/graph/badge.svg" alt="Coverage">
    <img src="https://sonarcloud.io/api/project_badges/measure?project=Soberis_ChatGalaxy&metric=alert_status" alt="Quality Gate">
    <img src="https://api.netlify.com/api/v1/badges/your-site-id/deploy-status" alt="Netlify Status">
    <img src="https://img.shields.io/github/deployments/Soberis/ChatGalaxy/production?label=vercel&logo=vercel" alt="Vercel">
  </p>
  
  <!-- 项目统计 -->
  <p>
    <img src="https://img.shields.io/github/stars/Soberis/ChatGalaxy?style=flat-square" alt="Stars">
    <img src="https://img.shields.io/github/forks/Soberis/ChatGalaxy?style=flat-square" alt="Forks">
    <img src="https://img.shields.io/github/issues/Soberis/ChatGalaxy?style=flat-square" alt="Issues">
    <img src="https://img.shields.io/github/last-commit/Soberis/ChatGalaxy?style=flat-square" alt="Last Commit">
    <img src="https://img.shields.io/github/languages/top/Soberis/ChatGalaxy?style=flat-square" alt="Top Language">
  </p>
  
  <p>
    <a href="#功能特性">功能特性</a> •
    <a href="#技术栈">技术栈</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#部署指南">部署指南</a> •
    <a href="#贡献指南">贡献指南</a>
  </p>
</div>

---

## 📋 项目概述

ChatGalaxy 是一个现代化的AI聊天平台，采用2025年最流行的技术栈构建。用户可以与多种AI角色进行实时对话，支持用户注册、聊天记录保存、实时消息推送等功能。项目采用前后端分离架构，具备优秀的可扩展性和维护性。

### ✨ 核心亮点

- 🤖 **多角色AI对话** - 支持智能助手、创意作家、技术专家等多种AI角色
- 💬 **实时通信** - 基于WebSocket的实时消息推送和流式响应
- 👤 **用户系统** - 完整的用户注册、登录、认证体系
- 📚 **聊天记录** - 持久化存储用户聊天历史，支持会话管理
- 📱 **响应式设计** - 完美适配桌面端、平板和移动设备
- 🚀 **现代化部署** - 支持云原生部署，自动扩缩容

## 🛠️ 技术栈

### 前端技术
- **框架**: Vue 3.5 + TypeScript 5.8
- **构建工具**: Vite 7.0
- **UI组件**: Element Plus 2.10 + TailwindCSS 3.4
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **实时通信**: WebSocket API
- **测试框架**: Vitest + Vue Test Utils

### 后端技术
- **框架**: Python 3.11 + FastAPI 0.104
- **数据验证**: Pydantic 2.5
- **服务器**: uvicorn 0.24
- **数据库**: PostgreSQL 17 (Supabase)
- **认证**: JWT Token + Supabase Auth
- **AI服务**: 阿里通义千问 (Qwen) API
- **测试框架**: Pytest + Coverage

### DevOps & CI/CD
- **版本控制**: Git + GitHub
- **CI/CD**: GitHub Actions (2025标准)
- **代码质量**: ESLint, Prettier, SonarCloud
- **安全扫描**: Snyk, Bandit, Safety
- **测试覆盖**: Codecov集成
- **容器化**: Docker + Multi-stage builds

### 部署架构
- **前端**: Vercel (已部署) [![Vercel](https://img.shields.io/badge/Vercel-Live-00C7B7?style=flat-square&logo=vercel)](https://traei69dx9j4-yaomh10-1706-sobers.vercel.app)
- **后端**: Render (配置就绪)
- **数据库**: Supabase (云托管)
- **CDN**: 全球加速
- **监控**: 实时性能监控

## 🎯 功能特性

### 核心功能
- ✅ AI智能对话 - 支持多轮对话和上下文理解
- ✅ 多角色切换 - 4种预设AI角色，满足不同场景需求
- ✅ 实时消息显示 - WebSocket实时推送，流式响应体验
- ✅ 用户认证系统 - 注册、登录、密码重置
- ✅ 聊天记录管理 - 会话创建、历史查看、记录清理
- ✅ 响应式界面 - 适配各种设备尺寸

### AI角色类型
1. **智能助手** - 通用AI助手，回答各类问题
2. **创意作家** - 专注创意写作和文学创作
3. **技术专家** - 专业技术问答和代码解析
4. **轻松聊天** - 轻松愉快的日常对话

### 用户类型
- **访客用户** - 可直接体验AI对话，无法保存记录
- **注册用户** - 完整功能体验，聊天记录持久化
- **管理员** - 系统管理和用户管理权限

## 🚀 快速开始

### 环境要求
- Node.js 20.16.0+
- Python 3.11+
- PostgreSQL 17+ (或使用Supabase)
- pnpm (推荐) 或 npm

### 1. 克隆项目
```bash
git clone https://github.com/your-username/ChatGalaxy.git
cd ChatGalaxy
```

### 2. 前端设置
```bash
cd frontend
pnpm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 启动开发服务器
pnpm dev
```

### 3. 后端设置
```bash
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入数据库和AI服务配置

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 数据库设置

#### 使用Supabase (推荐)
1. 在 [Supabase](https://supabase.com) 创建新项目
2. 获取项目URL和API密钥
3. 运行数据库迁移脚本

#### 本地PostgreSQL
```bash
# 创建数据库
createdb chatgalaxy

# 运行迁移
psql -d chatgalaxy -f migrations/init.sql
```

### 5. 访问应用
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📦 项目结构

```
ChatGalaxy/
├── frontend/                 # Vue3前端项目
│   ├── src/
│   │   ├── components/      # 可复用组件
│   │   ├── views/          # 页面组件
│   │   ├── services/       # API服务层
│   │   ├── stores/         # Pinia状态管理
│   │   └── router/         # 路由配置
│   ├── public/             # 静态资源
│   └── package.json
├── backend/                  # FastAPI后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── websocket/      # WebSocket处理
│   └── requirements.txt
├── supabase/                # 数据库配置
│   └── migrations/         # 数据库迁移文件
├── .trae/                   # 项目文档
│   └── documents/
└── README.md
```

## 🌐 部署指南

### 前端部署 (Vercel)

1. **连接GitHub仓库**
   - 登录 [Vercel](https://vercel.com)
   - 导入GitHub仓库
   - 选择 `frontend` 目录作为根目录

2. **配置环境变量**
   ```
   VITE_API_BASE_URL=https://your-backend-url.com
   VITE_WS_BASE_URL=wss://your-backend-url.com
   VITE_SUPABASE_URL=your-supabase-url
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

3. **部署设置**
   - 构建命令: `pnpm build`
   - 输出目录: `dist`
   - Node.js版本: 20.x

### 后端部署 (Render)

1. **创建Web Service**
   - 连接GitHub仓库
   - 选择 `backend` 目录
   - 运行时: Python 3.11

2. **配置环境变量**
   ```
   DATABASE_URL=your-postgresql-url
   SUPABASE_URL=your-supabase-url
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   QWEN_API_KEY=your-qwen-api-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

3. **部署命令**
   ```bash
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### 数据库部署 (Supabase)

1. **创建项目**
   - 访问 [Supabase Dashboard](https://app.supabase.com)
   - 创建新项目
   - 选择地区 (推荐: Singapore)

2. **运行迁移**
   ```bash
   # 使用Supabase CLI
   supabase db push
   
   # 或手动执行SQL
   # 在Supabase SQL编辑器中运行 migrations/ 目录下的SQL文件
   ```

3. **配置RLS策略**
   - 启用行级安全 (Row Level Security)
   - 配置用户权限策略

## 🔧 开发指南

### 代码规范
- 使用 ESLint + Prettier 进行代码格式化
- 遵循 Vue 3 Composition API 最佳实践
- TypeScript 严格模式开发
- 提交信息遵循 Conventional Commits 规范

### CI/CD 工作流

项目配置了完整的GitHub Actions CI/CD流程，包含以下工作流：

#### 🔄 前端CI (`frontend.yml`)
- **触发条件**: 前端代码变更、PR创建
- **检查项目**: TypeScript类型检查、ESLint代码分析、单元测试、构建验证
- **覆盖率**: 自动生成测试覆盖率报告并上传Codecov
- **多版本**: 支持Node.js 20.16.0和22.12.0测试

#### 🐍 后端CI (`backend.yml`)
- **触发条件**: 后端代码变更、PR创建
- **检查项目**: Ruff代码检查、MyPy类型检查、Bandit安全扫描
- **测试环境**: Python 3.11/3.12 + PostgreSQL集成测试
- **性能测试**: 包含API性能基准测试和负载测试

#### 🚀 自动部署 (`deploy.yml`)
- **前端部署**: 自动部署到Vercel，包含构建优化和CDN配置
- **后端部署**: 自动部署到Render，包含健康检查和回滚机制
- **集成测试**: 部署后自动执行端到端测试验证

#### 🔍 代码质量 (`quality.yml`)
- **代码分析**: SonarCloud集成，全面的代码质量分析
- **覆盖率监控**: 前后端测试覆盖率统计和趋势分析
- **性能预算**: 前端包大小监控和性能预算检查

#### 🛡️ 安全扫描 (`security.yml`)
- **依赖扫描**: 使用Snyk、Safety等工具检测依赖漏洞
- **代码安全**: Bandit、ESLint安全插件检测安全问题
- **容器安全**: Trivy和Docker Scout容器镜像安全扫描
- **敏感信息**: TruffleHog和GitLeaks检测敏感数据泄露

#### 🔒 PR检查 (`pr-checks.yml`)
- **PR验证**: 标题格式、描述完整性、文件变更范围检查
- **自动标签**: 根据变更内容自动添加相应标签
- **分支保护**: 强制代码审查和状态检查通过
- **命令支持**: 支持`/rerun-ci`、`/ready-for-review`等PR命令

### 测试
```bash
# 前端测试
cd frontend
pnpm test              # 单元测试
pnpm test:coverage     # 覆盖率测试
pnpm test:e2e          # 端到端测试

# 后端测试
cd backend
pytest                 # 单元测试
pytest --cov          # 覆盖率测试
pytest tests/integration  # 集成测试
```

### 构建
```bash
# 前端构建
cd frontend
pnpm build             # 生产构建
pnpm build:analyze     # 构建分析
pnpm preview           # 预览构建结果

# 后端无需构建，直接运行
# Docker构建
docker build -t chatgalaxy-backend ./backend
```

### 本地开发工作流

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   ```bash
   # 启动开发环境
   pnpm dev              # 前端
   python -m uvicorn app.main:app --reload  # 后端
   
   # 运行测试
   pnpm test             # 前端测试
   pytest                # 后端测试
   ```

3. **代码检查**
   ```bash
   # 前端代码检查
   pnpm lint             # ESLint检查
   pnpm format           # Prettier格式化
   pnm type-check        # TypeScript检查
   
   # 后端代码检查
   ruff check .          # 代码规范检查
   mypy .                # 类型检查
   bandit -r .           # 安全检查
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat(frontend): add new chat interface"
   git push origin feature/your-feature-name
   ```

5. **创建PR**
   - GitHub会自动触发CI/CD检查
   - 确保所有检查通过后请求代码审查
   - 合并到main分支后自动部署

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献指南

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献流程。

### 贡献流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ChatGalaxy/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/ChatGalaxy/discussions)

## 🙏 致谢

感谢以下开源项目和服务：

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [TailwindCSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [Supabase](https://supabase.com/) - 开源Firebase替代方案
- [Vercel](https://vercel.com/) - 前端部署平台
- [Render](https://render.com/) - 云应用平台

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给它一个星标！</p>
  <p>Made with ❤️ by ChatGalaxy Team</p>
</div>