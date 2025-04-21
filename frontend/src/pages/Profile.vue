<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">个人中心</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 个人信息 -->
      <div class="md:col-span-2">
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 class="text-lg font-semibold mb-4">个人信息</h2>
          
          <el-form 
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-position="top"
          >
            <div class="flex items-center mb-6">
              <div class="mr-6">
                <el-avatar :size="80" :src="profileForm.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
              </div>
              <div>
                <el-upload
                  action=""
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleAvatarChange"
                >
                  <el-button size="small">更换头像</el-button>
                </el-upload>
              </div>
            </div>
            
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" disabled />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold mb-4">修改密码</h2>
          
          <el-form 
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-position="top"
          >
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input 
                v-model="passwordForm.oldPassword" 
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="passwordForm.newPassword" 
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input 
                v-model="passwordForm.confirmPassword" 
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- 学习统计 -->
      <div>
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 class="text-lg font-semibold mb-4">学习统计</h2>
          
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">总单词数</span>
              <span class="font-medium">{{ stats.totalWords }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">收藏单词数</span>
              <span class="font-medium">{{ stats.favoriteWords }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">已掌握单词</span>
              <span class="font-medium">{{ stats.masteredWords }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">学习天数</span>
              <span class="font-medium">{{ stats.learningDays }}</span>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-lg font-semibold mb-4">账户信息</h2>
          
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">账户创建时间</span>
              <span class="font-medium">{{ formatDate(user?.createdAt) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">最近登录时间</span>
              <span class="font-medium">{{ formatDate(new Date().toISOString()) }}</span>
            </div>
          </div>
          
          <div class="mt-6">
            <el-button type="danger" @click="logout">退出登录</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { useWordsStore } from '@/store/words'
import { getProfile, updateProfile as updateProfileApi, changePassword as changePasswordApi } from '@/services/auth'

const router = useRouter()
const authStore = useAuthStore()
const wordsStore = useWordsStore()

// 状态
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const updating = ref(false)
const changingPassword = ref(false)
const user = computed(() => authStore.user)

// 表单数据
const profileForm = reactive({
  username: '',
  email: '',
  avatar: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 学习统计
const stats = reactive({
  totalWords: 0,
  favoriteWords: 0,
  masteredWords: 0,
  learningDays: 0
})

// 表单验证规则
const validatePass = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const profileRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ]
})

const passwordRules = reactive<FormRules>({
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ]
})

// 生命周期钩子
onMounted(async () => {
  await fetchProfile()
  await fetchStats()
})

// 方法
const fetchProfile = async () => {
  try {
    const profile = await getProfile()
    profileForm.username = profile.username || ''
    profileForm.email = profile.email
    profileForm.avatar = profile.avatar || ''
  } catch (error) {
    console.error('Failed to fetch profile:', error)
    ElMessage.error('获取个人信息失败')
  }
}

const fetchStats = async () => {
  try {
    await wordsStore.fetchWords()
    await wordsStore.fetchFavoriteWords()
    
    stats.totalWords = wordsStore.words.length
    stats.favoriteWords = wordsStore.favoriteWords.length
    stats.masteredWords = Math.floor(wordsStore.words.length * 0.4) // 模拟数据
    stats.learningDays = Math.floor(Math.random() * 30) + 1 // 模拟数据
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        await updateProfileApi({
          username: profileForm.username,
          avatar: profileForm.avatar
        })
        ElMessage.success('个人信息更新成功')
      } catch (error) {
        console.error('Failed to update profile:', error)
        ElMessage.error('更新个人信息失败')
      } finally {
        updating.value = false
      }
    }
  })
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      changingPassword.value = true
      try {
        await changePasswordApi(passwordForm.oldPassword, passwordForm.newPassword)
        ElMessage.success('密码修改成功')
        
        // 重置表单
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } catch (error) {
        console.error('Failed to change password:', error)
        ElMessage.error('密码修改失败')
      } finally {
        changingPassword.value = false
      }
    }
  })
}

const handleAvatarChange = (file: any) => {
  // 这里可以实现头像上传逻辑
  // 简化起见，我们假设直接获取了URL
  const fakeUrl = URL.createObjectURL(file.raw)
  profileForm.avatar = fakeUrl
}

const logout = () => {
  authStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>