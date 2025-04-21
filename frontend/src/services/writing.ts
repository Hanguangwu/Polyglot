import axiosInstance from '@/axios'  // 修改这里，使用配置了认证的实例
import { Writing, WritingCreate, WritingUpdate } from '@/types/writing'

// 修改API路径，确保与后端路由匹配
const API_URL = '/api/writing/'  // 确保这里的路径与后端路由前缀匹配

export const getWritings = async (): Promise<Writing[]> => {
  const response = await axiosInstance.get(API_URL)  // 使用 axiosInstance
  return response.data
}

export const getWritingById = async (id: string): Promise<Writing> => {
  const response = await axiosInstance.get(`${API_URL}/${id}`)  // 使用 axiosInstance
  return response.data
}

export const createWriting = async (writing: WritingCreate): Promise<Writing> => {
  const response = await axiosInstance.post(API_URL, writing)  // 使用 axiosInstance
  return response.data
}

export const updateWriting = async (id: string, writing: WritingUpdate): Promise<Writing> => {
  try {
    console.log("更新写作:", id, writing);  // 添加调试日志
    const response = await axiosInstance.put(`${API_URL}${id}`, writing);
    return response.data;
  } catch (error) {
    console.error("更新写作失败:", error);
    throw error;
  }
}

export const deleteWriting = async (id: string): Promise<boolean> => {
  const response = await axiosInstance.delete(`${API_URL}/${id}`)  // 使用 axiosInstance
  return response.data
}

export const checkWriting = async (data: { content: string, topic: string }): Promise<any> => {
  try {
    console.log("发送写作检查请求:", data)  // 添加调试日志
    const response = await axiosInstance.post(`${API_URL}check`, data)  // 注意这里的路径
    console.log("收到写作检查响应:", response.data)  // 添加调试日志
    return response.data
  } catch (error) {
    console.error("写作检查请求失败:", error)
    throw error
  }
}