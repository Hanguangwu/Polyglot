<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">单词学习</h1>
      <div class="flex space-x-2">
        <el-upload action="" :auto-upload="false" :on-change="handleFileChange" :show-file-list="false">
          <el-button type="primary">导入单词</el-button>
        </el-upload>
        <el-button @click="handleExport">导出单词</el-button>
        <el-button type="success" @click="showAddWordDialog = true">添加单词</el-button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-2">
        <div class="bg-white rounded-lg shadow-md p-4 mb-6 flex justify-between items-center">
          <el-input v-model="searchQuery" placeholder="搜索单词" prefix-icon="el-icon-search" clearable class="w-1/2" />

          <div class="flex items-center space-x-4">
            <span>随机选择</span>
            <el-input-number v-model="wordLimit" :min="10" :max="100" :step="10" />
            <el-button type="primary" @click="fetchRandomWordsForStudy">开始学习</el-button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-12" v-loading="true" element-loading-text="加载中...">
          <el-empty description="加载中" />
        </div>

        <template v-else-if="studyMode">
          <div class="bg-white rounded-lg shadow-md p-6 mb-4">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold">学习模式 ({{ currentIndex + 1 }}/{{ studyWords.length }})</h2>
              <el-button type="danger" @click="exitStudyMode">退出学习</el-button>
            </div>

            <el-pagination layout="prev, pager, next" :total="studyWords.length" :page-size="1"
              :current-page="currentIndex + 1" @current-change="handlePageChange" class="mb-4" />

            <div v-if="currentWord" class="p-6 border rounded-lg">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-bold">{{ currentWord.name }}</h3>
                <div class="flex space-x-2">
                  <el-button :type="currentWord.favorite ? 'warning' : 'default'"
                    @click="toggleFavorite(currentWord.id, !currentWord.favorite)" circle>
                    <el-icon>
                      <Star />
                    </el-icon>
                  </el-button>
                  <el-button :type="currentWord.learned ? 'success' : 'default'"
                    @click="toggleLearned(currentWord.id, !currentWord.learned)" circle>
                    <el-icon>
                      <Check />
                    </el-icon>
                  </el-button>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p class="text-gray-600 mb-1">英式发音:</p>
                  <div class="flex items-center">
                    <span class="text-lg mr-2">{{ currentWord.usphone || '暂无' }}</span>
                    <el-button v-if="currentWord.name" @click="playAudio('us', currentWord.name)" circle>
                      <el-icon>
                        <Mic />
                      </el-icon>
                    </el-button>
                  </div>
                </div>
                <div>
                  <p class="text-gray-600 mb-1">美式发音:</p>
                  <div class="flex items-center">
                    <span class="text-lg mr-2">{{ currentWord.ukphone || '暂无' }}</span>
                    <el-button v-if="currentWord.name" @click="playAudio('uk', currentWord.name)" circle>
                      <el-icon>
                        <Mic />
                      </el-icon>
                    </el-button>
                  </div>
                </div>
              </div>

              <div class="mb-4">
                <p class="text-gray-600 mb-1">翻译:</p>
                <div class="text-lg">
                  <span v-if="currentWord.trans && currentWord.trans.length">
                    {{ currentWord.trans.join('; ') }}
                  </span>
                  <span v-else-if="youdaoData && youdaoData.data && youdaoData.data.entries">
                    {{ youdaoData.data.entries[0]?.explain || '暂无翻译' }}
                  </span>
                  <span v-else>加载中...</span>
                </div>
              </div>

              <div v-if="youdaoData && youdaoData.data && youdaoData.data.entries && youdaoData.data.entries[0]"
                class="mb-4">
                <p class="text-gray-600 mb-1">详细解释:</p>
                <div class="text-lg">
                  {{ youdaoData.data.entries[0].explain }}
                </div>
              </div>
            </div>

            <div class="flex justify-between mt-4">
              <el-button :disabled="currentIndex === 0" @click="prevWord">
                <el-icon>
                  <ArrowLeft />
                </el-icon>
                上一个
              </el-button>
              <el-button :disabled="currentIndex === studyWords.length - 1" @click="nextWord" icon-position="right">
                下一个
                <el-icon>
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </div>
        </template>

        <template v-else>
          <div v-if="words.length === 0" class="text-center py-12 bg-white rounded-lg shadow-md">
            <p class="text-gray-500">暂无单词，请添加或导入单词</p>
          </div>

          <div v-else class="bg-white rounded-lg shadow-md p-4">
            <el-table :data="paginatedWords" style="width: 100%">
              <el-table-column prop="name" label="单词" width="180" />
              <el-table-column label="翻译" width="180">
                <template #default="scope">
                  {{ scope.row.trans ? scope.row.trans.join('; ') : '暂无' }}
                </template>
              </el-table-column>
              <el-table-column label="状态">
                <template #default="scope">
                  <el-tag v-if="scope.row.learned" type="success" class="mr-2">已学会</el-tag>
                  <el-tag v-if="scope.row.favorite" type="warning">收藏</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button :type="scope.row.favorite ? 'warning' : 'default'"
                    @click="toggleFavorite(scope.row.id, !scope.row.favorite)" circle>
                    <el-icon>
                      <Star />
                    </el-icon>
                  </el-button>
                  <el-button :type="scope.row.learned ? 'success' : 'default'"
                    @click="toggleLearned(scope.row.id, !scope.row.learned)" circle>
                    <el-icon>
                      <Check />
                    </el-icon>
                  </el-button>
                  <el-button type="danger" @click="confirmDelete(scope.row.id)" circle>
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <!-- 添加分页组件 -->
            <div class="flex justify-center mt-4">
              <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                :total="filteredWords.length" :page-sizes="[50, 100, 200]" layout="total, sizes, prev, pager, next"
                :pager-count="7" background @size-change="handleSizeChange" @current-change="handleCurrentChange" />
            </div>
          </div>
        </template>
      </div>

      <div class="md:col-span-1">
        <div v-if="studyMode" class="bg-white rounded-lg shadow-md p-4">
          <h3 class="text-lg font-bold mb-4">单词列表</h3>
          <ul class="divide-y">
            <li v-for="(word, index) in studyWords" :key="word.id" :class="[
          'py-2 px-3 cursor-pointer hover:bg-gray-100 transition',
          currentIndex === index ? 'bg-blue-50 font-bold' : ''
        ]" @click="goToWord(index)">
              <div class="flex justify-between items-center">
                <span>{{ word.name }}</span>
                <div class="flex space-x-1">
                  <el-tag v-if="word.learned" type="success" size="small">已学会</el-tag>
                  <el-tag v-if="word.favorite" type="warning" size="small">收藏</el-tag>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <div v-else>
          <div class="bg-white rounded-lg shadow-md p-4 mb-4">
            <h3 class="text-lg font-bold mb-4">收藏单词</h3>
            <ul v-if="favoriteWords.length" class="divide-y">
              <li v-for="word in favoriteWords" :key="word.id" class="py-2">
                <div class="flex justify-between items-center">
                  <span>{{ word.name }}</span>
                  <div class="flex space-x-2">
                    <el-button type="warning" @click="toggleFavorite(word.id, false)" icon="star" circle size="small" />
                  </div>
                </div>
              </li>
            </ul>
            <p v-else class="text-gray-500 text-center py-4">暂无收藏单词</p>
          </div>

          <div class="bg-white rounded-lg shadow-md p-4">
            <h3 class="text-lg font-bold mb-4">已学会单词</h3>
            <ul v-if="learnedWords.length" class="divide-y">
              <li v-for="word in learnedWords" :key="word.id" class="py-2">
                <div class="flex justify-between items-center">
                  <span>{{ word.name }}</span>
                  <div class="flex space-x-2">
                    <el-button type="success" @click="toggleLearned(word.id, false)" icon="check" circle size="small" />
                  </div>
                </div>
              </li>
            </ul>
            <p v-else class="text-gray-500 text-center py-4">暂无已学会单词</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加单词对话框 -->
    <el-dialog v-model="showAddWordDialog" title="添加单词" width="500px">
      <el-form :model="newWord" label-width="80px">
        <el-form-item label="单词" required>
          <el-input v-model="newWord.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddWordDialog = false">取消</el-button>
          <el-button type="primary" @click="addWord">添加</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="showDeleteDialog" title="确认删除" width="400px">
      <p>确定要删除这个单词吗？此操作不可撤销。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="deleteWord">删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, Check, Delete, ArrowLeft, ArrowRight, Mic } from '@element-plus/icons-vue'
