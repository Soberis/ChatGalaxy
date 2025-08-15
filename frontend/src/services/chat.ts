import { api } from './auth'

// WebSocket连接状态
export enum WebSocketStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
}

// 消息类型
export enum MessageType {
  USER = 'user',
  AI = 'ai',
  SYSTEM = 'system',
}

// 消息接口
export interface Message {
  id: string
  session_id: string
  content: string
  message_type: MessageType
  role_id?: string
  created_at: string
  is_streaming?: boolean
}

// 聊天会话接口
export interface ChatSession {
  id: string
  user_id?: string
  title: string
  role_id: string
  created_at: string
  updated_at: string
  message_count: number
}

// AI角色接口
export interface AIRole {
  id: string
  name: string
  description: string
  system_prompt: string
  avatar_url?: string
  is_active: boolean
  created_at: string
}

// WebSocket消息接口
export interface WebSocketMessage {
  type: 'message' | 'error' | 'status' | 'stream_start' | 'stream_chunk' | 'stream_end'
  data: any
  session_id?: string
  message_id?: string
}

// 发送消息请求接口
export interface SendMessageRequest {
  content: string
  session_id?: string
  role_id: string
}

// 聊天服务类
export class ChatService {
  private static ws: WebSocket | null = null
  private static wsStatus: WebSocketStatus = WebSocketStatus.DISCONNECTED
  private static messageHandlers: ((message: WebSocketMessage) => void)[] = []
  private static statusHandlers: ((status: WebSocketStatus) => void)[] = []
  private static reconnectAttempts = 0
  private static maxReconnectAttempts = 5
  private static reconnectDelay = 1000
  private static heartbeatInterval: number | null = null

  /**
   * 连接WebSocket
   */
  static async connectWebSocket(): Promise<void> {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    const token = localStorage.getItem('auth_token')

    try {
      this.wsStatus = WebSocketStatus.CONNECTING
      this.notifyStatusHandlers()

      // 构建WebSocket URL，包含认证token
      const url = token ? `${wsUrl}?token=${token}` : wsUrl
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket连接已建立')
        this.wsStatus = WebSocketStatus.CONNECTED
        this.reconnectAttempts = 0
        this.notifyStatusHandlers()
        this.startHeartbeat()
      }

      this.ws.onmessage = event => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.notifyMessageHandlers(message)
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onclose = event => {
        console.log('WebSocket连接已关闭:', event.code, event.reason)
        this.wsStatus = WebSocketStatus.DISCONNECTED
        this.notifyStatusHandlers()
        this.stopHeartbeat()

        // 自动重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = error => {
        console.error('WebSocket错误:', error)
        this.wsStatus = WebSocketStatus.ERROR
        this.notifyStatusHandlers()
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.wsStatus = WebSocketStatus.ERROR
      this.notifyStatusHandlers()
    }
  }

  /**
   * 断开WebSocket连接
   */
  static disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.stopHeartbeat()
    this.wsStatus = WebSocketStatus.DISCONNECTED
    this.notifyStatusHandlers()
  }

  /**
   * 发送WebSocket消息
   */
  private static sendWebSocketMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  /**
   * 开始心跳检测
   */
  private static startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.sendWebSocketMessage({ type: 'ping' })
    }, 30000) // 每30秒发送一次心跳
  }

  /**
   * 停止心跳检测
   */
  private static stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 安排重连
   */
  private static scheduleReconnect(): void {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`${delay}ms后尝试第${this.reconnectAttempts}次重连...`)

    setTimeout(() => {
      this.connectWebSocket()
    }, delay)
  }

  /**
   * 添加消息处理器
   */
  static addMessageHandler(handler: (message: WebSocketMessage) => void): void {
    this.messageHandlers.push(handler)
  }

  /**
   * 移除消息处理器
   */
  static removeMessageHandler(handler: (message: WebSocketMessage) => void): void {
    const index = this.messageHandlers.indexOf(handler)
    if (index > -1) {
      this.messageHandlers.splice(index, 1)
    }
  }

  /**
   * 添加状态处理器
   */
  static addStatusHandler(handler: (status: WebSocketStatus) => void): void {
    this.statusHandlers.push(handler)
  }

  /**
   * 移除状态处理器
   */
  static removeStatusHandler(handler: (status: WebSocketStatus) => void): void {
    const index = this.statusHandlers.indexOf(handler)
    if (index > -1) {
      this.statusHandlers.splice(index, 1)
    }
  }

  /**
   * 通知消息处理器
   */
  private static notifyMessageHandlers(message: WebSocketMessage): void {
    this.messageHandlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error('消息处理器执行失败:', error)
      }
    })
  }

  /**
   * 通知状态处理器
   */
  private static notifyStatusHandlers(): void {
    this.statusHandlers.forEach(handler => {
      try {
        handler(this.wsStatus)
      } catch (error) {
        console.error('状态处理器执行失败:', error)
      }
    })
  }

  /**
   * 获取WebSocket连接状态
   */
  static getWebSocketStatus(): WebSocketStatus {
    return this.wsStatus
  }

  /**
   * 发送聊天消息
   */
  static async sendMessage(request: SendMessageRequest): Promise<Message> {
    try {
      const response = await api.post('/api/chat/send', request)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '发送消息失败')
    }
  }

  /**
   * 获取聊天会话列表
   */
  static async getChatSessions(): Promise<ChatSession[]> {
    try {
      const response = await api.get('/api/chat/sessions')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取会话列表失败')
    }
  }

  /**
   * 获取会话消息历史
   */
  static async getSessionMessages(sessionId: string): Promise<Message[]> {
    try {
      const response = await api.get(`/api/chat/sessions/${sessionId}/messages`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取消息历史失败')
    }
  }

  /**
   * 创建新的聊天会话
   */
  static async createSession(title: string, roleId: string): Promise<ChatSession> {
    try {
      const response = await api.post('/api/chat/sessions', {
        title,
        role_id: roleId,
      })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '创建会话失败')
    }
  }

  /**
   * 删除聊天会话
   */
  static async deleteSession(sessionId: string): Promise<void> {
    try {
      await api.delete(`/api/chat/sessions/${sessionId}`)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '删除会话失败')
    }
  }

  /**
   * 更新会话标题
   */
  static async updateSessionTitle(sessionId: string, title: string): Promise<ChatSession> {
    try {
      const response = await api.put(`/api/chat/sessions/${sessionId}`, { title })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '更新会话标题失败')
    }
  }

  /**
   * 获取AI角色列表
   */
  static async getAIRoles(): Promise<AIRole[]> {
    try {
      const response = await api.get('/api/roles')
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取AI角色失败')
    }
  }

  /**
   * 获取单个AI角色信息
   */
  static async getAIRole(roleId: string): Promise<AIRole> {
    try {
      const response = await api.get(`/api/roles/${roleId}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '获取AI角色信息失败')
    }
  }
}
