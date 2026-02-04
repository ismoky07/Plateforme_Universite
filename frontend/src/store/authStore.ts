import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, UserRole } from '../types/auth'
import { authApi } from '../api/auth'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (username: string, password: string) => Promise<void>
  studentLogin: (numero: string, nom: string, prenom: string) => Promise<void>
  logout: () => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.login({ username, password })
          localStorage.setItem('token', response.access_token)

          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Erreur de connexion'
          set({ error: message, isLoading: false })
          throw error
        }
      },

      studentLogin: async (numero: string, nom: string, prenom: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.studentLogin({
            numero_etudiant: numero,
            nom,
            prenom,
          })
          localStorage.setItem('token', response.access_token)

          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Erreur de connexion'
          set({ error: message, isLoading: false })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('token')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      setError: (error: string | null) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
