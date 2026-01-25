import api from './api'
import type {
  Affectation,
  AffectationCreate,
  AffectationUpdate,
  PlanningFilters,
  DuplicateAffectationsRequest,
} from '../types'

export interface NonPlanifiesResponse {
  utilisateur_ids: string[]
  date_debut: string
  date_fin: string
  count: number
}

export const planningService = {
  /**
   * Récupère les affectations selon les filtres
   */
  async getAffectations(filters: PlanningFilters): Promise<Affectation[]> {
    const params = new URLSearchParams()
    params.append('date_debut', filters.date_debut)
    params.append('date_fin', filters.date_fin)

    if (filters.utilisateur_ids?.length) {
      filters.utilisateur_ids.forEach(id => params.append('utilisateur_ids', id))
    }
    if (filters.chantier_ids?.length) {
      filters.chantier_ids.forEach(id => params.append('chantier_ids', id))
    }
    if (filters.metiers?.length) {
      filters.metiers.forEach(m => params.append('metiers', m))
    }

    const response = await api.get<Affectation[]>('/api/planning/affectations', { params })
    return response.data
  },

  /**
   * Récupère une affectation par ID
   */
  async getById(id: string): Promise<Affectation> {
    const response = await api.get<Affectation>(`/api/planning/affectations/${id}`)
    return response.data
  },

  /**
   * Crée une nouvelle affectation
   */
  async create(data: AffectationCreate): Promise<Affectation[]> {
    const response = await api.post<Affectation[]>('/api/planning/affectations', data)
    return response.data
  },

  /**
   * Met à jour une affectation
   */
  async update(id: string, data: AffectationUpdate): Promise<Affectation> {
    const response = await api.put<Affectation>(`/api/planning/affectations/${id}`, data)
    return response.data
  },

  /**
   * Supprime une affectation
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/api/planning/affectations/${id}`)
  },

  /**
   * PLN-27: Déplace une affectation vers une nouvelle date/utilisateur
   */
  async move(id: string, newDate: string, newUserId?: string): Promise<Affectation> {
    // Construire le payload avec les types corrects pour le backend
    const data: Record<string, string | number> = { date: newDate }
    if (newUserId) {
      // Convertir explicitement en number pour le backend Pydantic
      data.utilisateur_id = parseInt(newUserId, 10)
    }
    const response = await api.put<Affectation>(`/api/planning/affectations/${id}`, data)
    return response.data
  },

  /**
   * Duplique les affectations d'une période vers une autre
   */
  async duplicate(data: DuplicateAffectationsRequest): Promise<Affectation[]> {
    const response = await api.post<Affectation[]>('/api/planning/affectations/duplicate', data)
    return response.data
  },

  /**
   * Récupère les utilisateurs non planifiés sur une période
   */
  async getNonPlanifies(date_debut: string, date_fin: string): Promise<NonPlanifiesResponse> {
    const response = await api.get<NonPlanifiesResponse>('/api/planning/non-planifies', {
      params: { date_debut, date_fin },
    })
    return response.data
  },

  /**
   * Récupère les affectations d'un chantier
   */
  async getByChantier(
    chantierId: string,
    date_debut: string,
    date_fin: string
  ): Promise<Affectation[]> {
    const response = await api.get<Affectation[]>(
      `/api/planning/chantiers/${chantierId}/affectations`,
      { params: { date_debut, date_fin } }
    )
    return response.data
  },

  /**
   * Récupère les affectations d'un utilisateur
   */
  async getByUtilisateur(
    utilisateurId: string,
    date_debut: string,
    date_fin: string
  ): Promise<Affectation[]> {
    const response = await api.get<Affectation[]>(
      `/api/planning/utilisateurs/${utilisateurId}/affectations`,
      { params: { date_debut, date_fin } }
    )
    return response.data
  },
}