import { useWordsStore } from '@/store/words'
import { Word, YoudaoResponse } from '@/types/word'
import { getYoudaoTranslation } from '@/services/words'

const wordsStore = useWordsStore()

// 状态
const loading = ref(false)
const searchQuery = ref('')
const wordLimit = ref(50)
const studyMode = ref(false)
const studyWords = ref<Word[]>([])
const currentIndex = ref(0)
const showAddWordDialog = ref(false)
const showDeleteDialog = ref(false)
const wordToDelete = ref('')
const newWord = ref({ name: '' })
const youdaoData = ref<YoudaoResponse | null>(null)
// 添加分页相关的响应式变量
const currentPage = ref(1)
const pageSize = ref(100)


// 确保 words 是一个计算属性，从 store 获取
const words = computed(() => wordsStore.words || [])
const favoriteWords = computed(() => wordsStore.favoriteWords || [])
const learnedWords = computed(() => wordsStore.learnedWords || [])

// 计算属性
const filteredWords = computed(() => {
  if (!searchQuery.value) return words.value

  const query = searchQuery.value.toLowerCase()
  return words.value.filter(word =>
    word.name.toLowerCase().includes(query) ||
    (word.trans && word.trans.some(t => t.toLowerCase().includes(query)))
  )
})

const currentWord = computed(() => {
  if (studyWords.value.length === 0 || currentIndex.value < 0 || currentIndex.value >= studyWords.value.length) {
    return null
  }
  return studyWords.value[currentIndex.value]
})

