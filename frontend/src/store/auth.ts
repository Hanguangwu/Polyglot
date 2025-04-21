import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { User } from '@/types/user'
import { login as loginApi, register as registerApi, getProfile } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  
  // 方法
  const login = async (email: string, password: string) => {
    try {
      const response = await loginApi(email, password)
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      
      // 获取用户信息
      await fetchUserProfile()
      
      return response
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }
  
  const register = async (email: string, password: string, username?: string) => {
    try {
      const response = await registerApi(email, password, username)
      return response
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  }
  
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
  
  const fetchUserProfile = async () => {
    if (!token.value) return
    
    try {
      const userData = await getProfile()
      user.value = userData
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    }
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUserProfile
  }
})