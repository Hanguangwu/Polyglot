<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">AI 对话</h1>
      <div class="flex space-x-2">
        <el-button type="primary" @click="showNewSessionDialog = true">新建对话</el-button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <!-- 对话列表 -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <h2 class="text-lg font-semibold mb-4">我的对话</h2>
        
        <div v-if="loading" class="text-center py-4">
          <el-loading />
        </div>
        
        <div v-else-if="chatSessions.length === 0" class="text-center py-4">
          <p class="text-gray-500">暂无对话，请创建新对话</p>
        </div>
        
        <div v-else class="space-y-2">
          <div 
            v-for="session in chatSessions" 
            :key="session.id"
            class="p-3 rounded-md cursor-pointer"
            :class="currentSession?.id === session.id ? 'bg-blue-100' : 'hover:bg-gray-100'"
            @click="selectSession(session)"
          >
            <div class="flex justify-between items-center">
              <div>
                <h3 class="font-medium">{{ session.title }}</h3>
                <p class="text-sm text-gray-500">{{ formatDate(session.created_at) }}</p>
                <div class="mt-1">
                  <el-tag size="small" :type="session.type === 'casual' ? 'info' : 'warning'">
                    {{ session.type === 'casual' ? '闲聊' : '雅思口语' }}
                  </el-tag>
                </div>
              </div>
              <el-button 
                type="text" 
                @click.stop="confirmDeleteSession(session)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 对话区域 -->
      <div class="md:col-span-3">
        <div v-if="!currentSession" class="bg-white rounded-lg shadow-md p-8 text-center">
          <div class="mb-6">
            <el-icon class="text-5xl text-blue-500"><ChatDotRound /></el-icon>
          </div>
          <h2 class="text-xl font-semibold mb-2">开始你的AI对话</h2>
          <p class="text-gray-600 mb-6">创建一个新的对话，或者从左侧选择已有的对话</p>
          <el-button type="primary" @click="showNewSessionDialog = true">新建对话</el-button>
        </div>
        
        <div v-else class="bg-white rounded-lg shadow-md p-4">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h2 class="text-xl font-semibold">{{ currentSession.title }}</h2>
              <el-tag size="small" :type="currentSession.type === 'casual' ? 'info' : 'warning'" class="mt-1">
                {{ currentSession.type === 'casual' ? '闲聊' : '雅思口语' }}
              </el-tag>
            </div>
          </div>
          
          <!-- 消息列表 -->
          <div class="h-[500px] overflow-y-auto mb-4 p-2" ref="messagesContainer">
            <div v-if="currentSession.messages.length === 0" class="text-center py-4">
              <p class="text-gray-500">
                {{ currentSession.type === 'casual' ? '发送一条消息开始闲聊' : '发送一条消息开始雅思口语练习' }}
              </p>
            </div>
            
            <div v-else class="space-y-4">
              <div 
                v-for="(message, index) in currentSession.messages" 
                :key="index"
                :class="[
                  'p-4 rounded-lg max-w-[80%]', 
                  message.role === 'user' 
                    ? 'ml-auto bg-blue-100' 
                    : 'bg-gray-100'
                ]"
              >
                <!-- 用户消息 -->
                <div v-if="message.role === 'user'">
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                  
                  <div v-if="message.score" class="mt-2">
                    <el-tag size="small" :type="getScoreTagType(message.score)">
                      得分: {{ message.score }}
                    </el-tag>
                  </div>
                  
                  <div v-if="message.feedback" class="mt-2 text-sm text-gray-600">
                    {{ message.feedback }}
                  </div>
                </div>
                
                <!-- AI消息 -->
                <div v-else>
                  <!-- 普通内容 -->
                  <div class="whitespace-pre-wrap" v-html="markdownToHtml(message.content)"></div>
                  
                  <!-- 修正内容 -->
                  <div v-if="message.corrected_content" class="mt-4 p-3 bg-white rounded border">
                    <div class="text-sm font-semibold mb-2">修正:</div>
                    <div v-html="message.corrected_content"></div>
                  </div>
                  
                  <!-- 音频播放 -->
                  <div v-if="message.audio_url" class="mt-3">
                    <audio controls :src="message.audio_url" class="w-full"></audio>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入区域 -->
          <div class="border-t pt-4">
            <div class="flex items-center space-x-2 mb-2">
              <el-button 
                v-if="currentSession.type === 'ielts' || isRecording" 
                :type="isRecording ? 'danger' : 'primary'"
                @click="toggleRecording"
                :icon="isRecording ? 'el-icon-microphone' : 'el-icon-microphone'"
              >
                {{ isRecording ? '停止录音' : '开始录音' }}
              </el-button>
              
              <div v-if="isRecording" class="text-red-500 animate-pulse">
                正在录音... {{ recordingTime }}s
              </div>
              
              <div v-if="processingAudio" class="text-blue-500">
                处理音频中...
              </div>
            </div>
            
            <div class="flex space-x-2">
              <el-input
                v-model="userInput"
                placeholder="输入消息..."
                type="textarea"
                :rows="3"
                :disabled="isRecording || processingAudio"
                @keydown.enter.ctrl.prevent="sendMessage"
              />
              
              <div class="flex flex-col justify-end">
                <el-button 
                  type="primary" 
                  @click="sendMessage" 
                  :loading="sending"
                  :disabled="isRecording || processingAudio"
                >
                  发送
                </el-button>
              </div>
            </div>
            
            <div class="text-xs text-gray-500 mt-1">
              按 Ctrl + Enter 发送
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 新建对话对话框 -->
    <el-dialog
      v-model="showNewSessionDialog"
      title="新建对话"
      width="500px"
    >
      <el-form 
        ref="sessionFormRef"
        :model="newSession"
        :rules="sessionRules"
        label-position="top"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="newSession.title" placeholder="例如：英语口语练习" />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="newSession.type">
            <el-radio label="casual">闲聊</el-radio>
            <el-radio label="ielts">雅思口语</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showNewSessionDialog = false">取消</el-button>
          <el-button type="primary" @click="createSession" :loading="creating">创建</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 删除对话确认框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="删除对话"
      width="400px"
    >
      <p>确定要删除对话 "{{ sessionToDelete?.title }}" 吗？此操作不可恢复。</p>
      
      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="deleteSession" :loading="deleting">删除</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, ChatDotRound } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  getChatSessions, 
  getChatSessionById, 
  createChatSession as createChatSessionApi, 
  updateChatSession as updateChatSessionApi, 
  deleteChatSession as deleteChatSessionApi,
  addMessage as addMessageApi,
  getAIResponse as getAIResponseApi,
  uploadAudio as uploadAudioApi
} from '@/services/chat'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ChatSession } from '@/types/chat'

