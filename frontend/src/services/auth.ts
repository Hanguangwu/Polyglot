import api from './api'

export const login = async (email: string, password: string) => {
    try {
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 使用 username 字段
        formData.append('password', password);
        
        console.log('发送登录请求:', email);
        
        const response = await api.post('/auth/login', formData.toString(), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            withCredentials: true // 确保发送凭证
        });
        
        console.log('登录响应:', response.data);
        return response.data;
    } catch (error) {
        console.error('登录请求错误:', error);
        throw error;
    }
};

export const register = async (email: string, password: string, username?: string) => {
    const response = await api.post('/auth/register', {
        email,
        password,
        username
    })

    return response.data
}

export const getProfile = async () => {
    const response = await api.get('/auth/me')
    return response.data
}

export const updateProfile = async (data: { username?: string; avatar?: string }) => {
    const response = await api.put('/auth/me', data)
    return response.data
}

export const changePassword = async (oldPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
    })

    return response.data
}