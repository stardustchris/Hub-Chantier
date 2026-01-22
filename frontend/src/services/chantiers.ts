import api from './api'
import type { Chantier, ChantierCreate, ChantierUpdate, ChantierStatut, PaginatedResponse } from '../types'

export interface ChantiersListParams {
  page?: number
  size?: number
  search?: string
  statut?: ChantierStatut
}

export const chantiersService = {
  async list(params: ChantiersListParams = {}): Promise<PaginatedResponse<Chantier>> {
    const response = await api.get<PaginatedResponse<Chantier>>('/api/chantiers', { params })
    return response.data
  },

  async getById(id: string): Promise<Chantier> {
    const response = await api.get<Chantier>(`/api/chantiers/${id}`)
    return response.data
  },

  async getByCode(code: string): Promise<Chantier> {
    const response = await api.get<Chantier>(`/api/chantiers/code/${code}`)
    return response.data
  },

  async create(data: ChantierCreate): Promise<Chantier> {
    const response = await api.post<Chantier>('/api/chantiers', data)
    return response.data
  },

  async update(id: string, data: ChantierUpdate): Promise<Chantier> {
    const response = await api.put<Chantier>(`/api/chantiers/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/chantiers/${id}`)
  },

  // Gestion du statut
  async changeStatut(id: string, statut: ChantierStatut): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${id}/statut`, { statut })
    return response.data
  },

  async demarrer(id: string): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${id}/demarrer`)
    return response.data
  },

  async receptionner(id: string): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${id}/receptionner`)
    return response.data
  },

  async fermer(id: string): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${id}/fermer`)
    return response.data
  },

  // Gestion des conducteurs
  async addConducteur(chantierId: string, userId: string): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${chantierId}/conducteurs`, { user_id: userId })
    return response.data
  },

  async removeConducteur(chantierId: string, userId: string): Promise<Chantier> {
    const response = await api.delete<Chantier>(`/api/chantiers/${chantierId}/conducteurs/${userId}`)
    return response.data
  },

  // Gestion des chefs
  async addChef(chantierId: string, userId: string): Promise<Chantier> {
    const response = await api.post<Chantier>(`/api/chantiers/${chantierId}/chefs`, { user_id: userId })
    return response.data
  },

  async removeChef(chantierId: string, userId: string): Promise<Chantier> {
    const response = await api.delete<Chantier>(`/api/chantiers/${chantierId}/chefs/${userId}`)
    return response.data
  },
}