// 状态
const loading = ref(false)
const chatSessions = ref<ChatSession[]>([])
const currentSession = ref<ChatSession | null>(null)
const showNewSessionDialog = ref(false)
const showDeleteDialog = ref(false)
const sessionToDelete = ref<ChatSession | null>(null)
const creating = ref(false)
const deleting = ref(false)
const sending = ref(false)
const userInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// 录音相关
const isRecording = ref(false)
const processingAudio = ref(false)
const recordingTime = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
const recordingInterval = ref<number | null>(null)

// 表单相关
const sessionFormRef = ref<FormInstance>()
const newSession = reactive({
  title: '',
  type: 'casual' as 'casual' | 'ielts'
})
const sessionRules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度应在2到50个字符之间', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ]
})

// 生命周期钩子
onMounted(async () => {
  await fetchChatSessions()
})

onUnmounted(() => {
  stopRecording()
})

// 方法
const fetchChatSessions = async () => {
  loading.value = true
  try {
    chatSessions.value = await getChatSessions()
  } catch (error) {
    console.error('Failed to fetch chat sessions:', error)
    ElMessage.error('获取对话列表失败')
  } finally {
    loading.value = false
  }
}

const selectSession = async (session: ChatSession) => {
  try {
    const fullSession = await getChatSessionById(session.id)
    currentSession.value = fullSession
    
    // 滚动到最新消息
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to fetch session details:', error)
    ElMessage.error('获取对话详情失败')
  }
}

const createSession = async () => {
  await sessionFormRef.value?.validate(async (valid) => {
    if (!valid) return
    
    creating.value = true
    try {
      const created = await createChatSessionApi({
        title: newSession.title,
        type: newSession.type
      })
      
      chatSessions.value.unshift(created)
      currentSession.value = created
      showNewSessionDialog.value = false
      
      // 重置表单
      newSession.title = ''
      newSession.type = 'casual'
      
      // 发送初始消息以触发AI响应
      await sendInitialMessage()
      
      ElMessage.success('创建对话成功')
    } catch (error) {
      console.error('Failed to create chat session:', error)
      ElMessage.error('创建对话失败')
    } finally {
      creating.value = false
    }
  })
}

const sendInitialMessage = async () => {
  if (!currentSession.value) return
  
  sending.value = true
  try {
    // 添加用户初始消息
    await addMessageApi(currentSession.value.id, {
      role: 'user',
      content: '你好，我们开始对话吧'
    })
    
    // 获取完整会话
    currentSession.value = await getChatSessionById(currentSession.value.id)
    
    // 获取AI响应
    await getAIResponse()
    
  } catch (error) {
    console.error('Failed to send initial message:', error)
    ElMessage.error('发送初始消息失败')
  } finally {
    sending.value = false
  }
}

