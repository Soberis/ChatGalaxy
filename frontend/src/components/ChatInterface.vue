<template>
  <div class="chat-interface h-full flex flex-col bg-gray-50">
    <!-- 聊天头部 -->
    <div class="chat-header bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <el-avatar :size="40" :src="currentRole?.avatar_url" class="bg-primary-500">
          <el-icon><User /></el-icon>
        </el-avatar>
        <div>
          <h3 class="text-lg font-semibold text-gray-800">{{ currentRole?.name }}</h3>
          <p class="text-sm text-gray-500">{{ currentRole?.description }}</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <el-button type="primary" @click="showRoleSelector = true">
          <el-icon><Switch /></el-icon>
          切换角色
        </el-button>
        <el-button @click="clearChat">
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="chat-messages flex-1 overflow-y-auto px-6 py-4" ref="messagesContainer">
      <div v-if="messages.length === 0" class="text-center text-gray-500 mt-20">
        <el-icon size="48" class="mb-4"><ChatDotRound /></el-icon>
        <p class="text-lg">开始与 {{ currentRole?.name }} 对话吧！</p>
        <p class="text-sm mt-2">{{ currentRole?.system_prompt }}</p>
      </div>
      
      <div v-for="message in messages" :key="message.id" class="message-item mb-6">
        <!-- 用户消息 -->
        <div v-if="message.message_type === MessageType.USER" class="flex justify-end">
          <div class="max-w-2xl">
            <div class="bg-primary-500 text-white rounded-lg px-4 py-3 shadow-sm">
              <p class="whitespace-pre-wrap">{{ message.content }}</p>
            </div>
            <div class="text-xs text-gray-500 mt-1 text-right">
              {{ formatTime(message.created_at) }}
            </div>
          </div>
        </div>
        
        <!-- AI消息 -->
        <div v-else class="flex justify-start">
          <div class="max-w-2xl">
            <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
              <div v-if="message.is_streaming" class="flex items-center space-x-2 text-gray-500">
                <el-icon class="animate-spin"><Loading /></el-icon>
                <span>AI正在思考中...</span>
              </div>
              <div v-else>
                <p class="whitespace-pre-wrap text-gray-800">{{ message.content }}</p>
              </div>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatTime(message.created_at) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 流式消息显示 -->
      <div v-if="streamingMessage" class="message-item mb-6">
        <div class="flex justify-start">
          <div class="max-w-2xl">
            <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
              <p class="whitespace-pre-wrap text-gray-800">{{ streamingMessage }}</p>
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
    <div class="chat-input bg-white border-t border-gray-200 px-6 py-4">
      <div class="flex items-end space-x-3">
        <div class="flex-1">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入消息..."
            @keydown.enter.exact="handleSendMessage"
            @keydown.enter.shift.exact.prevent="inputMessage += '\n'"
            :disabled="isLoading"
            class="chat-textarea"
          />
        </div>
        <el-button
          type="primary"
          @click="handleSendMessage"
          :loading="isLoading"
          :disabled="!inputMessage.trim()"
          size="large"
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 角色选择器 -->
    <el-dialog v-model="showRoleSelector" title="选择AI角色" width="600px">
      <div class="grid grid-cols-2 gap-4">
        <div
          v-for="role in availableRoles"
          :key="role.id"
          @click="selectRole(role)"
          class="role-card p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-primary-500 hover:shadow-md transition-all"
          :class="{ 'border-primary-500 bg-primary-50': role.id === currentRole?.id }"
        >
          <div class="flex items-center space-x-3 mb-3">
            <el-avatar :size="40" :src="role.avatar_url" class="bg-primary-500">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div>
              <h4 class="font-semibold text-gray-800">{{ role.name }}</h4>
              <p class="text-sm text-gray-500">{{ role.description }}</p>
            </div>
          </div>
          <p class="text-xs text-gray-600">{{ role.system_prompt }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Delete, Switch, ChatDotRound, Loading, Promotion } from '@element-plus/icons-vue'
import { 
  ChatService, 
  type Message, 
  type AIRole, 
  type ChatSession,
  type WebSocketMessage,
  WebSocketStatus,
  MessageType
} from '../services/chat'
import { AuthService } from '../services/auth'

// 组件属性定义
interface Props {
  currentUser?: {
    id: string
    username: string
    email: string
  } | null
}

const props = withDefaults(defineProps<Props>(), {
  currentUser: null
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
      const sessionTitle = messageContent.length > 20 
        ? messageContent.substring(0, 20) + '...' 
        : messageContent
      currentSession.value = await ChatService.createSession(sessionTitle, currentRole.value.id)
    }
    
    // 发送消息到后端
    const userMessage = await ChatService.sendMessage({
      content: messageContent,
      session_id: currentSession.value.id,
      role_id: currentRole.value.id
    })
    
    // 添加用户消息到界面
    messages.value.push(userMessage)
    await nextTick()
    scrollToBottom()
    
  } catch (error: any) {
    ElMessage.error(error.message || '发送消息失败，请重试')
    console.error('发送消息错误:', error)
  } finally {
    isLoading.value = false
  }
}

/**
 * 模拟流式响应（后续替换为真实API调用）
 */
const simulateStreamResponse = async (userMessage: string) => {
  const responses = [
    '这是一个很有趣的问题。',
    '让我来为你详细解答一下。',
    '根据我的理解，这个问题涉及到多个方面。',
    '希望我的回答对你有帮助！'
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
    created_at: new Date().toISOString()
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
    await ElMessageBox.confirm(
      '确定要清空所有对话记录吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
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
    minute: '2-digit'
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
          created_at: new Date().toISOString()
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
    
  } catch (error: any) {
    console.error('初始化失败:', error)
    ElMessage.error('初始化失败，请刷新页面重试')
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
}

.chat-messages {
  scroll-behavior: smooth;
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
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}
</style>