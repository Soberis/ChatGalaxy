# 贡献指南

感谢您对 ChatGalaxy 项目的关注！我们欢迎所有形式的贡献，包括但不限于代码、文档、问题报告和功能建议。

## 🤝 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过以下步骤报告：

1. 在 [GitHub Issues](https://github.com/your-username/ChatGalaxy/issues) 中搜索是否已有相关问题
2. 如果没有找到，请创建新的 Issue
3. 使用清晰的标题和详细的描述
4. 如果是 bug 报告，请包含：
   - 操作系统和版本
   - Node.js 和 Python 版本
   - 重现步骤
   - 预期行为和实际行为
   - 错误截图（如适用）

### 提交代码

#### 开发环境设置

1. **Fork 仓库**
   ```bash
   # 克隆您的 fork
   git clone https://github.com/your-username/ChatGalaxy.git
   cd ChatGalaxy
   
   # 添加上游仓库
   git remote add upstream https://github.com/original-owner/ChatGalaxy.git
   ```

2. **安装依赖**
   ```bash
   # 前端依赖
   cd frontend
   pnpm install
   
   # 后端依赖
   cd ../backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

3. **配置环境**
   ```bash
   # 复制环境变量模板
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   
   # 编辑配置文件，填入必要的配置
   ```

#### 开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **进行开发**
   - 遵循项目的代码规范
   - 编写清晰的提交信息
   - 添加必要的测试
   - 更新相关文档

3. **运行测试**
   ```bash
   # 前端测试
   cd frontend
   pnpm test
   pnpm lint
   
   # 后端测试
   cd backend
   pytest
   flake8 .
   black . --check
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **推送并创建 Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   然后在 GitHub 上创建 Pull Request。

## 📝 代码规范

### 前端 (Vue.js + TypeScript)

- 使用 **Composition API** 而不是 Options API
- 遵循 **Vue 3** 最佳实践
- 使用 **TypeScript** 进行类型检查
- 组件文件使用 **PascalCase** 命名
- 使用 **ESLint** 和 **Prettier** 进行代码格式化

```typescript
// ✅ 好的示例
<script setup lang="ts">
import { ref, computed } from 'vue'

interface User {
  id: number
  name: string
}

const user = ref<User | null>(null)
const displayName = computed(() => user.value?.name || 'Guest')
</script>
```

### 后端 (Python + FastAPI)

- 遵循 **PEP 8** 代码风格
- 使用 **Type Hints** 进行类型注解
- 使用 **Pydantic** 进行数据验证
- 函数和变量使用 **snake_case** 命名
- 类使用 **PascalCase** 命名
- 使用 **Black** 进行代码格式化

```python
# ✅ 好的示例
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

async def create_user(user_data: UserCreate) -> Optional[User]:
    """创建新用户
    
    Args:
        user_data: 用户创建数据
        
    Returns:
        创建的用户对象，如果失败则返回 None
    """
    # 实现逻辑
    pass
```

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型 (type):**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

**示例:**
```
feat(chat): add real-time message streaming

fix(auth): resolve JWT token expiration issue

docs: update API documentation for chat endpoints
```

## 🧪 测试指南

### 前端测试

- 使用 **Vitest** 进行单元测试
- 使用 **Vue Test Utils** 进行组件测试
- 测试文件命名：`*.test.ts` 或 `*.spec.ts`

```typescript
// 示例测试
import { mount } from '@vue/test-utils'
import ChatMessage from '@/components/ChatMessage.vue'

describe('ChatMessage', () => {
  it('renders message content correctly', () => {
    const wrapper = mount(ChatMessage, {
      props: {
        message: 'Hello, World!',
        sender: 'user'
      }
    })
    
    expect(wrapper.text()).toContain('Hello, World!')
  })
})
```

### 后端测试

- 使用 **pytest** 进行测试
- 使用 **FastAPI TestClient** 进行 API 测试
- 测试文件命名：`test_*.py`

```python
# 示例测试
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

## 📚 文档贡献

- 更新 README.md 中的相关部分
- 为新功能添加 API 文档
- 更新 CHANGELOG.md
- 确保代码注释清晰易懂

## 🎯 Pull Request 指南

### PR 标题
使用清晰描述性的标题，遵循提交信息规范：
```
feat: add user avatar upload functionality
fix: resolve WebSocket connection issues
docs: update deployment guide
```

### PR 描述
请在 PR 描述中包含：

1. **变更摘要** - 简要描述您的更改
2. **相关 Issue** - 链接到相关的 Issue（如果有）
3. **测试说明** - 描述如何测试您的更改
4. **截图** - 如果是 UI 更改，请提供截图
5. **检查清单** - 确认您已完成必要的步骤

### PR 模板

```markdown
## 变更摘要
简要描述此 PR 的更改内容。

## 相关 Issue
- Closes #123
- Related to #456

## 更改类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 重大更改
- [ ] 文档更新
- [ ] 性能改进
- [ ] 代码重构

## 测试
- [ ] 已添加单元测试
- [ ] 已添加集成测试
- [ ] 手动测试通过
- [ ] 所有现有测试通过

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 自我审查了代码
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 没有引入新的警告
```

## 🔍 代码审查

所有 PR 都需要经过代码审查才能合并。审查者会检查：

- 代码质量和规范
- 功能正确性
- 测试覆盖率
- 文档完整性
- 性能影响

## 🏷️ 版本发布

项目使用 [语义化版本](https://semver.org/) 进行版本管理：

- **MAJOR** (主版本): 不兼容的 API 更改
- **MINOR** (次版本): 向后兼容的功能添加
- **PATCH** (修订版本): 向后兼容的 bug 修复

## 📞 获取帮助

如果您在贡献过程中遇到问题，可以通过以下方式获取帮助：

- 在相关 Issue 中提问
- 在 [GitHub Discussions](https://github.com/your-username/ChatGalaxy/discussions) 中讨论
- 发送邮件至 your-email@example.com

## 🙏 致谢

感谢所有为 ChatGalaxy 项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

再次感谢您的贡献！🎉