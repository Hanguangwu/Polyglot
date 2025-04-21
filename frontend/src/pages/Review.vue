<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">单词复习</h1>
    
    <div v-if="loading" class="flex justify-center items-center h-64">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="!currentWord && reviewWords.length === 0" class="text-center py-12">
      <el-empty description="暂无需要复习的单词">
        <el-button type="primary" @click="$router.push('/words')">去添加单词</el-button>
      </el-empty>
    </div>
    
    <div v-else-if="currentWord" class="max-w-2xl mx-auto">
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <div class="text-sm text-gray-500">
            进度: {{ reviewedCount }}/{{ totalCount }}
          </div>
          <el-tag>{{ currentWord.category || '未分类' }}</el-tag>
        </div>
        
        <div class="mb-6">
          <!-- 修改这里，使用 name 而不是 word，使用 trans 而不是 translation -->
          <h2 class="text-3xl font-bold text-center mb-2">{{ showTranslation ? (currentWord.trans && currentWord.trans.join('; ')) : currentWord.name }}</h2>
          <p v-if="showTranslation" class="text-xl text-center text-gray-700">{{ currentWord.name }}</p>
          <!-- 使用 usphone 或 ukphone 作为音标 -->
          <p v-if="showTranslation && (currentWord.usphone || currentWord.ukphone)" class="text-center text-gray-500">
            {{ currentWord.usphone ? `美 [${currentWord.usphone}]` : '' }}
            {{ currentWord.ukphone ? `英 [${currentWord.ukphone}]` : '' }}
          </p>
        </div>
        
        <div class="flex justify-center mb-6">
          <el-button type="primary" @click="toggleTranslation">
            {{ showTranslation ? '隐藏翻译' : '显示翻译' }}
          </el-button>
        </div>
        
        <div v-if="showTranslation" class="mb-6">
          <div v-if="currentWord.definition" class="bg-gray-50 p-4 rounded-md mb-4">
            <p class="text-gray-700">{{ currentWord.definition }}</p>
          </div>
          
          <div v-if="currentWord.example" class="bg-gray-50 p-4 rounded-md">
            <p class="text-gray-700 italic">{{ currentWord.example }}</p>
          </div>
        </div>
        
        <div v-if="showTranslation" class="flex justify-center space-x-4">
          <el-button type="danger" @click="markWord('difficult')">
            困难
          </el-button>
          <el-button type="warning" @click="markWord('medium')">
            一般
          </el-button>
          <el-button type="success" @click="markWord('easy')">
            简单
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReviewWords, updateWordReviewStatus } from '@/services/words'

// 状态
const loading = ref(true)
const reviewWords = ref<any[]>([])
const currentWordIndex = ref(0)
const showTranslation = ref(false)
const reviewedCount = ref(0)
const totalCount = ref(0)

// 计算属性
const currentWord = computed(() => {
  if (reviewWords.value.length === 0) return null
  return reviewWords.value[currentWordIndex.value]
})

// 生命周期钩子
onMounted(async () => {
  await fetchReviewWords()
})

// 方法
const fetchReviewWords = async () => {
  loading.value = true
  try {
    const response = await getReviewWords()
    console.log('获取到的复习单词:', response) // 添加调试日志
    reviewWords.value = response
    totalCount.value = response.length
    loading.value = false
  } catch (error) {
    console.error('Failed to fetch review words:', error)
    ElMessage.error('获取复习单词失败')
    loading.value = false
  }
}

const toggleTranslation = () => {
  showTranslation.value = !showTranslation.value
}

const markWord = async (difficulty: 'easy' | 'medium' | 'difficult') => {
  if (!currentWord.value) return
  
  try {
    // 更新单词复习状态
    await updateWordReviewStatus(currentWord.value.id, difficulty)
    
    // 更新计数
    reviewedCount.value++
    
    // 移动到下一个单词
    if (currentWordIndex.value < reviewWords.value.length - 1) {
      currentWordIndex.value++
      showTranslation.value = false
    } else {
      // 所有单词都已复习完
      ElMessage.success('恭喜你完成了所有单词的复习！')
      reviewWords.value = []
    }
  } catch (error) {
    console.error('Failed to update word review status:', error)
    ElMessage.error('更新单词状态失败')
  }
}
</script>