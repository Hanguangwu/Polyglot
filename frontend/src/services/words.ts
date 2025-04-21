import api from './api'
import { Word, YoudaoResponse } from '@/types/word'

// 获取单词列表
export const getWords = async (limit?: number, random?: boolean): Promise<Word[]> => {
  const params: any = {}
  if (limit) params.limit = limit
  if (random) params.random = random
  
  const response = await api.get('/words', { params })
  return response.data
}

// 获取收藏单词
export const getFavoriteWords = async (): Promise<Word[]> => {
  const response = await api.get('/words/favorites')
  return response.data
}

// 获取已学会单词
export const getLearnedWords = async (): Promise<Word[]> => {
  const response = await api.get('/words/learned')
  return response.data
}

// 获取需要复习的单词
export const getReviewWords = async (): Promise<Word[]> => {
  const response = await api.get('/words/review')
  return response.data
}

// 添加单词
export const addWord = async (wordData: { name: string, trans?: string[] }): Promise<Word> => {
  const response = await api.post('/words', wordData)
  return response.data
}

// 更新单词
export const updateWord = async (wordId: string, data: Partial<Word>): Promise<Word> => {
  const response = await api.put(`/words/${wordId}`, data)
  return response.data
}

// 删除单词
export const deleteWord = async (wordId: string): Promise<boolean> => {
  const response = await api.delete(`/words/${wordId}`)
  return response.data
}

// 切换收藏状态
export const toggleFavorite = async (wordId: string, favorite: boolean): Promise<Word> => {
  // 使用查询参数
  const response = await api.put(`/words/${wordId}/favorite`, null, {
    params: { favorite }
  })
  return response.data
}

// 切换学会状态
export const toggleLearned = async (wordId: string, learned: boolean): Promise<Word> => {
  // 使用查询参数
  const response = await api.put(`/words/${wordId}/learned`, null, {
    params: { learned }
  })
  return response.data
}

// 导入单词
export const importWords = async (file: File): Promise<Word[]> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/words/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

// 导出单词
export const exportWords = async (): Promise<Blob> => {
  const response = await api.get('/words/export', {
    responseType: 'blob'
  })
  return response.data
}

// 获取有道翻译
export const getYoudaoTranslation = async (word: string): Promise<YoudaoResponse> => {
  // 改为通过我们自己的后端代理请求
  const response = await api.get(`/words/youdao?word=${encodeURIComponent(word)}`)
  return response.data
}

// 添加获取复习单词的方法
export const getWordsForReview = async (): Promise<Word[]> => {
  const response = await api.get('/words/review')
  return response.data
}

// 添加更新单词复习状态的方法
export const updateWordReviewStatus = async (id: string, difficulty: 'easy' | 'medium' | 'difficult'): Promise<Word> => {
  try {
    console.log(`更新单词 ${id} 的复习状态为 ${difficulty}`)
    const response = await api.post(`/words/${id}/review`, { difficulty })
    return response.data
  } catch (error) {
    console.error('更新单词复习状态失败:', error)
    throw error
  }
}