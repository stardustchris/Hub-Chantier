import api from './api'

export interface User {
  id: number
  email: string
  nom: string
  prenom: string
  role: string
  is_active: boolean
}

export interface AuthResponse {
  user: User
  access_token: string
  token_type: string
}

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post<AuthResponse>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  async register(data: {
    email: string
    password: string
    nom: string
    prenom: string
  }): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/register', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },
}