const confirmDeleteSession = (session: ChatSession) => {
  sessionToDelete.value = session
  showDeleteDialog.value = true
}

const deleteSession = async () => {
  if (!sessionToDelete.value) return
  
  deleting.value = true
  try {
    await deleteChatSessionApi(sessionToDelete.value.id)
    
    // 从列表中移除
    chatSessions.value = chatSessions.value.filter(s => s.id !== sessionToDelete.value!.id)
    
    // 如果删除的是当前选中的，清空当前选中
    if (currentSession.value?.id === sessionToDelete.value.id) {
      currentSession.value = null
    }
    
    showDeleteDialog.value = false
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('Failed to delete session:', error)
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
    sessionToDelete.value = null
  }
}

const sendMessage = async () => {
  if (!currentSession.value || !userInput.value.trim()) return
  
  sending.value = true
  try {
    // 添加用户消息
    await addMessageApi(currentSession.value.id, {
      role: 'user',
      content: userInput.value
    })
    
    // 清空输入
    userInput.value = ''
    
    // 获取完整会话
    currentSession.value = await getChatSessionById(currentSession.value.id)
    
    // 滚动到最新消息
    await nextTick()
    scrollToBottom()
    
    // 获取AI响应
    await getAIResponse()
    
  } catch (error) {
    console.error('Failed to send message:', error)
    ElMessage.error('发送消息失败')
  } finally {
    sending.value = false
  }
}

const getAIResponse = async () => {
  if (!currentSession.value) return
  
  sending.value = true
  try {
    // 获取AI响应
    const response = await getAIResponseApi(currentSession.value.id)
    
    // 获取完整会话
    currentSession.value = await getChatSessionById(currentSession.value.id)
    
    // 滚动到最新消息
    await nextTick()
    scrollToBottom()
    
  } catch (error) {
    console.error('Failed to get AI response:', error)
    ElMessage.error('获取AI回复失败')
  } finally {
    sending.value = false
  }
}

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }
    
    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      await processAudioRecording(audioBlob)
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    
    // 开始计时
    recordingInterval.value = window.setInterval(() => {
      recordingTime.value++
      
      // 自动停止录音（2分钟）
      if (recordingTime.value >= 120) {
        stopRecording()
      }
    }, 1000)
    
  } catch (error) {
    console.error('Failed to start recording:', error)
    ElMessage.error('无法访问麦克风')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    
    // 停止所有音轨
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
  }
  
  // 清除计时器
  if (recordingInterval.value) {
    clearInterval(recordingInterval.value)
    recordingInterval.value = null
  }
  
  isRecording.value = false
}

const processAudioRecording = async (audioBlob: Blob) => {
  if (!currentSession.value) return
  
  processingAudio.value = true
  try {
    // 上传音频
    const response = await uploadAudioApi(currentSession.value.id, audioBlob)
    
    // 获取完整会话
    currentSession.value = await getChatSessionById(currentSession.value.id)
    
    // 滚动到最新消息
    await nextTick()
    scrollToBottom()
    
    // 获取AI响应
    await getAIResponse()
    
  } catch (error) {
    console.error('Failed to process audio:', error)
    ElMessage.error('处理音频失败')
  } finally {
    processingAudio.value = false
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 工具方法
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getScoreTagType = (score: number) => {
  if (score >= 7) return 'success'
  if (score >= 6) return 'warning'
  if (score >= 5) return ''
  return 'danger'
}

const markdownToHtml = (markdown: string) => {
  if (!markdown) return ''
  const html = marked(markdown)
  return DOMPurify.sanitize(html)
}
</script>

<style>
/* 确保删除线和插入线样式正确显示 */
del {
  color: #F56C6C;
  background-color: #FEF0F0;
  text-decoration: line-through;
}

ins {
  color: #67C23A;
  background-color: #F0F9EB;
  text-decoration: none;
}

/* 确保音频播放器样式合适 */
audio {
  height: 40px;
}

/* 确保markdown内容样式正确 */
.whitespace-pre-wrap p {
  margin-bottom: 0.5rem;
}

.whitespace-pre-wrap ul, .whitespace-pre-wrap ol {
  padding-left: 1.5rem;
  margin-bottom: 0.5rem;
}

.whitespace-pre-wrap h1, .whitespace-pre-wrap h2, .whitespace-pre-wrap h3 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
</style>