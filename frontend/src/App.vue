<template>
  <div class="min-h-screen flex flex-col">
    <Navbar />
    
    <main class="flex-grow">
      <router-view />
    </main>
    
    <footer v-if="showFooter" class="bg-gray-800 text-white py-6">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p>&copy; 2025 Polyglot. All rights reserved.</p>
          </div>
          
          <div class="flex space-x-4">
            <a href="#" class="text-gray-300 hover:text-white">关于我们</a>
            <a href="#" class="text-gray-300 hover:text-white">隐私政策</a>
            <a href="#" class="text-gray-300 hover:text-white">使用条款</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './layouts/Navbar.vue'

const route = useRoute()

// 计算属性：是否显示底部
const showFooter = computed(() => {
  const noFooterRoutes = ['/login', '/register', '/forgot-password']
  return !noFooterRoutes.includes(route.path)
})
</script>
