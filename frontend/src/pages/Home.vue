<template>
  <div class="min-h-screen bg-home-bg bg-cover bg-center">
    <div class="container mx-auto px-4 py-12">
      <div class="max-w-4xl mx-auto bg-white bg-opacity-90 rounded-lg shadow-lg p-8">
        <h1 class="text-4xl font-bold text-center mb-8">欢迎使用 Polyglot</h1>
        
        <div v-if="!isAuthenticated" class="flex justify-center space-x-6 mb-8">
          <router-link 
            to="/login" 
            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
          >
            登录
          </router-link>
          <router-link 
            to="/register" 
            class="bg-white border border-blue-600 text-blue-600 hover:bg-blue-50 font-medium py-2 px-6 rounded-lg transition-colors"
          >
            注册
          </router-link>
        </div>
        
        <div v-if="isAuthenticated" class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <div class="bg-primary-50 p-6 rounded-lg shadow">
            <h2 class="text-2xl font-semibold mb-4">单词学习</h2>
            <p class="text-gray-700 mb-4">
              通过智能记忆系统，高效学习和记忆英语单词。支持导入导出，自定义复习计划。
            </p>
            <router-link 
              to="/words" 
              class="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              开始学习
            </router-link>
          </div>
          
          <div class="bg-primary-50 p-6 rounded-lg shadow">
            <h2 class="text-2xl font-semibold mb-4">AI 对话</h2>
            <p class="text-gray-700 mb-4">
              与AI进行英语对话，提高口语和听力能力。多种场景选择，实时反馈。
            </p>
            <router-link 
              to="/chat" 
              class="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              开始对话
            </router-link>
          </div>
        </div>
        
        <div v-if="isAuthenticated" class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-primary-50 p-6 rounded-lg shadow">
            <h2 class="text-2xl font-semibold mb-4">写作助手</h2>
            <p class="text-gray-700 mb-4">
              智能检查英语写作，提供语法、拼写和风格建议，帮助提高写作水平。
            </p>
            <router-link 
              to="/writing" 
              class="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              开始写作
            </router-link>
          </div>
          
          <div class="bg-primary-50 p-6 rounded-lg shadow">
            <h2 class="text-2xl font-semibold mb-4">单词复习</h2>
            <p class="text-gray-700 mb-4">
              基于间隔重复记忆原理，科学安排复习计划，提高记忆效率。
            </p>
            <router-link 
              to="/review" 
              class="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition-colors"
            >
              开始复习
            </router-link>
          </div>
        </div>
        
        <div v-if="!isAuthenticated" class="mt-8">
          <h2 class="text-2xl font-semibold mb-4 text-center">Polyglot 功能介绍</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="flex items-start space-x-3">
              <div class="bg-blue-100 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold">智能单词学习</h3>
                <p class="text-gray-600">基于记忆曲线的科学记忆方法，提高单词记忆效率</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-3">
              <div class="bg-blue-100 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold">AI 英语对话</h3>
                <p class="text-gray-600">与AI进行多场景英语对话，提高口语和听力能力</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-3">
              <div class="bg-blue-100 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold">写作助手</h3>
                <p class="text-gray-600">智能检查英语写作，提供语法和风格建议</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-3">
              <div class="bg-blue-100 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold">个性化学习计划</h3>
                <p class="text-gray-600">根据学习进度自动调整学习内容和复习计划</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <Footer />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import Footer from '@/layouts/Footer.vue'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>