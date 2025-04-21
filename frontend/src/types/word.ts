export interface Word {
  id: string
  name: string
  trans: string[]
  usphone?: string
  ukphone?: string
  definition?: string
  example?: string
  favorite: boolean
  learned: boolean
  createdAt: string
  lastReviewed?: string
  reviewCount?: number
}

export interface WordCreate {
  name: string
  trans?: string[]
  usphone?: string
  ukphone?: string
  definition?: string
  example?: string
}

export interface WordFormData {
  name: string
  trans?: string[]
  usphone?: string
  ukphone?: string
  definition?: string
  example?: string
}

export interface YoudaoResponse {
  result: {
    msg: string
    code: number
  }
  data: {
    entries: {
      explain: string
      entry: string
    }[]
    query: string
    language: string
    type: string
  }
}