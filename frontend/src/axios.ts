import axios from 'axios'

const instance = axios.create({
    baseURL: import.meta.env.BACKEND_BASE_URL,
    timeout: 60000,  // 增加超时时间到60秒
    withCredentials: true
})

instance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        //const token = store.state.auth.token;
        //console.log("当前令牌:", token); // 打印令牌以进行调试  
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        } else {
            console.warn("未提供有效的身份验证令牌");
        }
        return config;
    },
    error => {
        return Promise.reject(error)
    }
)

instance.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

export default instance