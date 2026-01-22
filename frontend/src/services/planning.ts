import api from './api'
import type {
  Affectation,
  AffectationCreate,
  AffectationUpdate,
  AffectationListResponse,
  DeplacerAffectation,
  DupliquerAffectations,
} from '../types'

export interface PlanningListParams {
  date_debut: string
  date_fin: string
  utilisateur_id?: number
  chantier_id?: number
  skip?: number
  limit?: number
}

export const planningService = {
  /**
   * Liste les affectations pour une période (PLN-01, PLN-02).
   */
  async list(params: PlanningListParams): Promise<AffectationListResponse> {
    const response = await api.get<AffectationListResponse>('/api/planning', { params })
    return response.data
  },

  /**
   * Récupère toutes les affectations pour une date (PLN-21).
   */
  async getByDate(date: string): Promise<AffectationListResponse> {
    const response = await api.get<AffectationListResponse>(`/api/planning/date/${date}`)
    return response.data
  },

  /**
   * Récupère une affectation par ID.
   */
  async getById(id: string): Promise<Affectation> {
    const response = await api.get<Affectation>(`/api/planning/${id}`)
    return response.data
  },

  /**
   * Crée une nouvelle affectation (PLN-03, PLN-28).
   */
  async create(data: AffectationCreate): Promise<Affectation> {
    const response = await api.post<Affectation>('/api/planning', data)
    return response.data
  },

  /**
   * Met à jour une affectation existante.
   */
  async update(id: string, data: AffectationUpdate): Promise<Affectation> {
    const response = await api.put<Affectation>(`/api/planning/${id}`, data)
    return response.data
  },

  /**
   * Supprime une affectation.
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/api/planning/${id}`)
  },

  /**
   * Déplace une affectation vers une nouvelle date/chantier (PLN-27 Drag&Drop).
   */
  async deplacer(id: string, data: DeplacerAffectation): Promise<Affectation> {
    const response = await api.post<Affectation>(`/api/planning/${id}/deplacer`, data)
    return response.data
  },

  /**
   * Duplique les affectations d'une période vers une autre (PLN-16).
   */
  async dupliquer(data: DupliquerAffectations): Promise<Affectation[]> {
    const response = await api.post<Affectation[]>('/api/planning/dupliquer', data)
    return response.data
  },

  /**
   * Récupère les IDs des utilisateurs non planifiés pour une date (PLN-04, PLN-11).
   */
  async getUtilisateursNonPlanifies(date: string): Promise<number[]> {
    const response = await api.get<number[]>(`/api/planning/non-planifies/${date}`)
    return response.data
  },
}
