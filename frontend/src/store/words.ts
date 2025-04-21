import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Word } from '@/types/word'
import api from '@/services/api'
import { 
  getWords, getFavoriteWords, getLearnedWords, getReviewWords,
  addWord, updateWord, deleteWord, toggleFavorite, toggleLearned,
  importWords as importWordsApi, exportWords as exportWordsApi
} from '@/services/words'

export const useWordsStore = defineStore('words', () => {
  // 状态
  const words = ref<Word[]>([])
  const favoriteWords = ref<Word[]>([])
  const learnedWords = ref<Word[]>([])
  const reviewWords = ref<Word[]>([])
  const loading = ref(false)
  const studyWords = ref<Word[]>([])
  
  // 方法
  const fetchWords = async () => {
    loading.value = true
    try {
      words.value = await getWords()
    } catch (error) {
      console.error('Failed to fetch words:', error)
    } finally {
      loading.value = false
    }
  }
  
  const fetchRandomWords = async (limit: number) => {
    loading.value = true
    try {
      studyWords.value = await getWords(limit, true)
      return studyWords.value
    } catch (error) {
      console.error('Failed to fetch random words:', error)
      return []
    } finally {
      loading.value = false
    }
  }
  
  const fetchFavoriteWords = async () => {
    try {
      favoriteWords.value = await getFavoriteWords()
    } catch (error) {
      console.error('Failed to fetch favorite words:', error)
    }
  }
  
  const fetchLearnedWords = async () => {
    try {
      learnedWords.value = await getLearnedWords()
    } catch (error) {
      console.error('Failed to fetch learned words:', error)
    }
  }
  
  const fetchReviewWords = async () => {
    try {
      reviewWords.value = await getReviewWords()
    } catch (error) {
      console.error('Failed to fetch review words:', error)
    }
  }
  
  const addNewWord = async (wordData: { name: string }) => {
    try {
      const newWord = await addWord({
        name: wordData.name.trim(),
        trans: []  // 添加空的翻译数组
      })
      words.value.unshift(newWord)
      return newWord
    } catch (error) {
      console.error('Failed to add word:', error)
      throw error
    }
  }
  
  const updateWordById = async (wordId: string, data: Partial<Word>) => {
    const updatedWord = await updateWord(wordId, data)
    
    // 更新本地状态
    const index = words.value.findIndex(w => w.id === wordId)
    if (index !== -1) {
      words.value[index] = updatedWord
    }
    
    return updatedWord
  }
  
  const deleteWordById = async (wordId: string) => {
    const success = await deleteWord(wordId)
    
    if (success) {
      // 从本地状态中移除
      words.value = words.value.filter(w => w.id !== wordId)
      favoriteWords.value = favoriteWords.value.filter(w => w.id !== wordId)
      learnedWords.value = learnedWords.value.filter(w => w.id !== wordId)
    }
    
    return success
  }
  
  const toggleWordFavorite = async (wordId: string, favorite: boolean) => {
    const updatedWord = await toggleFavorite(wordId, favorite)
    
    // 更新本地状态
    const index = words.value.findIndex(w => w.id === wordId)
    if (index !== -1) {
      words.value[index] = updatedWord
    }
    
    // 更新收藏列表
    if (favorite) {
      favoriteWords.value.push(updatedWord)
    } else {
      favoriteWords.value = favoriteWords.value.filter(w => w.id !== wordId)
    }
    
    return updatedWord
  }
  
  const toggleWordLearned = async (wordId: string, learned: boolean) => {
    const updatedWord = await toggleLearned(wordId, learned)
    
    // 更新本地状态
    const index = words.value.findIndex(w => w.id === wordId)
    if (index !== -1) {
      words.value[index] = updatedWord
    }
    
    // 更新已学会列表
    if (learned) {
      learnedWords.value.push(updatedWord)
    } else {
      learnedWords.value = learnedWords.value.filter(w => w.id !== wordId)
    }
    
    return updatedWord
  }
  
  const importWordList = async (file: File) => {
    return await importWordsApi(file)
  }
  
  const exportWordList = async () => {
    return await exportWordsApi()
  }
  
  return {
    words,
    favoriteWords,
    learnedWords,
    reviewWords,
    loading,
    studyWords,
    fetchWords,
    fetchRandomWords,
    fetchFavoriteWords,
    fetchLearnedWords,
    fetchReviewWords,
    addNewWord,
    updateWordById,
    deleteWordById,
    toggleWordFavorite,
    toggleWordLearned,
    importWordList,
    exportWordList
  }
})