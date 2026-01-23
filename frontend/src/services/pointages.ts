import api from './api'
import type {
  Pointage,
  PointageCreate,
  PointageUpdate,
  PointageFilters,
  FeuilleHeures,
  FeuilleHeuresFilters,
  NavigationSemaine,
  VueChantier,
  VueCompagnon,
  VariablePaieCreate,
  JaugeAvancement,
  ExportFeuilleHeuresRequest,
  PaginatedResponse,
} from '../types'

export interface BulkCreateFromPlanningRequest {
  utilisateur_id: number
  semaine_debut: string
  affectations: Array<{
    affectation_id: number
    chantier_id: number
    date_affectation: string
    heures_prevues: string
  }>
}

export const pointagesService = {
  // ===== POINTAGES CRUD =====

  /**
   * Crée un nouveau pointage
   */
  async create(data: PointageCreate, currentUserId: number): Promise<Pointage> {
    const response = await api.post<Pointage>('/api/pointages', data, {
      params: { current_user_id: currentUserId },
    })
    return response.data
  },

  /**
   * Liste les pointages avec filtres (FDH-04)
   */
  async list(filters: PointageFilters = {}): Promise<PaginatedResponse<Pointage>> {
    const params = new URLSearchParams()
    if (filters.utilisateur_id) params.append('utilisateur_id', String(filters.utilisateur_id))
    if (filters.chantier_id) params.append('chantier_id', String(filters.chantier_id))
    if (filters.date_debut) params.append('date_debut', filters.date_debut)
    if (filters.date_fin) params.append('date_fin', filters.date_fin)
    if (filters.statut) params.append('statut', filters.statut)
    if (filters.page) params.append('page', String(filters.page))
    if (filters.page_size) params.append('page_size', String(filters.page_size))

    const response = await api.get<PaginatedResponse<Pointage>>('/api/pointages', { params })
    return response.data
  },

  /**
   * Récupère un pointage par ID
   */
  async getById(id: number): Promise<Pointage> {
    const response = await api.get<Pointage>(`/api/pointages/${id}`)
    return response.data
  },

  /**
   * Met à jour un pointage (si brouillon ou rejeté)
   */
  async update(id: number, data: PointageUpdate, currentUserId: number): Promise<Pointage> {
    const response = await api.put<Pointage>(`/api/pointages/${id}`, data, {
      params: { current_user_id: currentUserId },
    })
    return response.data
  },

  /**
   * Supprime un pointage (si brouillon ou rejeté)
   */
  async delete(id: number, currentUserId: number): Promise<void> {
    await api.delete(`/api/pointages/${id}`, {
      params: { current_user_id: currentUserId },
    })
  },

  // ===== WORKFLOW VALIDATION =====

  /**
   * Signe un pointage (FDH-12)
   */
  async sign(id: number, signature: string): Promise<Pointage> {
    const response = await api.post<Pointage>(`/api/pointages/${id}/sign`, { signature })
    return response.data
  },

  /**
   * Soumet un pointage pour validation
   */
  async submit(id: number): Promise<Pointage> {
    const response = await api.post<Pointage>(`/api/pointages/${id}/submit`)
    return response.data
  },

  /**
   * Valide un pointage
   */
  async validate(id: number, validateurId: number): Promise<Pointage> {
    const response = await api.post<Pointage>(`/api/pointages/${id}/validate`, null, {
      params: { validateur_id: validateurId },
    })
    return response.data
  },

  /**
   * Rejette un pointage
   */
  async reject(id: number, motif: string, validateurId: number): Promise<Pointage> {
    const response = await api.post<Pointage>(
      `/api/pointages/${id}/reject`,
      { motif },
      { params: { validateur_id: validateurId } }
    )
    return response.data
  },

  // ===== FEUILLES D'HEURES =====

  /**
   * Liste les feuilles d'heures
   */
  async listFeuilles(filters: FeuilleHeuresFilters = {}): Promise<PaginatedResponse<FeuilleHeures>> {
    const params = new URLSearchParams()
    if (filters.utilisateur_id) params.append('utilisateur_id', String(filters.utilisateur_id))
    if (filters.annee) params.append('annee', String(filters.annee))
    if (filters.numero_semaine) params.append('numero_semaine', String(filters.numero_semaine))
    if (filters.statut) params.append('statut', filters.statut)
    if (filters.page) params.append('page', String(filters.page))
    if (filters.page_size) params.append('page_size', String(filters.page_size))

    const response = await api.get<PaginatedResponse<FeuilleHeures>>('/api/pointages/feuilles', { params })
    return response.data
  },

  /**
   * Récupère une feuille d'heures par ID
   */
  async getFeuilleById(id: number): Promise<FeuilleHeures> {
    const response = await api.get<FeuilleHeures>(`/api/pointages/feuilles/${id}`)
    return response.data
  },

  /**
   * Récupère la feuille d'heures d'un utilisateur pour une semaine (FDH-05)
   */
  async getFeuilleUtilisateurSemaine(utilisateurId: number, semaineDebut: string): Promise<FeuilleHeures> {
    const response = await api.get<FeuilleHeures>(
      `/api/pointages/feuilles/utilisateur/${utilisateurId}/semaine`,
      { params: { semaine_debut: semaineDebut } }
    )
    return response.data
  },

  /**
   * Navigation par semaine (FDH-02)
   */
  async getNavigation(semaineDebut: string): Promise<NavigationSemaine> {
    const response = await api.get<NavigationSemaine>('/api/pointages/navigation', {
      params: { semaine_debut: semaineDebut },
    })
    return response.data
  },

  // ===== VUES HEBDOMADAIRES (FDH-01) =====

  /**
   * Vue par chantiers
   */
  async getVueChantiers(semaineDebut: string, chantierIds?: number[]): Promise<VueChantier[]> {
    const params = new URLSearchParams()
    params.append('semaine_debut', semaineDebut)
    if (chantierIds?.length) {
      params.append('chantier_ids', chantierIds.join(','))
    }

    const response = await api.get<VueChantier[]>('/api/pointages/vues/chantiers', { params })
    return response.data
  },

  /**
   * Vue par compagnons
   */
  async getVueCompagnons(semaineDebut: string, utilisateurIds?: number[]): Promise<VueCompagnon[]> {
    const params = new URLSearchParams()
    params.append('semaine_debut', semaineDebut)
    if (utilisateurIds?.length) {
      params.append('utilisateur_ids', utilisateurIds.join(','))
    }

    const response = await api.get<VueCompagnon[]>('/api/pointages/vues/compagnons', { params })
    return response.data
  },

  // ===== VARIABLES DE PAIE (FDH-13) =====

  /**
   * Crée une variable de paie
   */
  async createVariablePaie(data: VariablePaieCreate): Promise<void> {
    await api.post('/api/pointages/variables-paie', data)
  },

  // ===== STATISTIQUES (FDH-14, FDH-15) =====

  /**
   * Jauge d'avancement (FDH-14)
   */
  async getJaugeAvancement(
    utilisateurId: number,
    semaineDebut: string,
    heuresPlanifiees = 35
  ): Promise<JaugeAvancement> {
    const response = await api.get<JaugeAvancement>(
      `/api/pointages/stats/jauge-avancement/${utilisateurId}`,
      { params: { semaine_debut: semaineDebut, heures_planifiees: heuresPlanifiees } }
    )
    return response.data
  },

  // ===== EXPORT (FDH-03, FDH-17, FDH-19) =====

  /**
   * Exporte les feuilles d'heures
   */
  async export(data: ExportFeuilleHeuresRequest, currentUserId: number): Promise<Blob> {
    const response = await api.post('/api/pointages/export', data, {
      params: { current_user_id: currentUserId },
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Génère une feuille de route (FDH-19)
   */
  async getFeuilleRoute(utilisateurId: number, semaineDebut: string): Promise<unknown> {
    const response = await api.get(`/api/pointages/feuille-route/${utilisateurId}`, {
      params: { semaine_debut: semaineDebut },
    })
    return response.data
  },

  // ===== INTEGRATION PLANNING (FDH-10) =====

  /**
   * Crée des pointages en masse depuis le planning
   */
  async bulkCreateFromPlanning(data: BulkCreateFromPlanningRequest, currentUserId: number): Promise<Pointage[]> {
    const response = await api.post<Pointage[]>('/api/pointages/bulk-from-planning', data, {
      params: { current_user_id: currentUserId },
    })
    return response.data
  },
}
