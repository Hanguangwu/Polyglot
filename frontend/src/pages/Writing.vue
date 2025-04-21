<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">雅思写作练习</h1>
      <div class="flex space-x-2">
        <el-button type="primary" @click="showNewWritingDialog = true">新建写作</el-button>
        <el-button v-if="currentWriting" type="success" @click="saveWriting">保存写作</el-button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <!-- 写作列表 -->
      <div class="bg-white rounded-lg shadow-md p-4">
        <h2 class="text-lg font-semibold mb-4">我的写作</h2>

        <div v-if="loading" class="text-center py-4">
          <el-loading />
        </div>

        <div v-else-if="writings.length === 0" class="text-center py-4">
          <p class="text-gray-500">暂无写作，请创建新写作</p>
        </div>

        <div v-else class="space-y-2">
          <div v-for="writing in writings" :key="writing.id" class="p-3 rounded-md cursor-pointer"
            :class="currentWriting?.id === writing.id ? 'bg-blue-100' : 'hover:bg-gray-100'"
            @click="selectWriting(writing)">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="font-medium">{{ writing.title }}</h3>
                <p class="text-sm text-gray-500">{{ formatDate(writing.created_at) }}</p>
                <div v-if="writing.score" class="mt-1">
                  <el-tag size="small" :type="getScoreTagType(writing.score)">
                    得分: {{ writing.score }}
                  </el-tag>
                </div>
              </div>
              <el-button type="text" @click.stop="confirmDeleteWriting(writing)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 写作区域 -->
      <div class="md:col-span-3">
        <div v-if="!currentWriting && !checkMode" class="bg-white rounded-lg shadow-md p-8 text-center">
          <div class="mb-6">
            <el-icon class="text-5xl text-blue-500">
              <Edit />
            </el-icon>
          </div>
          <h2 class="text-xl font-semibold mb-2">开始你的雅思写作练习</h2>
          <p class="text-gray-600 mb-6">创建一个新的写作任务，或者从左侧选择已有的写作</p>
          <el-button type="primary" @click="showNewWritingDialog = true">新建写作</el-button>
        </div>

        <div v-else-if="checkMode" class="bg-white rounded-lg shadow-md p-4">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">写作评分结果</h2>
            <div>
              <el-button @click="checkMode = false">返回编辑</el-button>
              <el-button type="primary" @click="saveWithFeedback">保存结果</el-button>
            </div>
          </div>

          <el-tabs>
            <el-tab-pane label="评分与反馈">
              <div v-if="checkResult.score" class="mb-4">
                <h3 class="text-lg font-semibold mb-2">总体得分: {{ checkResult.score }}</h3>
                <el-progress :percentage="(checkResult.score / 9) * 100" :color="getScoreColor(checkResult.score)"
                  :format="format => `${checkResult.score}/9`" :stroke-width="20" />
              </div>

              <div class="prose max-w-none" v-html="markdownToHtml(checkResult.feedback)"></div>
            </el-tab-pane>

            <el-tab-pane label="语法修正">
              <div class="prose max-w-none" v-html="checkResult.corrected_content"></div>
            </el-tab-pane>

            <el-tab-pane label="范文">
              <div class="prose max-w-none" v-html="markdownToHtml(checkResult.model_essay)"></div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div v-else class="bg-white rounded-lg shadow-md p-4">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h2 class="text-xl font-semibold">{{ currentWriting.title }}</h2>
              <p v-if="currentWriting.topic" class="text-gray-600 mt-1">{{ currentWriting.topic }}</p>
            </div>

            <div class="flex items-center space-x-2">
              <div v-if="timerActive" class="text-lg font-mono">
                {{ formatTime(remainingTime) }}
              </div>
              <el-button v-if="!timerActive" @click="startTimer" type="primary" plain>
                开始计时 (40分钟)
              </el-button>
              <el-button v-else @click="stopTimer" type="danger" plain>
                停止计时
              </el-button>
            </div>
          </div>

          <div class="mb-4">
            <el-input v-model="currentWriting.topic" placeholder="输入雅思写作题目 (Task 2)" type="textarea" :rows="2" />
          </div>

          <div>
            <el-input v-model="currentWriting.content" placeholder="在这里输入你的作文..." type="textarea" :rows="15" />
          </div>

          <div class="flex justify-between mt-4">
            <div>
              <span class="text-gray-500">字数: {{ wordCount }}</span>
            </div>
            <div>
              <el-button @click="checkWriting" type="primary" :loading="checking">
                检查写作
              </el-button>
            </div>
          </div>

          <!-- 新增：展示反馈信息 -->
          <div v-if="currentWriting.feedback" class="mt-6">
            <h3 class="text-lg font-semibold mb-2">反馈信息</h3>
            <div class="prose max-w-none" v-html="markdownToHtml(currentWriting.feedback)"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建写作对话框 -->
    <el-dialog v-model="showNewWritingDialog" title="新建写作" width="500px">
      <el-form ref="writingFormRef" :model="newWriting" :rules="writingRules" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newWriting.title" placeholder="例如：雅思Task 2 - 环境话题" />
        </el-form-item>

        <el-form-item label="题目 (可选)" prop="topic">
          <el-input v-model="newWriting.topic" type="textarea" :rows="2" placeholder="输入雅思写作题目 (Task 2)" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showNewWritingDialog = false">取消</el-button>
          <el-button type="primary" @click="createWriting" :loading="creating">创建</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除写作确认框 -->
    <el-dialog v-model="showDeleteDialog" title="删除写作" width="400px">
      <p>确定要删除写作 "{{ writingToDelete?.title }}" 吗？此操作不可恢复。</p>

      <template #footer>
        <div class="flex justify-end space-x-2">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="deleteWriting" :loading="deleting">删除</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Edit } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getWritings,
  getWritingById,
  createWriting as createWritingApi,
  updateWriting as updateWritingApi,
  deleteWriting as deleteWritingApi,
  checkWriting as checkWritingApi
} from '@/services/writing'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { Writing } from '@/types/writing'
import { ElLoading } from 'element-plus'

