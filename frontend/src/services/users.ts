import api from './api'
import type { User, UserCreate, UserUpdate, PaginatedResponse } from '../types'

export interface UsersListParams {
  page?: number
  size?: number
  search?: string
  role?: string
  is_active?: boolean
}

export interface NavigationIds {
  prevId: string | null
  nextId: string | null
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

  /**
   * Récupère les IDs précédent/suivant pour navigation (USR-09).
   */
  async getNavigationIds(currentId: string): Promise<NavigationIds> {
    try {
      // Récupérer la liste complète des IDs triés
      const response = await api.get<PaginatedResponse<User>>('/api/users', {
        params: { size: 500 },
      })
      const ids = response.data.items.map((u) => u.id)
      const currentIndex = ids.indexOf(currentId)

      return {
        prevId: currentIndex > 0 ? ids[currentIndex - 1] : null,
        nextId: currentIndex < ids.length - 1 ? ids[currentIndex + 1] : null,
      }
    } catch {
      return { prevId: null, nextId: null }
    }
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
