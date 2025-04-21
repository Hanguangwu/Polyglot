<template>
  <footer class="bg-gray-800 text-white py-8">
    <div class="container mx-auto px-4">
      <div class="flex flex-col md:flex-row justify-between">
        <div class="mb-6 md:mb-0">
          <h2 class="text-xl font-bold mb-4">Polyglot</h2>
          <p class="text-gray-400">您的英语学习助手</p>
        </div>
        
        <div class="mb-6 md:mb-0">
          <h3 class="text-lg font-semibold mb-4">快速链接</h3>
          <ul class="space-y-2">
            <li><router-link to="/" class="text-gray-400 hover:text-white transition-colors">首页</router-link></li>
            <li><router-link to="/words" class="text-gray-400 hover:text-white transition-colors">背单词</router-link></li>
            <li><router-link to="/chat" class="text-gray-400 hover:text-white transition-colors">AI 聊天</router-link></li>
            <li><router-link to="/writing" class="text-gray-400 hover:text-white transition-colors">写作检查</router-link></li>
          </ul>
        </div>
        
        <div>
          <h3 class="text-lg font-semibold mb-4">联系我们</h3>
          <ul class="space-y-2">
            <li class="text-gray-400">邮箱: support@polyglot.com</li>
            <li class="text-gray-400">微信: Polyglot_Support</li>
          </ul>
        </div>
      </div>
      
      <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
        <p>&copy; {{ new Date().getFullYear() }} Polyglot. 保留所有权利。</p>
      </div>
    </div>
  </footer>
</template>