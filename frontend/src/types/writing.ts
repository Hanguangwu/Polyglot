export interface Suggestion {
  type: 'grammar' | 'spelling' | 'style'
  text: string
  suggestion: string
  explanation: string
}

export interface WritingFeedback {
  original: string
  corrected: string
  suggestions: Suggestion[]
}

export interface WritingBase {
  title: string
  content: string
  topic?: string
  time_spent?: number
}

export interface WritingCreate extends WritingBase {}

export interface WritingUpdate {
  title?: string
  content?: string
  topic?: string
  time_spent?: number
  feedback?: string
  corrected_content?: string
  model_essay?: string
  score?: number
}

export interface Writing extends WritingBase {
  id: string
  user_id: string
  created_at: string
  feedback?: string
  corrected_content?: string
  model_essay?: string
  score?: number
}