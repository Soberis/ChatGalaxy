<template>
  <div class="auth-form max-w-md mx-auto">
    <div class="bg-white rounded-lg shadow-lg p-8">
      <!-- Logo和标题 -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <el-icon size="32" class="text-white"><ChatDotRound /></el-icon>
        </div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">ChatGalaxy</h1>
        <p class="text-gray-600">
          {{ isLogin ? '欢迎回来' : '创建您的账户' }}
        </p>
      </div>

      <!-- 表单切换标签 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="auth-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @submit.prevent="handleLogin"
            class="mt-6"
          >
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                type="email"
                placeholder="邮箱地址"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <div class="flex items-center justify-between w-full">
                <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                <el-button type="text" @click="showForgotPassword = true">
                  忘记密码？
                </el-button>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="w-full"
                :loading="isLoading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            @submit.prevent="handleRegister"
            class="mt-6"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                type="email"
                placeholder="邮箱地址"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="agreement">
              <el-checkbox v-model="registerForm.agreement">
                我已阅读并同意
                <el-button type="text" @click="showTerms = true">用户协议</el-button>
                和
                <el-button type="text" @click="showPrivacy = true">隐私政策</el-button>
              </el-checkbox>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="w-full"
                :loading="isLoading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 访客模式 -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <el-button
          type="text"
          class="w-full text-gray-600 hover:text-primary-500"
          @click="handleGuestMode"
        >
          <el-icon class="mr-2"><UserFilled /></el-icon>
          以访客身份继续
        </el-button>
        <p class="text-xs text-gray-500 text-center mt-2">
          访客模式下的聊天记录不会被保存
        </p>
      </div>
    </div>
    
    <!-- 忘记密码对话框 -->
    <el-dialog v-model="showForgotPassword" title="重置密码" width="400px">
      <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef">
        <el-form-item prop="email">
          <el-input
            v-model="forgotPasswordForm.email"
            type="email"
            placeholder="请输入您的邮箱地址"
            :prefix-icon="Message"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showForgotPassword = false">取消</el-button>
          <el-button type="primary" :loading="isLoading" @click="handleForgotPassword">
            发送重置邮件
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 用户协议对话框 -->
    <el-dialog v-model="showTerms" title="用户协议" width="600px">
      <div class="text-sm text-gray-700 max-h-96 overflow-y-auto">
        <h3 class="font-semibold mb-3">ChatGalaxy 用户协议</h3>
        <p class="mb-3">欢迎使用 ChatGalaxy AI 聊天平台。在使用我们的服务之前，请仔细阅读以下条款：</p>
        <ol class="list-decimal list-inside space-y-2">
          <li>用户应当遵守相关法律法规，不得利用本平台从事违法活动。</li>
          <li>用户对其账户信息的安全性负责，应当妥善保管登录凭证。</li>
          <li>本平台提供的AI对话服务仅供参考，不构成专业建议。</li>
          <li>用户生成的内容应当符合社会公德，不得包含违法违规信息。</li>
          <li>我们保留在必要时暂停或终止服务的权利。</li>
        </ol>
      </div>
    </el-dialog>
    
    <!-- 隐私政策对话框 -->
    <el-dialog v-model="showPrivacy" title="隐私政策" width="600px">
      <div class="text-sm text-gray-700 max-h-96 overflow-y-auto">
        <h3 class="font-semibold mb-3">隐私政策</h3>
        <p class="mb-3">我们重视您的隐私保护，本政策说明我们如何收集、使用和保护您的个人信息：</p>
        <ol class="list-decimal list-inside space-y-2">
          <li>我们仅收集提供服务所必需的个人信息，包括邮箱、用户名等。</li>
          <li>您的聊天记录将被加密存储，仅用于改善服务质量。</li>
          <li>我们不会向第三方出售或泄露您的个人信息。</li>
          <li>您有权随时查看、修改或删除您的个人信息。</li>
          <li>我们采用行业标准的安全措施保护您的数据安全。</li>
        </ol>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  ChatDotRound,
  Message,
  Lock,
  User,
  UserFilled
} from '@element-plus/icons-vue'
import { AuthService, type LoginRequest, type RegisterRequest } from '../services/auth'

// 定义事件
const emit = defineEmits<{
  login: [user: { id: string; username: string; email: string }]
  register: [user: { id: string; username: string; email: string }]
  guestMode: []
}>()

// 响应式数据
const activeTab = ref('login')
const isLoading = ref(false)
const showForgotPassword = ref(false)
const showTerms = ref(false)
const showPrivacy = ref(false)

// 表单引用
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const forgotPasswordFormRef = ref<FormInstance>()

// 登录表单
const loginForm = reactive({
  email: '',
  password: '',
  remember: false
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

// 忘记密码表单
const forgotPasswordForm = reactive({
  email: ''
})

// 计算属性
const isLogin = computed(() => activeTab.value === 'login')

// 表单验证规则
const loginRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  agreement: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请阅读并同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const forgotPasswordRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

/**
 * 处理标签切换
 */
const handleTabChange = (tabName: string) => {
  // 清空表单数据
  if (tabName === 'login') {
    Object.assign(loginForm, {
      email: '',
      password: '',
      remember: false
    })
  } else {
    Object.assign(registerForm, {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreement: false
    })
  }
}

/**
 * 处理登录
 */
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    isLoading.value = true
    
    // 调用认证服务登录
    const loginRequest: LoginRequest = {
      email: loginForm.email,
      password: loginForm.password
    }
    
    const authResponse = await AuthService.login(loginRequest)
    
    ElMessage.success('登录成功')
    emit('login', authResponse.user)
    
  } catch (error: unknown) {
    console.error('登录失败:', error)
    const errorMessage = error instanceof Error ? error.message : '登录失败，请检查邮箱和密码'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

/**
 * 处理注册
 */
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return
    
    isLoading.value = true
    
    // 调用认证服务注册
    const registerRequest: RegisterRequest = {
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    }
    
    const authResponse = await AuthService.register(registerRequest)
    
    ElMessage.success('注册成功')
    emit('register', authResponse.user)
    
  } catch (error: unknown) {
    console.error('注册失败:', error)
    const errorMessage = error instanceof Error ? error.message : '注册失败，请重试'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

/**
 * 处理忘记密码
 */
const handleForgotPassword = async () => {
  if (!forgotPasswordFormRef.value) return
  
  try {
    const valid = await forgotPasswordFormRef.value.validate()
    if (!valid) return
    
    isLoading.value = true
    
    // 调用认证服务发送重置邮件
    await AuthService.sendPasswordResetEmail(forgotPasswordForm.email)
    
    ElMessage.success('重置邮件已发送，请查收')
    showForgotPassword.value = false
    forgotPasswordForm.email = ''
    
  } catch (error: unknown) {
    console.error('发送重置邮件失败:', error)
    const errorMessage = error instanceof Error ? error.message : '发送失败，请重试'
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

/**
 * 处理访客模式
 */
const handleGuestMode = () => {
  ElMessage.info('已进入访客模式')
  emit('guestMode')
}
</script>

<style scoped>
.auth-form {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.auth-tabs :deep(.el-tabs__header) {
  margin: 0;
}

.auth-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.auth-tabs :deep(.el-tabs__item) {
  font-weight: 500;
}

.auth-tabs :deep(.el-tabs__item.is-active) {
  color: #1677FF;
}

.auth-tabs :deep(.el-tabs__active-bar) {
  background-color: #1677FF;
}

.dialog-footer {
  text-align: right;
}

.dialog-footer .el-button {
  margin-left: 10px;
}
</style>