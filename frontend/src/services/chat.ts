import axiosInstance from '@/axios'
import { ChatSession, ChatSessionCreate, ChatSessionUpdate, Message } from '@/types/chat'

const API_URL = '/api/chat/'

// export const getChatSessions = async (): Promise<ChatSession[]> => {
//   const response = await axiosInstance.get(API_URL)
//   return response.data
// }

export const getChatSessions = async (): Promise<ChatSession[]> => {
  try {
    const response = await axiosInstance.get(API_URL)
    return response.data
  } catch (error) {
    console.error('获取会话列表失败:', error)
    throw error
  }
}

export const getChatSessionById = async (id: string): Promise<ChatSession> => {
  const response = await axiosInstance.get(`${API_URL}/${id}`)
  return response.data
}

export const createChatSession = async (session: ChatSessionCreate): Promise<ChatSession> => {
  const response = await axiosInstance.post(API_URL, session)
  return response.data
}

export const updateChatSession = async (id: string, session: ChatSessionUpdate): Promise<ChatSession> => {
  const response = await axiosInstance.put(`${API_URL}/${id}`, session)
  return response.data
}

export const deleteChatSession = async (id: string): Promise<boolean> => {
  const response = await axiosInstance.delete(`${API_URL}/${id}`)
  return response.data
}

export const addMessage = async (sessionId: string, message: Message): Promise<ChatSession> => {
  const response = await axiosInstance.post(`${API_URL}/${sessionId}/messages`, message)
  return response.data
}

export const getAIResponse = async (sessionId: string): Promise<Message> => {
  const response = await axiosInstance.post(`${API_URL}/${sessionId}/ai-response`)
  return response.data
}

export const uploadAudio = async (sessionId: string, audioBlob: Blob): Promise<Message> => {
  const formData = new FormData()
  formData.append('audio_file', audioBlob, 'recording.wav')
  
  const response = await axiosInstance.post(`${API_URL}/${sessionId}/upload-audio`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}