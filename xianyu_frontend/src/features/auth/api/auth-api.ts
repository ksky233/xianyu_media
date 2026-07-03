import { apiClient } from '@/lib/api-client'
import type { LoginFormValues } from '@/features/auth/schemas/auth-schema'

export interface UserInfo {
  id: number
  username: string
  email: string
  role: string
  created_at: string
  updated_at?: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user_info: UserInfo
}

export function login(data: LoginFormValues) {
  return apiClient<LoginResponse>('/api/v1/user/login', {
    method: 'POST',
    body: data,
  })
}

export function getUserProfile() {
  return apiClient<UserInfo>('/api/v1/user/profile')
}
