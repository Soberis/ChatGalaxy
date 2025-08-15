<template>
  <div class="home-view">
    <!-- 未登录状态：显示认证表单 -->
    <AuthForm
      v-if="!isAuthenticated"
      @login="handleLogin"
      @register="handleRegister"
      @guest-mode="handleGuestMode"
    />
    
    <!-- 已登录状态：显示聊天界面 -->
    <div v-else class="chat-container">
      <!-- 顶部导航栏 -->
      <header class="chat-header bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center h-16">
            <!-- Logo和标题 -->
            <div class="flex items-center">
              <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center mr-3">
                <el-icon size="20" class="text-white"><ChatDotRound /></el-icon>
              </div>
              <h1 class="text-xl font-bold text-gray-800">ChatGalaxy</h1>
            </div>
            
            <!-- 用户信息和操作 -->
            <div class="flex items-center space-x-4">
              <!-- 当前AI角色显示 -->
              <div class="hidden sm:flex items-center text-sm text-gray-600">
                <el-icon class="mr-1"><User /></el-icon>
                <span>{{ currentRole?.name || '智能助手' }}</span>
              </div>
              
              <!-- 用户菜单 -->
              <el-dropdown @command="handleUserMenuCommand">
                <div class="flex items-center cursor-pointer hover:bg-gray-50 rounded-lg px-3 py-2">
                  <el-avatar :size="32" :src="currentUser?.avatar_url">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  <span class="ml-2 text-sm font-medium text-gray-700 hidden sm:block">
                    {{ currentUser?.username || '访客用户' }}
                  </span>
                  <el-icon class="ml-1 text-gray-400"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile" v-if="!isGuest">
                      <el-icon><User /></el-icon>
                      个人资料
                    </el-dropdown-item>
                    <el-dropdown-item command="history" v-if="!isGuest">
                      <el-icon><Clock /></el-icon>
                      聊天记录
                    </el-dropdown-item>
                    <el-dropdown-item command="settings">
                      <el-icon><Setting /></el-icon>
                      设置
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </header>
      
      <!-- 聊天界面 -->
      <main class="chat-main flex-1 overflow-hidden">
        <ChatInterface
          :current-user="currentUser"
          :is-guest="isGuest"
          @role-change="handleRoleChange"
        />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  User,
  ArrowDown,
  Clock,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import AuthForm from '@/components/AuthForm.vue'
import ChatInterface from '@/components/ChatInterface.vue'
import { AuthService, type User as AuthUser } from '../services/auth'
import { type AIRole } from '../services/chat'

// 用户类型定义（使用认证服务的类型）
type User = AuthUser

// 响应式数据
const currentUser = ref<User | null>(null)
const isGuest = ref(false)
const currentRole = ref<AIRole | null>(null)

// 计算属性
const isAuthenticated = computed(() => {
  return currentUser.value !== null || isGuest.value
})

// AI角色数据
const aiRoles: AIRole[] = [
  {
    id: '1',
    name: '智能助手',
    description: '我是您的智能助手，可以帮助您解答各种问题',
    system_prompt: '你是一个智能助手，请用友好、专业的语气回答用户的问题。',
    is_active: true,
    created_at: new Date().toISOString()
  },
  {
    id: '2',
    name: '创意作家',
    description: '我擅长创作故事、诗歌和各种创意内容',
    system_prompt: '你是一个富有创意的作家，擅长创作各种文学作品和创意内容。',
    is_active: true,
    created_at: new Date().toISOString()
  },
  {
    id: '3',
    name: '技术专家',
    description: '我专注于编程、技术问题和解决方案',
    system_prompt: '你是一个技术专家，专门解答编程和技术相关的问题。',
    is_active: true,
    created_at: new Date().toISOString()
  },
  {
    id: '4',
    name: '轻松聊天',
    description: '让我们轻松愉快地聊天吧',
    system_prompt: '你是一个轻松友好的聊天伙伴，用轻松愉快的语气与用户交流。',
    is_active: true,
    created_at: new Date().toISOString()
  }
]

// 初始化用户状态
const initializeUserState = async () => {
  try {
    // 检查是否有有效的认证状态
    if (AuthService.isAuthenticated()) {
      const userInfo = AuthService.getLocalUser()
      if (userInfo) {
        currentUser.value = userInfo
        isGuest.value = false
        return
      }
    }
    
    // 检查访客模式
    const guestMode = localStorage.getItem('guest_mode')
    const guestUserInfo = localStorage.getItem('guest_user_info')
    
    if (guestMode === 'true' && guestUserInfo) {
      try {
        currentUser.value = JSON.parse(guestUserInfo)
        isGuest.value = true
      } catch (error) {
        console.error('解析访客用户信息失败:', error)
        localStorage.removeItem('guest_mode')
        localStorage.removeItem('guest_user_info')
      }
    }
    
  } catch (error) {
    console.error('初始化用户状态失败:', error)
  }
}

// 监听用户状态变化，保存访客模式信息
watch([currentUser, isGuest], ([user, guest]) => {
  if (guest && user) {
    localStorage.setItem('guest_mode', 'true')
    localStorage.setItem('guest_user_info', JSON.stringify(user))
  } else if (!guest) {
    localStorage.removeItem('guest_mode')
    localStorage.removeItem('guest_user_info')
  }
}, { deep: true })

/**
 * 组件挂载时初始化
 */
onMounted(async () => {
  await initializeUserState()
  
  // 设置默认AI角色
  currentRole.value = aiRoles[0]
})

/**
 * 处理登录
 */
const handleLogin = async (userData: { user: User; token: string }) => {
  currentUser.value = userData.user
  isGuest.value = false
  ElMessage.success(`欢迎回来，${userData.user.username}！`)
}

/**
 * 处理注册
 */
const handleRegister = async (userData: { user: User; token: string }) => {
  currentUser.value = userData.user
  isGuest.value = false
  ElMessage.success(`注册成功，欢迎加入 ChatGalaxy，${userData.user.username}！`)
}

/**
 * 处理访客模式
 */
const handleGuestMode = () => {
  // 创建临时访客用户
  const guestUser: User = {
    id: 'guest_' + Date.now(),
    username: '访客用户',
    email: 'guest@example.com',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
  currentUser.value = guestUser
  isGuest.value = true
  ElMessage.success('已进入访客模式，开始体验 ChatGalaxy！')
}

/**
 * 处理AI角色切换
 */
const handleRoleChange = (role: AIRole) => {
  currentRole.value = role
  ElMessage.success(`已切换到：${role.name}`)
}

/**
 * 处理用户菜单命令
 */
const handleUserMenuCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
      
    case 'history':
      ElMessage.info('聊天记录功能开发中...')
      break
      
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
      
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '确认退出',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        try {
          await AuthService.logout()
          currentUser.value = null
          isGuest.value = false
          currentRole.value = null
          ElMessage.success('已退出登录')
        } catch (error: unknown) {
          console.error('退出登录失败:', error)
          // 即使API调用失败，也清除本地状态
          currentUser.value = null
          isGuest.value = false
          currentRole.value = null
          ElMessage.success('已退出登录')
        }
        
      } catch {
        // 用户取消退出
      }
      break
  }
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.chat-header {
  flex-shrink: 0;
  z-index: 10;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header .max-w-7xl {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .chat-header h1 {
    font-size: 1.125rem;
  }
}

/* 用户菜单样式 */
.el-dropdown {
  outline: none;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}
</style>