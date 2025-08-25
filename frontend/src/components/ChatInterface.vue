<template>
  <div class="chat-interface h-screen flex flex-col bg-gray-50">
    <!-- 聊天头部 -->
    <div
      class="chat-header bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between flex-shrink-0"
    >
      <div class="flex items-center space-x-2 sm:space-x-3 flex-1 min-w-0">
        <el-avatar :size="32" :src="currentRole?.avatar_url" class="bg-primary-500 flex-shrink-0">
          <el-icon><User /></el-icon>
        </el-avatar>
        <div class="min-w-0 flex-1">
          <h3 class="text-base sm:text-lg font-semibold text-gray-800 truncate">{{ currentRole?.name }}</h3>
          <p class="text-xs sm:text-sm text-gray-500 truncate">{{ currentRole?.description }}</p>
        </div>
      </div>
      <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
        <el-button type="primary" size="small" @click="showRoleSelector = true" class="hidden sm:inline-flex">
          <el-icon><Switch /></el-icon>
          切换角色
        </el-button>
        <el-button type="primary" size="small" @click="showRoleSelector = true" class="sm:hidden">
          <el-icon><Switch /></el-icon>
        </el-button>
        <el-button size="small" @click="clearChat" class="hidden sm:inline-flex">
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
        <el-button size="small" @click="clearChat" class="sm:hidden">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="chat-messages flex-1 overflow-y-auto px-4 sm:px-6 py-4 min-h-0" ref="messagesContainer">
      <div
        v-if="messages.length === 0"
        class="h-full flex flex-col items-center justify-center text-center text-gray-500 px-4"
      >
        <el-icon size="48" class="mb-4 text-gray-400"><ChatDotRound /></el-icon>
        <p class="text-lg sm:text-xl font-medium mb-2">开始与 {{ currentRole?.name }} 对话吧！</p>
        <p class="text-sm text-gray-400 max-w-md">{{ currentRole?.system_prompt }}</p>
      </div>

      <div v-for="message in messages" :key="message.id" class="message-item mb-4 sm:mb-6">
        <!-- 用户消息 -->
        <div v-if="message.message_type === MessageType.USER" class="flex justify-end">
          <div class="max-w-xs sm:max-w-md md:max-w-lg lg:max-w-2xl">
            <div class="bg-primary-500 text-white rounded-lg px-3 sm:px-4 py-2 sm:py-3 shadow-sm">
              <p class="whitespace-pre-wrap text-sm sm:text-base">{{ message.content }}</p>
            </div>
            <div class="text-xs text-gray-500 mt-1 text-right">
              {{ formatTime(message.created_at) }}
            </div>
          </div>
        </div>

        <!-- AI消息 -->
        <div v-else class="flex justify-start">
          <div class="max-w-xs sm:max-w-md md:max-w-lg lg:max-w-2xl">
            <div class="bg-white border border-gray-200 rounded-lg px-3 sm:px-4 py-2 sm:py-3 shadow-sm">
              <div v-if="message.is_streaming" class="flex items-center space-x-2 text-gray-500">
                <el-icon class="animate-spin"><Loading /></el-icon>
                <span class="text-sm">AI正在思考中...</span>
              </div>
              <div v-else>
                <p class="whitespace-pre-wrap text-gray-800 text-sm sm:text-base">{{ message.content }}</p>
              </div>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatTime(message.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 流式消息显示 -->
      <div v-if="streamingMessage" class="message-item mb-4 sm:mb-6">
        <div class="flex justify-start">
          <div class="max-w-xs sm:max-w-md md:max-w-lg lg:max-w-2xl">
            <div class="bg-white border border-gray-200 rounded-lg px-3 sm:px-4 py-2 sm:py-3 shadow-sm">
              <p class="whitespace-pre-wrap text-gray-800 text-sm sm:text-base">{{ streamingMessage }}</p>
              <div class="flex items-center space-x-2 text-gray-500 mt-2">
                <el-icon class="animate-pulse"><Loading /></el-icon>
                <span class="text-xs">正在生成回复...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input bg-white border-t border-gray-200 px-4 sm:px-6 py-4 flex-shrink-0 sticky bottom-0">
      <div class="flex items-end space-x-3">
        <div class="flex-1">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 3 }"
            placeholder="输入消息...按Enter发送，Shift+Enter换行"
            @keydown.enter.exact="handleSendMessage"
            @keydown.enter.shift.exact.prevent="inputMessage += '\n'"
            :disabled="isLoading"
            class="chat-textarea"
            size="large"
          />
        </div>
        <el-button
          type="primary"
          @click="handleSendMessage"
          :loading="isLoading"
          :disabled="!inputMessage.trim()"
          size="large"
          class="flex-shrink-0 h-12"
        >
          <el-icon><Promotion /></el-icon>
          <span class="ml-1 hidden sm:inline">发送</span>
        </el-button>
      </div>
    </div>

    <!-- 角色选择器 -->
    <el-dialog v-model="showRoleSelector" title="选择AI角色" :width="dialogWidth">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="role in availableRoles"
          :key="role.id"
          @click="selectRole(role)"
          class="role-card p-3 sm:p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-primary-500 hover:shadow-md transition-all"
          :class="{ 'border-primary-500 bg-primary-50': role.id === currentRole?.id }"
        >
          <div class="flex items-center space-x-2 sm:space-x-3 mb-2 sm:mb-3">
            <el-avatar :size="32" :src="role.avatar_url" class="bg-primary-500 flex-shrink-0">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="min-w-0 flex-1">
              <h4 class="font-semibold text-gray-800 text-sm sm:text-base truncate">{{ role.name }}</h4>
              <p class="text-xs sm:text-sm text-gray-500 truncate">{{ role.description }}</p>
            </div>
          </div>
          <p class="text-xs text-gray-600 line-clamp-2">{{ role.system_prompt }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ChatDotRound, Delete, Loading, Promotion, Switch, User } from '@element-plus/icons-vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
  import {
    type AIRole,
    ChatService,
    type ChatSession,
    type Message,
    MessageType,
    type WebSocketMessage,
    WebSocketStatus,
  } from '../services/chat'

  // 组件属性定义
  interface Props {
    currentUser?: {
      id: string
      username: string
      email: string
    } | null
  }

  const props = withDefaults(defineProps<Props>(), {
    currentUser: null,
  })

  // 组件事件
  const emit = defineEmits<{
    roleChange: [role: AIRole]
  }>()

  // 响应式数据
  const messages = ref<Message[]>([])
  const inputMessage = ref('')
  const isLoading = ref(false)
  const showRoleSelector = ref(false)
  const messagesContainer = ref<HTMLElement>()
  const currentRole = ref<AIRole | null>(null)
  const availableRoles = ref<AIRole[]>([])
  const currentSession = ref<ChatSession | null>(null)
  const wsStatus = ref<WebSocketStatus>(WebSocketStatus.DISCONNECTED)
  const streamingMessage = ref<string>('')

  // 计算属性
  const dialogWidth = computed(() => {
    if (typeof window === 'undefined') return '90%'
    return window.innerWidth < 640 ? '95%' : window.innerWidth < 1024 ? '80%' : '600px'
  })

  /**
   * 发送消息处理函数
   */
  const handleSendMessage = async () => {
    if (!inputMessage.value.trim() || isLoading.value || !currentRole.value) return

    const messageContent = inputMessage.value.trim()
    inputMessage.value = ''
    isLoading.value = true

    try {
      // 如果没有当前会话，创建新会话
      if (!currentSession.value) {
        const sessionTitle = messageContent.length > 20 ? messageContent.substring(0, 20) + '...' : messageContent
        currentSession.value = await ChatService.createSession(sessionTitle, currentRole.value.id)
      }

      // 发送消息到后端
      const userMessage = await ChatService.sendMessage({
        content: messageContent,
        session_id: currentSession.value.id,
        role_id: currentRole.value.id,
      })

      // 添加用户消息到界面
      messages.value.push(userMessage)
      await nextTick()
      scrollToBottom()
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '发送消息失败，请重试'
      ElMessage.error(errorMessage)
      console.error('发送消息错误:', error)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 模拟流式响应（后续替换为真实API调用）
   */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const simulateStreamResponse = async (userMessage: string) => {
    const responses = [
      '这是一个很有趣的问题。',
      '让我来为你详细解答一下。',
      '根据我的理解，这个问题涉及到多个方面。',
      '希望我的回答对你有帮助！',
    ]

    const fullResponse = responses.join(' ')
    streamingMessage.value = ''

    // 模拟逐字显示
    for (let i = 0; i < fullResponse.length; i++) {
      streamingMessage.value += fullResponse[i]
      await new Promise(resolve => setTimeout(resolve, 50))
      scrollToBottom()
    }

    // 添加完整消息到列表
    const aiMessage: Message = {
      id: Date.now().toString(),
      session_id: currentSession.value?.id || '',
      content: streamingMessage.value,
      message_type: MessageType.AI,
      role_id: currentRole.value?.id,
      created_at: new Date().toISOString(),
    }

    messages.value.push(aiMessage)
    streamingMessage.value = ''

    await nextTick()
    scrollToBottom()
  }

  /**
   * 选择AI角色
   */
  const selectRole = async (role: AIRole) => {
    currentRole.value = role
    showRoleSelector.value = false
    emit('roleChange', role)

    // 切换角色时创建新会话
    currentSession.value = null
    messages.value = []

    ElMessage.success(`已切换到${role.name}`)
  }

  /**
   * 清空对话
   */
  const clearChat = async () => {
    try {
      await ElMessageBox.confirm('确定要清空所有对话记录吗？此操作不可恢复。', '确认清空', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })

      messages.value = []
      currentSession.value = null
      streamingMessage.value = ''
      ElMessage.success('对话已清空')
    } catch {
      // 用户取消操作
    }
  }

  /**
   * 滚动到底部
   */
  const scrollToBottom = () => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }

  /**
   * 格式化时间
   */
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // 监听消息变化，自动滚动到底部
  watch(
    () => messages.value.length,
    async () => {
      await nextTick()
      scrollToBottom()
    }
  )

  // WebSocket消息处理器
  const handleWebSocketMessage = (wsMessage: WebSocketMessage) => {
    switch (wsMessage.type) {
      case 'message':
        // 接收到完整消息
        messages.value.push(wsMessage.data as Message)
        nextTick(() => scrollToBottom())
        break

      case 'stream_start':
        // 开始流式响应
        streamingMessage.value = ''
        nextTick(() => scrollToBottom())
        break

      case 'stream_chunk':
        // 流式响应数据块
        streamingMessage.value += wsMessage.data
        nextTick(() => scrollToBottom())
        break

      case 'stream_end':
        // 流式响应结束
        if (streamingMessage.value) {
          // 将流式消息添加到消息列表
          const aiMessage: Message = {
            id: wsMessage.message_id || Date.now().toString(),
            session_id: wsMessage.session_id || currentSession.value?.id || '',
            content: streamingMessage.value,
            message_type: MessageType.AI,
            role_id: currentRole.value?.id,
            created_at: new Date().toISOString(),
          }
          messages.value.push(aiMessage)
          streamingMessage.value = ''
        }
        break

      case 'error':
        ElMessage.error(wsMessage.data || '发生未知错误')
        break
    }
  }

  // WebSocket状态处理器
  const handleWebSocketStatus = (status: WebSocketStatus) => {
    wsStatus.value = status

    switch (status) {
      case WebSocketStatus.CONNECTED:
        console.log('WebSocket连接已建立')
        break
      case WebSocketStatus.DISCONNECTED:
        console.log('WebSocket连接已断开')
        break
      case WebSocketStatus.ERROR:
        ElMessage.error('WebSocket连接出错')
        break
    }
  }

  // 初始化函数
  const initialize = async () => {
    try {
      // 加载AI角色列表
      availableRoles.value = await ChatService.getAIRoles()
      if (availableRoles.value.length > 0) {
        currentRole.value = availableRoles.value[0]
      }

      // 如果用户已登录，连接WebSocket
      if (props.currentUser) {
        await ChatService.connectWebSocket()
      }
    } catch (error: unknown) {
      console.error('初始化失败:', error)
      const errorMessage = error instanceof Error ? error.message : '初始化失败，请刷新页面重试'
      ElMessage.error(errorMessage)
    }
  }

  // 组件挂载时的初始化
  onMounted(async () => {
    // 添加WebSocket事件监听器
    ChatService.addMessageHandler(handleWebSocketMessage)
    ChatService.addStatusHandler(handleWebSocketStatus)

    // 初始化组件
    await initialize()
  })

  // 组件卸载时的清理
  onUnmounted(() => {
    // 移除WebSocket事件监听器
    ChatService.removeMessageHandler(handleWebSocketMessage)
    ChatService.removeStatusHandler(handleWebSocketStatus)

    // 断开WebSocket连接
    ChatService.disconnectWebSocket()
  })
</script>

<style scoped>
  .chat-interface {
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
  }

  .chat-messages {
    scroll-behavior: smooth;
    flex: 1;
    min-height: 0;
  }

  .chat-input {
    background: white;
    border-top: 1px solid #e5e7eb;
    backdrop-filter: blur(10px);
  }

  .message-item {
    animation: fadeIn 0.3s ease-in;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .role-card {
    transition: all 0.2s ease;
  }

  .role-card:hover {
    transform: translateY(-2px);
  }

  .chat-textarea :deep(.el-textarea__inner) {
    resize: none;
    border-radius: 8px;
    border: 1px solid #d1d5db;
    transition: border-color 0.3s ease;
  }

  .chat-textarea :deep(.el-textarea__inner):focus {
    border-color: #1677ff;
    box-shadow: 0 0 0 2px rgba(22, 119, 255, 0.1);
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  /* 移动端优化 */
  @media (max-width: 640px) {
    .chat-interface {
      height: 100vh;
      height: 100dvh; /* 动态视口高度 */
    }

    .chat-input {
      padding: 12px 16px;
    }

    .chat-messages {
      padding: 12px 16px;
    }
  }
</style>