// 监听器
watch(currentWord, async (newWord) => {
  if (newWord) {
    await fetchYoudaoData(newWord.name)
  }
})

// 方法
const fetchRandomWordsForStudy = async () => {
  loading.value = true
  try {
    const words = await wordsStore.fetchRandomWords(wordLimit.value)
    if (words.length === 0) {
      ElMessage.warning('没有可学习的单词，请先添加单词')
      return
    }

    studyWords.value = words
    currentIndex.value = 0
    studyMode.value = true

    // 获取第一个单词的有道翻译
    if (words.length > 0) {
      await fetchYoudaoData(words[0].name)
    }
  } catch (error) {
    console.error('Failed to fetch random words:', error)
    ElMessage.error('获取单词失败')
  } finally {
    loading.value = false
  }
}

const fetchYoudaoData = async (word: string) => {
  try {
    // 使用我们的服务函数而不是直接调用 axios
    youdaoData.value = await getYoudaoTranslation(word)
  } catch (error) {
    console.error('Failed to fetch Youdao data:', error)
    youdaoData.value = null
  }
}

const exitStudyMode = () => {
  ElMessageBox.confirm('确定要退出学习模式吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    studyMode.value = false
    studyWords.value = []
    currentIndex.value = 0
  }).catch(() => { })
}

const handlePageChange = (page: number) => {
  currentIndex.value = page - 1
}

const prevWord = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextWord = () => {
  if (currentIndex.value < studyWords.value.length - 1) {
    currentIndex.value++
  }
}

const goToWord = (index: number) => {
  currentIndex.value = index
}

const playAudio = (type: 'us' | 'uk', word: string) => {
  const typeCode = type === 'uk' ? 1 : 0
  const audio = new Audio(`https://dict.youdao.com/dictvoice?type=${typeCode}&audio=${word}`)
  audio.play()
}

const toggleFavorite = async (wordId: string, favorite: boolean) => {
  try {
    await wordsStore.toggleWordFavorite(wordId, favorite)
    ElMessage.success(favorite ? '已添加到收藏' : '已从收藏中移除')
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    ElMessage.error('操作失败')
  }
}

const toggleLearned = async (wordId: string, learned: boolean) => {
  try {
    await wordsStore.toggleWordLearned(wordId, learned)
    ElMessage.success(learned ? '已标记为学会' : '已取消学会标记')
  } catch (error) {
    console.error('Failed to toggle learned:', error)
    ElMessage.error('操作失败')
  }
}

const handleFileChange = (file: any) => {
  if (!file.raw) {
    ElMessage.error('请选择文件')
    return
  }

  if (!file.raw.name.endsWith('.json')) {
    ElMessage.error('只支持 JSON 文件')
    return
  }

  ElMessageBox.confirm('确定要导入这个文件吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    loading.value = true
    try {
      const imported = await wordsStore.importWordList(file.raw)
      ElMessage.success(`成功导入 ${imported.length} 个单词`)
      // 导入成功后刷新单词列表
      await wordsStore.fetchWords()
    } catch (error) {
      console.error('Failed to import words:', error)
      ElMessage.error('导入失败')
    } finally {
      loading.value = false
    }
  }).catch(() => { })
}

const handleExport = async () => {
  try {
    const blob = await wordsStore.exportWordList()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'words.json'
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export words:', error)
    ElMessage.error('导出失败')
  }
}

const addWord = async () => {
  if (!newWord.value.name.trim()) {
    ElMessage.warning('请输入单词')
    return
  }

  try {
    await wordsStore.addNewWord({ name: newWord.value.name.trim() })
    ElMessage.success('添加成功')
    showAddWordDialog.value = false
    newWord.value.name = ''
  } catch (error) {
    console.error('Failed to add word:', error)
    ElMessage.error('添加失败')
  }
}

const confirmDelete = (wordId: string) => {
  wordToDelete.value = wordId
  showDeleteDialog.value = true
}

const deleteWord = async () => {
  if (!wordToDelete.value) return

  try {
    await wordsStore.deleteWordById(wordToDelete.value)
    ElMessage.success('删除成功')
    showDeleteDialog.value = false
  } catch (error) {
    console.error('Failed to delete word:', error)
    ElMessage.error('删除失败')
  }
}

// 添加分页计算属性
const paginatedWords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWords.value.slice(start, end)
})

// 添加分页处理方法
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1  // 重置到第一页
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// 生命周期钩子
onMounted(async () => {
  loading.value = true
  try {
    await wordsStore.fetchWords()
    await wordsStore.fetchFavoriteWords()
    await wordsStore.fetchLearnedWords()
  } catch (error) {
    console.error('Failed to fetch initial data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
})
</script>