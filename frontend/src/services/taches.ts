/**
 * Service API pour le module Taches (CDC Section 13 - TAC-01 à TAC-20)
 */

import api from './api'
import type {
  Tache,
  TacheCreate,
  TacheUpdate,
  TacheStats,
  TemplateModele,
  TemplateCreate,
  FeuilleTache,
  FeuilleTacheCreate,
  PaginatedResponse,
} from '../types'

// ===== TACHES =====

export interface TacheListParams {
  page?: number
  size?: number
  query?: string
  statut?: string
  include_sous_taches?: boolean
}

export interface TacheListResponse extends PaginatedResponse<Tache> {}

export interface TemplateListResponse extends PaginatedResponse<TemplateModele> {
  categories: string[]
}

export interface FeuilleTacheListResponse extends PaginatedResponse<FeuilleTache> {
  total_heures: number
  total_quantite: number
}

export const tachesService = {
  // ===== Taches CRUD =====

  /**
   * Liste les taches d'un chantier (TAC-01)
   */
  async listByChantier(chantierId: number, params: TacheListParams = {}): Promise<TacheListResponse> {
    const response = await api.get(`/api/taches/chantier/${chantierId}`, {
      params: {
        page: params.page || 1,
        size: params.size || 50,
        query: params.query,
        statut: params.statut,
        include_sous_taches: params.include_sous_taches ?? true,
      },
    })
    return response.data
  },

  /**
   * Obtient une tache par ID
   */
  async getById(tacheId: number, includeSousTaches = true): Promise<Tache> {
    const response = await api.get(`/api/taches/${tacheId}`, {
      params: { include_sous_taches: includeSousTaches },
    })
    return response.data
  },

  /**
   * Cree une nouvelle tache (TAC-06, TAC-07)
   */
  async create(data: TacheCreate): Promise<Tache> {
    const response = await api.post('/api/taches', data)
    return response.data
  },

  /**
   * Met a jour une tache
   */
  async update(tacheId: number, data: TacheUpdate): Promise<Tache> {
    const response = await api.put(`/api/taches/${tacheId}`, data)
    return response.data
  },

  /**
   * Supprime une tache
   */
  async delete(tacheId: number): Promise<void> {
    await api.delete(`/api/taches/${tacheId}`)
  },

  /**
   * Marque une tache comme terminee ou la rouvre (TAC-13)
   */
  async complete(tacheId: number, terminer = true): Promise<Tache> {
    const response = await api.post(`/api/taches/${tacheId}/complete`, { terminer })
    return response.data
  },

  /**
   * Reordonne les taches (TAC-15 - drag & drop)
   */
  async reorder(ordres: { tache_id: number; ordre: number }[]): Promise<Tache[]> {
    const response = await api.post('/api/taches/reorder', ordres)
    return response.data
  },

  /**
   * Obtient les statistiques des taches d'un chantier (TAC-20)
   */
  async getStats(chantierId: number): Promise<TacheStats> {
    const response = await api.get(`/api/taches/chantier/${chantierId}/stats`)
    return response.data
  },

  // ===== Templates (TAC-04, TAC-05) =====

  /**
   * Liste les templates de taches
   */
  async listTemplates(params: {
    page?: number
    size?: number
    query?: string
    categorie?: string
    active_only?: boolean
  } = {}): Promise<TemplateListResponse> {
    const response = await api.get('/api/templates-taches', {
      params: {
        page: params.page || 1,
        size: params.size || 50,
        query: params.query,
        categorie: params.categorie,
        active_only: params.active_only ?? true,
      },
    })
    return response.data
  },

  /**
   * Cree un nouveau template (TAC-04)
   */
  async createTemplate(data: TemplateCreate): Promise<TemplateModele> {
    const response = await api.post('/api/templates-taches', data)
    return response.data
  },

  /**
   * Importe un template dans un chantier (TAC-05)
   */
  async importTemplate(templateId: number, chantierId: number): Promise<Tache[]> {
    const response = await api.post('/api/templates-taches/import', {
      template_id: templateId,
      chantier_id: chantierId,
    })
    return response.data
  },

  // ===== Feuilles de taches (TAC-18, TAC-19) =====

  /**
   * Liste les feuilles de taches d'une tache
   */
  async listFeuillesByTache(
    tacheId: number,
    params: { page?: number; size?: number } = {}
  ): Promise<FeuilleTacheListResponse> {
    const response = await api.get(`/api/feuilles-taches/tache/${tacheId}`, {
      params: { page: params.page || 1, size: params.size || 50 },
    })
    return response.data
  },

  /**
   * Liste les feuilles en attente de validation (TAC-19)
   */
  async listFeuillesEnAttente(
    chantierId?: number,
    params: { page?: number; size?: number } = {}
  ): Promise<FeuilleTacheListResponse> {
    const response = await api.get('/api/feuilles-taches/en-attente', {
      params: {
        chantier_id: chantierId,
        page: params.page || 1,
        size: params.size || 50,
      },
    })
    return response.data
  },

  /**
   * Cree une feuille de tache (TAC-18)
   */
  async createFeuille(data: FeuilleTacheCreate): Promise<FeuilleTache> {
    const response = await api.post('/api/feuilles-taches', data)
    return response.data
  },

  /**
   * Valide ou rejette une feuille de tache (TAC-19)
   */
  async validateFeuille(
    feuilleId: number,
    valider: boolean,
    motifRejet?: string
  ): Promise<FeuilleTache> {
    const response = await api.post(`/api/feuilles-taches/${feuilleId}/validate`, {
      valider,
      motif_rejet: motifRejet,
    })
    return response.data
  },

  // ===== Export PDF (TAC-16) =====

  /**
   * Genere un export PDF des taches d'un chantier
   */
  async exportPDF(chantierId: number): Promise<Blob> {
    const response = await api.get(`/api/taches/chantier/${chantierId}/export-pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * Telecharge le PDF genere
   */
  downloadPDF(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}

export default tachesService
