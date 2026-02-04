import apiClient from './client'
import { LoginCredentials, StudentLoginCredentials, TokenResponse } from '../types/auth'

export const authApi = {
  // Regular login
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
    return response.data
  },

  // Student login (simplified)
  studentLogin: async (credentials: StudentLoginCredentials): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login/student', credentials)
    return response.data
  },

  // Register
  register: async (data: {
    username: string
    email: string
    password: string
    full_name: string
    role?: string
  }): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/register', data)
    return response.data
  },

  // Refresh token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // Logout
  logout: async () => {
    const response = await apiClient.post('/auth/logout')
    return response.data
  },
}
