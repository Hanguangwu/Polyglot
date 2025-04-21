export interface User {
  id: string
  email: string
  username?: string
  avatar?: string
  createdAt: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  username?: string
}

export interface ProfileUpdateData {
  username?: string
  avatar?: string
}

export interface PasswordChangeData {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}