// 状态
const loading = ref(false)
const writings = ref<Writing[]>([])
const currentWriting = ref<Writing | null>(null)
const showNewWritingDialog = ref(false)
const showDeleteDialog = ref(false)
const writingToDelete = ref<Writing | null>(null)
const creating = ref(false)
const deleting = ref(false)
const checking = ref(false)
const checkMode = ref(false)
const checkResult = ref({
  feedback: '',
  score: null,
  corrected_content: '',
  model_essay: ''
})

// 计时器相关
const timerActive = ref(false)
const remainingTime = ref(40 * 60) // 40分钟，以秒为单位
const timerInterval = ref<number | null>(null)

// 表单相关
const writingFormRef = ref<FormInstance>()
const newWriting = reactive({
  title: '',
  topic: '',
  content: ''
})
const writingRules = reactive<FormRules>({
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度应在2到50个字符之间', trigger: 'blur' }
  ]
})

// 计算属性
const wordCount = computed(() => {
  if (!currentWriting.value?.content) return 0
  return currentWriting.value.content.trim().split(/\s+/).length
})

// 生命周期钩子
// 在 onMounted 钩子中添加登录检查
onMounted(async () => {
  // 检查用户是否已登录
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    // 可以添加路由导航到登录页面
    // router.push('/login')
    return
  }

  await fetchWritings()
})

// 修改 fetchWritings 方法，添加错误处理
const fetchWritings = async () => {
  loading.value = true
  try {
    writings.value = await getWritings()
  } catch (error) {
    console.error('Failed to fetch writings:', error)
    // 如果是401错误，提示用户登录
    if (error.response && error.response.status === 401) {
      ElMessage.warning('登录已过期，请重新登录')
      // 可以添加路由导航到登录页面
      // router.push('/login')
    } else {
      ElMessage.error('获取写作列表失败')
    }
  } finally {
    loading.value = false
  }
}

const selectWriting = async (writing: Writing) => {
  try {
    const fullWriting = await getWritingById(writing.id)
    currentWriting.value = fullWriting
    checkMode.value = false
    stopTimer()
  } catch (error) {
    console.error('Failed to fetch writing details:', error)
    ElMessage.error('获取写作详情失败')
  }
}

const createWriting = async () => {
  await writingFormRef.value?.validate(async (valid) => {
    if (!valid) return

    creating.value = true
    try {
      const created = await createWritingApi({
        title: newWriting.title,
        topic: newWriting.topic,
        content: ''
      })

      writings.value.unshift(created)
      currentWriting.value = created
      showNewWritingDialog.value = false

      // 重置表单
      newWriting.title = ''
      newWriting.topic = ''

      ElMessage.success('创建写作成功')
    } catch (error) {
      console.error('Failed to create writing:', error)
      ElMessage.error('创建写作失败')
    } finally {
      creating.value = false
    }
  })
}

const saveWriting = async () => {
  if (!currentWriting.value) return

  try {
    await updateWritingApi(currentWriting.value.id, {
      title: currentWriting.value.title,
      content: currentWriting.value.content,
      topic: currentWriting.value.topic,
      time_spent: timerActive.value ? (40 * 60 - remainingTime.value) : undefined
    })

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Failed to save writing:', error)
    ElMessage.error('保存失败')
  }
}

