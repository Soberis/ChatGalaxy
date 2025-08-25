# Assets 资源目录

本目录用于存放 ChatGalaxy 项目的静态资源文件。

## 📁 目录结构

```
assets/
├── README.md           # 本文件，资源目录说明
├── screenshots/        # 项目截图目录
│   ├── desktop/       # 桌面端截图
│   ├── mobile/        # 移动端截图
│   └── features/      # 功能特性截图
├── logos/             # 项目 Logo 文件
├── icons/             # 图标文件
└── badges/            # 徽章配置文件
```

## 📸 截图规范

### 桌面端截图 (desktop/)

- `home-page.png` - 主页面截图
- `chat-interface.png` - 聊天界面截图
- `auth-form.png` - 登录注册界面截图
- `user-profile.png` - 用户资料页面截图

### 移动端截图 (mobile/)

- `mobile-home.png` - 移动端主页
- `mobile-chat.png` - 移动端聊天界面
- `mobile-auth.png` - 移动端登录界面

### 功能特性截图 (features/)

- `ai-roles.png` - AI 角色切换功能
- `real-time-chat.png` - 实时聊天功能
- `message-history.png` - 聊天记录功能
- `responsive-design.png` - 响应式设计展示

## 🏷️ 项目徽章配置

以下是推荐在 README.md 中使用的项目徽章：

### 技术栈徽章

```markdown
![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Element Plus](https://img.shields.io/badge/Element_Plus-409EFF?style=for-the-badge&logo=element&logoColor=white)
```

### 部署状态徽章

```markdown
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
```

### 项目状态徽章

```markdown
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-green.svg?style=for-the-badge)
```

### 代码质量徽章

```markdown
![Code Style](https://img.shields.io/badge/Code_Style-Prettier-ff69b4.svg?style=for-the-badge)
![Linting](https://img.shields.io/badge/Linting-ESLint-4B32C3.svg?style=for-the-badge)
```

## 🎨 Logo 和图标规范

### Logo 文件 (logos/)

- `logo.png` - 主 Logo（矢量格式）
- `logo.png` - 主 Logo（PNG 格式，1024x1024）
- `logo-light.svg` - 浅色主题 Logo
- `logo-dark.svg` - 深色主题 Logo
- `favicon.ico` - 网站图标

### 图标文件 (icons/)

- `app-icon-192.png` - PWA 应用图标 (192x192)
- `app-icon-512.png` - PWA 应用图标 (512x512)
- `apple-touch-icon.png` - iOS 应用图标 (180x180)

## 📝 使用说明

1. **添加截图**: 将新的截图文件放入对应的子目录中
2. **更新 README**: 在主 README.md 中引用截图文件
3. **优化图片**: 确保图片文件大小适中，推荐使用 WebP 格式
4. **命名规范**: 使用小写字母和连字符，如 `chat-interface.png`

## 🔗 在 README 中引用截图

```markdown
## 📸 项目截图

### 桌面端

![主页面](./assets/screenshots/desktop/home-page.png)
![聊天界面](./assets/screenshots/desktop/chat-interface.png)

### 移动端

<div align="center">
  <img src="./assets/screenshots/mobile/mobile-home.png" width="300" alt="移动端主页">
  <img src="./assets/screenshots/mobile/mobile-chat.png" width="300" alt="移动端聊天">
</div>
```

## 📊 文件大小建议

- **截图文件**: 建议不超过 500KB
- **Logo 文件**: SVG 格式优先，PNG 不超过 100KB
- **图标文件**: 根据规格要求，保持清晰度

---

**注意**: 请确保所有上传的图片都是项目相关的，并且拥有适当的使用权限。
