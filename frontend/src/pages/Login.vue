<template>
    <div class="min-h-screen flex items-center justify-center bg-login-bg bg-cover bg-center">
        <div class="max-w-md w-full bg-white bg-opacity-90 rounded-lg shadow-lg p-8">
            <h1 class="text-3xl font-bold text-center mb-6">登录</h1>

            <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-position="top">
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="loginForm.email" placeholder="请输入邮箱" />
                </el-form-item>

                <el-form-item label="密码" prop="password">
                    <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
                </el-form-item>

                <div class="flex justify-between items-center mb-6">
                    <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                    <router-link to="/forgot-password" class="text-primary-600 hover:text-primary-800">
                        忘记密码？
                    </router-link>
                </div>

                <el-button type="primary" class="w-full" :loading="loading" @click="handleLogin">
                    登录
                </el-button>
            </el-form>

            <div class="mt-6 text-center">
                <p class="text-gray-600">
                    还没有账号？
                    <router-link to="/register" class="text-primary-600 hover:text-primary-800">
                        立即注册
                    </router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = reactive({
    email: '',
    password: ''
})

const loginRules = {
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
    ]
}

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const handleLogin = async () => {
    if (!loginFormRef.value) return

    try {
        loading.value = true
        await loginFormRef.value.validate()

        //console.log('开始登录:', loginForm.email);
        const result = await authStore.login(loginForm.email, loginForm.password)
        console.log('登录结果:', result);

        ElMessage.success('登录成功')
        router.push('/')
    } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查邮箱和密码')
    } finally {
        loading.value = false
    }
}
</script>