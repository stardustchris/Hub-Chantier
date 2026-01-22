import api from './api'
import type { User, UserCreate, UserUpdate, PaginatedResponse } from '../types'

export interface UsersListParams {
  page?: number
  size?: number
  search?: string
  role?: string
  is_active?: boolean
}

export const usersService = {
  async list(params: UsersListParams = {}): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/api/users', { params })
    return response.data
  },

  async getById(id: string): Promise<User> {
    const response = await api.get<User>(`/api/users/${id}`)
    return response.data
  },

  async create(data: UserCreate): Promise<User> {
    const response = await api.post<User>('/api/auth/register', data)
    return response.data
  },

  async update(id: string, data: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/api/users/${id}`, data)
    return response.data
  },

  async activate(id: string): Promise<User> {
    const response = await api.post<User>(`/api/users/${id}/activate`)
    return response.data
  },

  async deactivate(id: string): Promise<User> {
    const response = await api.post<User>(`/api/users/${id}/deactivate`)
    return response.data
  },
}
