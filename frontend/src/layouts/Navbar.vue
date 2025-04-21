<template>
  <nav class="bg-blue-600 text-white shadow-md">
    <div class="container mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-xl font-bold">Polyglot</router-link>
          
          <div class="hidden md:flex space-x-4">
            <router-link to="/" class="hover:text-blue-200 transition-colors">首页</router-link>
            <router-link v-if="isAuthenticated" to="/words" class="hover:text-blue-200 transition-colors">背单词</router-link>
            <router-link v-if="isAuthenticated" to="/chat" class="hover:text-blue-200 transition-colors">AI 聊天</router-link>
            <router-link v-if="isAuthenticated" to="/writing" class="hover:text-blue-200 transition-colors">写作检查</router-link>
            <router-link v-if="isAuthenticated" to="/review" class="hover:text-blue-200 transition-colors">复习</router-link>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <template v-if="isAuthenticated">
            <router-link to="/profile" class="hover:text-blue-200 transition-colors">个人中心</router-link>
            <button @click="logout" class="hover:text-blue-200 transition-colors">退出</button>
          </template>
          <template v-else>
            <router-link to="/login" class="hover:text-blue-200 transition-colors">登录</router-link>
            <router-link to="/register" class="bg-white text-blue-600 px-3 py-1 rounded hover:bg-blue-100 transition-colors">注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>