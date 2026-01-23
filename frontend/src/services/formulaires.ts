/**
 * Service API pour le module Formulaires - CDC Section 8 (FOR-01 à FOR-11)
 */

import api from './api'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  FormulaireRempli,
  FormulaireCreate,
  FormulaireUpdate,
  FormulaireHistorique,
  CategorieFormulaire,
  StatutFormulaire,
} from '../types'

// ===== INTERFACES DE REPONSE =====

interface TemplatesListResponse {
  templates: TemplateFormulaire[]
  total: number
  skip: number
  limit: number
}

interface FormulairesListResponse {
  formulaires: FormulaireRempli[]
  total: number
  skip: number
  limit: number
}

interface HistoryResponse {
  formulaire_id: number
  versions: FormulaireHistorique[]
}

interface ExportPDFResponse {
  formulaire_id: number
  filename: string
  content_type: string
  content_base64: string
}

// ===== PARAMETRES DE FILTRAGE =====

interface TemplateFilters {
  query?: string
  categorie?: CategorieFormulaire
  active_only?: boolean
  skip?: number
  limit?: number
}

interface FormulaireFilters {
  chantier_id?: number
  template_id?: number
  user_id?: number
  statut?: StatutFormulaire
  date_debut?: string
  date_fin?: string
  skip?: number
  limit?: number
}

// ===== SERVICE FORMULAIRES =====

export const formulairesService = {
  // ===== TEMPLATES (FOR-01) =====

  /**
   * Liste les templates de formulaire avec filtres optionnels
   */
  async listTemplates(filters: TemplateFilters = {}): Promise<TemplatesListResponse> {
    const params = new URLSearchParams()
    if (filters.query) params.append('query', filters.query)
    if (filters.categorie) params.append('categorie', filters.categorie)
    if (filters.active_only) params.append('active_only', 'true')
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await api.get(`/api/templates-formulaires?${params.toString()}`)
    return response.data
  },

  /**
   * Recupere un template par son ID
   */
  async getTemplate(id: number): Promise<TemplateFormulaire> {
    const response = await api.get(`/api/templates-formulaires/${id}`)
    return response.data
  },

  /**
   * Cree un nouveau template de formulaire
   */
  async createTemplate(data: TemplateFormulaireCreate): Promise<TemplateFormulaire> {
    const response = await api.post('/api/templates-formulaires', data)
    return response.data
  },

  /**
   * Met a jour un template existant
   */
  async updateTemplate(id: number, data: TemplateFormulaireUpdate): Promise<TemplateFormulaire> {
    const response = await api.put(`/api/templates-formulaires/${id}`, data)
    return response.data
  },

  /**
   * Supprime un template
   */
  async deleteTemplate(id: number): Promise<void> {
    await api.delete(`/api/templates-formulaires/${id}`)
  },

  // ===== FORMULAIRES REMPLIS (FOR-02 à FOR-11) =====

  /**
   * Liste les formulaires avec filtres
   */
  async listFormulaires(filters: FormulaireFilters = {}): Promise<FormulairesListResponse> {
    const params = new URLSearchParams()
    if (filters.chantier_id) params.append('chantier_id', filters.chantier_id.toString())
    if (filters.template_id) params.append('template_id', filters.template_id.toString())
    if (filters.user_id) params.append('user_id', filters.user_id.toString())
    if (filters.statut) params.append('statut', filters.statut)
    if (filters.date_debut) params.append('date_debut', filters.date_debut)
    if (filters.date_fin) params.append('date_fin', filters.date_fin)
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await api.get(`/api/formulaires?${params.toString()}`)
    return response.data
  },

  /**
   * Liste les formulaires d'un chantier specifique (FOR-10)
   */
  async listByChantier(chantierId: number, skip = 0, limit = 100): Promise<FormulairesListResponse> {
    const response = await api.get(`/api/formulaires/chantier/${chantierId}?skip=${skip}&limit=${limit}`)
    return response.data
  },

  /**
   * Recupere un formulaire par son ID
   */
  async getFormulaire(id: number): Promise<FormulaireRempli> {
    const response = await api.get(`/api/formulaires/${id}`)
    return response.data
  },

  /**
   * Cree un formulaire depuis un template (FOR-11)
   */
  async createFormulaire(data: FormulaireCreate): Promise<FormulaireRempli> {
    const response = await api.post('/api/formulaires', data)
    return response.data
  },

  /**
   * Met a jour les champs d'un formulaire (FOR-02)
   */
  async updateFormulaire(id: number, data: FormulaireUpdate): Promise<FormulaireRempli> {
    const response = await api.put(`/api/formulaires/${id}`, data)
    return response.data
  },

  // ===== PHOTOS (FOR-04) =====

  /**
   * Ajoute une photo horodatee au formulaire
   */
  async addPhoto(
    formulaireId: number,
    url: string,
    nomFichier: string,
    champNom: string,
    latitude?: number,
    longitude?: number
  ): Promise<FormulaireRempli> {
    const response = await api.post(`/api/formulaires/${formulaireId}/photos`, {
      url,
      nom_fichier: nomFichier,
      champ_nom: champNom,
      latitude,
      longitude,
    })
    return response.data
  },

  // ===== SIGNATURE (FOR-05) =====

  /**
   * Ajoute une signature electronique au formulaire
   */
  async addSignature(
    formulaireId: number,
    signatureUrl: string,
    signatureNom: string
  ): Promise<FormulaireRempli> {
    const response = await api.post(`/api/formulaires/${formulaireId}/signature`, {
      signature_url: signatureUrl,
      signature_nom: signatureNom,
    })
    return response.data
  },

  // ===== SOUMISSION ET VALIDATION (FOR-07) =====

  /**
   * Soumet un formulaire avec horodatage automatique
   */
  async submitFormulaire(
    formulaireId: number,
    signatureUrl?: string,
    signatureNom?: string
  ): Promise<FormulaireRempli> {
    const response = await api.post(`/api/formulaires/${formulaireId}/submit`, {
      signature_url: signatureUrl,
      signature_nom: signatureNom,
    })
    return response.data
  },

  /**
   * Valide un formulaire soumis
   */
  async validateFormulaire(formulaireId: number): Promise<FormulaireRempli> {
    const response = await api.post(`/api/formulaires/${formulaireId}/validate`)
    return response.data
  },

  // ===== HISTORIQUE (FOR-08) =====

  /**
   * Recupere l'historique des versions d'un formulaire
   */
  async getHistory(formulaireId: number): Promise<HistoryResponse> {
    const response = await api.get(`/api/formulaires/${formulaireId}/history`)
    return response.data
  },

  // ===== EXPORT PDF (FOR-09) =====

  /**
   * Exporte un formulaire en PDF
   */
  async exportPDF(formulaireId: number): Promise<ExportPDFResponse> {
    const response = await api.get(`/api/formulaires/${formulaireId}/export`)
    return response.data
  },

  /**
   * Telecharge le PDF d'un formulaire
   */
  async downloadPDF(formulaireId: number): Promise<void> {
    const exportData = await this.exportPDF(formulaireId)

    // Decoder le base64 et creer un blob avec gestion d'erreur
    let byteCharacters: string
    try {
      byteCharacters = atob(exportData.content_base64)
    } catch {
      throw new Error('Erreur lors du decodage du fichier PDF')
    }

    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    const blob = new Blob([byteArray], { type: exportData.content_type })

    // Creer un lien de telechargement
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = exportData.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}

export default formulairesService
