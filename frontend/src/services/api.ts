import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  timeout: 10000,
  withCredentials: true,  // 允许跨域请求携带凭证
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // 处理响应错误
      ElMessage.error(error.response.data.detail || '请求失败')
    } else if (error.request) {
      // 处理请求错误
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      // 处理其他错误
      ElMessage.error('发生错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default api