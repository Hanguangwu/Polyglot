export interface Message {
  role: 'user' | 'assistant'
  content: string
  audio_url?: string
  corrected_content?: string
  score?: number
  feedback?: string
}

export interface ChatSessionBase {
  title: string
  type: 'casual' | 'ielts'
}

export interface ChatSessionCreate extends ChatSessionBase {}

export interface ChatSessionUpdate {
  title?: string
  messages?: Message[]
}

export interface ChatSession extends ChatSessionBase {
  id: string
  user_id: string
  created_at: string
  messages: Message[]
}