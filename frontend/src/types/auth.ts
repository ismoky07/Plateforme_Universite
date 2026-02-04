export type UserRole = 'student' | 'professor' | 'admin'

export interface User {
  username: string
  email?: string
  full_name: string
  role: UserRole
  numero_etudiant?: string
  nom?: string
  prenom?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface StudentLoginCredentials {
  numero_etudiant: string
  nom: string
  prenom: string
}

export interface TokenResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in: number
  user: User
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
