import axios from 'axios'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加JWT token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

// 用户信息接口
export interface User {
  id: string
  username: string
  email: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

// 登录请求接口
export interface LoginRequest {
  email: string
  password: string
}

// 注册请求接口
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

// 认证响应接口
export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// 认证服务类
export class AuthService {
  /**
   * 用户登录
   * @param credentials 登录凭据
   * @returns 认证响应
   */
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await api.post('/api/auth/login', credentials)
      const authData = response.data

      // 保存token和用户信息到本地存储
      localStorage.setItem('auth_token', authData.access_token)
      localStorage.setItem('user_info', JSON.stringify(authData.user))

      return authData
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '登录失败')
    }
  }

  /**
   * 用户注册
   * @param userData 注册数据
   * @returns 认证响应
   */
  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await api.post('/api/auth/register', userData)
      const authData = response.data

      // 保存token和用户信息到本地存储
      localStorage.setItem('auth_token', authData.access_token)
      localStorage.setItem('user_info', JSON.stringify(authData.user))

      return authData
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '注册失败')
    }
  }

  /**
   * 用户退出登录
   */
  static async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout')
    } catch (error) {
      // 即使后端退出失败，也要清除本地存储
      console.warn('后端退出登录失败:', error)
    } finally {
      // 清除本地存储
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
    }
  }

  /**
   * 获取当前用户信息
   * @returns 用户信息
   */
  static async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get('/api/auth/me')
      const user = response.data

      // 更新本地存储的用户信息
      localStorage.setItem('user_info', JSON.stringify(user))

      return user
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取用户信息失败')
    }
  }

  /**
   * 刷新访问令牌
   * @returns 新的认证响应
   */
  static async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await api.post('/api/auth/refresh')
      const authData = response.data

      // 更新本地存储的token
      localStorage.setItem('auth_token', authData.access_token)
      localStorage.setItem('user_info', JSON.stringify(authData.user))

      return authData
    } catch (error: any) {
      // 刷新失败，清除本地存储
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
      throw new Error(error.response?.data?.detail || '刷新令牌失败')
    }
  }

  /**
   * 检查用户是否已登录
   * @returns 是否已登录
   */
  static isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token')
    return !!token
  }

  /**
   * 获取本地存储的用户信息
   * @returns 用户信息或null
   */
  static getLocalUser(): User | null {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      try {
        return JSON.parse(userInfo)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('user_info')
      }
    }
    return null
  }

  /**
   * 获取本地存储的访问令牌
   * @returns 访问令牌或null
   */
  static getToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  /**
   * 发送密码重置邮件
   * @param email 邮箱地址
   */
  static async sendPasswordResetEmail(email: string): Promise<void> {
    try {
      await api.post('/api/auth/password-reset', { email })
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '发送重置邮件失败')
    }
  }

  /**
   * 重置密码
   * @param token 重置令牌
   * @param newPassword 新密码
   */
  static async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      await api.post('/api/auth/password-reset/confirm', {
        token,
        new_password: newPassword,
      })
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '重置密码失败')
    }
  }
}

// 导出axios实例供其他服务使用
export { api }