const saveWithFeedback = async () => {
  if (!currentWriting.value || !checkResult.value) return;

  try {
    console.log("保存反馈:", checkResult.value);  // 添加调试日志
    
    const updateData = {
      // 保留原有字段
      title: currentWriting.value.title,
      content: currentWriting.value.content,
      topic: currentWriting.value.topic,
      
      // 添加AI反馈相关字段
      feedback: checkResult.value.feedback,
      corrected_content: checkResult.value.corrected_content,
      model_essay: checkResult.value.model_essay,
      score: checkResult.value.score,
      
      // 记录写作时间
      time_spent: timerActive.value ? (40 * 60 - remainingTime.value) : undefined
    };
    
    await updateWritingApi(currentWriting.value.id, updateData);

    // 更新本地数据
    currentWriting.value = {
      ...currentWriting.value,
      ...updateData
    };

    // 更新列表中的数据
    const index = writings.value.findIndex(w => w.id === currentWriting.value!.id);
    if (index !== -1) {
      writings.value[index] = {
        ...writings.value[index],
        score: checkResult.value.score,
        feedback: checkResult.value.feedback ? '已评分' : undefined
      };
    }

    ElMessage.success('保存成功');
    checkMode.value = false;
  } catch (error) {
    console.error('Failed to save feedback:', error);
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message));
  }
}

const confirmDeleteWriting = (writing: Writing) => {
  writingToDelete.value = writing
  showDeleteDialog.value = true
}

const deleteWriting = async () => {
  if (!writingToDelete.value) return

  deleting.value = true
  try {
    await deleteWritingApi(writingToDelete.value.id)

    // 从列表中移除
    writings.value = writings.value.filter(w => w.id !== writingToDelete.value!.id)

    // 如果删除的是当前选中的，清空当前选中
    if (currentWriting.value?.id === writingToDelete.value.id) {
      currentWriting.value = null
    }

    showDeleteDialog.value = false
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('Failed to delete writing:', error)
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
    writingToDelete.value = null
  }
}

const checkWriting = async () => {
  if (!currentWriting.value?.content || !currentWriting.value?.topic) {
    ElMessage.warning('请先输入题目和内容')
    return
  }

  checking.value = true
  try {
    // 保存当前内容，确保不会丢失
    await saveWriting()
    
    const result = await checkWritingApi({
      content: currentWriting.value.content,
      topic: currentWriting.value.topic
    })

    console.log("收到评分结果:", result)  // 添加调试日志
    
    // 确保所有字段都有值
    checkResult.value = {
      feedback: result.feedback || '',
      score: result.score || 0,
      corrected_content: result.corrected_content || currentWriting.value.content,
      model_essay: result.model_essay || ''
    }
    
    // 切换到评分模式
    checkMode.value = true

    // 停止计时器
    if (timerActive.value) {
      stopTimer()
    }
  } catch (error) {
    console.error('Failed to check writing:', error)
    ElMessage.error('检查写作失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    checking.value = false
  }
}

// 计时器相关方法
const startTimer = () => {
  if (timerActive.value) return

  remainingTime.value = 40 * 60 // 重置为40分钟
  timerActive.value = true

  timerInterval.value = window.setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      stopTimer()
      ElMessage.warning('时间到！')
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  timerActive.value = false
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

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getScoreTagType = (score: number) => {
  if (score >= 7) return 'success'
  if (score >= 6) return 'warning'
  if (score >= 5) return ''
  return 'danger'
}

const getScoreColor = (score: number) => {
  if (score >= 7) return '#67C23A'
  if (score >= 6) return '#E6A23C'
  if (score >= 5) return '#409EFF'
  return '#F56C6C'
}

const markdownToHtml = (markdown: string) => {
  if (!markdown) return ''
  const html = marked(markdown)
  return DOMPurify.sanitize(html)
}
</script>

<style>
.el-tabs__content {
  padding: 20px 0;
}

/* 添加一些样式使redlines标记更明显 */
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

.prose {
  max-width: 65ch;
  color: #374151;
  line-height: 1.75;
}

.prose h1,
.prose h2,
.prose h3,
.prose h4 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
}

.prose p,
.prose ul,
.prose ol {
  margin-top: 1em;
  margin-bottom: 1em;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
  margin-bottom: 1em;
}

.prose th,
.prose td {
  padding: 0.5em;
  border: 1px solid #e5e7eb;
}

.prose th {
  background-color: #f9fafb;
  font-weight: 600;
}
</style>
