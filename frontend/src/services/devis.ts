import api from './api'
import type {
  Article,
  ArticleCreate,
  ArticleUpdate,
  Devis,
  DevisCreate,
  DevisUpdate,
  DevisDetail,
  LotDevis,
  LotDevisCreate,
  LotDevisUpdate,
  LigneDevis,
  LigneDevisCreate,
  LigneDevisUpdate,
  DebourseDetail,
  DebourseDetailCreate,
  JournalDevisEntry,
  DashboardDevis,
} from '../types'

const BASE = '/api/devis'

export const devisService = {
  // ===== Articles (DEV-01) =====
  async listArticles(params?: {
    categorie?: string
    type_debourse?: string
    actif_seulement?: boolean
    search?: string
    limit?: number
    offset?: number
  }): Promise<{ items: Article[]; total: number }> {
    const response = await api.get<{ items: Article[]; total: number }>(
      `${BASE}/articles`,
      { params }
    )
    return response.data
  },

  async getArticle(id: number): Promise<Article> {
    const response = await api.get<Article>(`${BASE}/articles/${id}`)
    return response.data
  },

  async createArticle(data: ArticleCreate): Promise<Article> {
    const response = await api.post<Article>(`${BASE}/articles`, data)
    return response.data
  },

  async updateArticle(id: number, data: ArticleUpdate): Promise<Article> {
    const response = await api.put<Article>(`${BASE}/articles/${id}`, data)
    return response.data
  },

  async deleteArticle(id: number): Promise<void> {
    await api.delete(`${BASE}/articles/${id}`)
  },

  // ===== Devis (DEV-03) =====
  async listDevis(params?: {
    statut?: string
    client_nom?: string
    date_debut?: string
    date_fin?: string
    montant_min?: number
    montant_max?: number
    search?: string
    sort_by?: string
    sort_direction?: string
    limit?: number
    offset?: number
  }): Promise<{ items: Devis[]; total: number }> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      `${BASE}/devis`,
      { params }
    )
    return response.data
  },

  async getDevis(id: number): Promise<DevisDetail> {
    const response = await api.get<DevisDetail>(`${BASE}/devis/${id}`)
    return response.data
  },

  async createDevis(data: DevisCreate): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis`, data)
    return response.data
  },

  async updateDevis(id: number, data: DevisUpdate): Promise<Devis> {
    const response = await api.put<Devis>(`${BASE}/devis/${id}`, data)
    return response.data
  },

  async deleteDevis(id: number): Promise<void> {
    await api.delete(`${BASE}/devis/${id}`)
  },

  // ===== Workflow (DEV-15) =====
  async soumettreDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/soumettre`)
    return response.data
  },

  async validerDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/valider`)
    return response.data
  },

  async envoyerDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/envoyer`)
    return response.data
  },

  async marquerVu(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/vu`)
    return response.data
  },

  async negocierDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/negocier`)
    return response.data
  },

  async accepterDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/accepter`)
    return response.data
  },

  async refuserDevis(id: number, motif?: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/refuser`, { motif })
    return response.data
  },

  async marquerPerdu(id: number, motif?: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/devis/${id}/perdu`, { motif })
    return response.data
  },

  // ===== Lots (DEV-03) =====
  async listLots(devisId: number): Promise<LotDevis[]> {
    const response = await api.get<{ items: LotDevis[]; total: number }>(
      `${BASE}/devis/${devisId}/lots`
    )
    return response.data.items
  },

  async createLot(data: LotDevisCreate): Promise<LotDevis> {
    const response = await api.post<LotDevis>(`${BASE}/lots`, data)
    return response.data
  },

  async updateLot(id: number, data: LotDevisUpdate): Promise<LotDevis> {
    const response = await api.put<LotDevis>(`${BASE}/lots/${id}`, data)
    return response.data
  },

  async deleteLot(id: number): Promise<void> {
    await api.delete(`${BASE}/lots/${id}`)
  },

  async reorderLots(devisId: number, lotIds: number[]): Promise<void> {
    await api.post(`${BASE}/devis/${devisId}/lots/reorder`, { lot_ids: lotIds })
  },

  // ===== Lignes (DEV-03) =====
  async createLigne(data: LigneDevisCreate): Promise<LigneDevis> {
    const response = await api.post<LigneDevis>(`${BASE}/lignes`, data)
    return response.data
  },

  async updateLigne(id: number, data: LigneDevisUpdate): Promise<LigneDevis> {
    const response = await api.put<LigneDevis>(`${BASE}/lignes/${id}`, data)
    return response.data
  },

  async deleteLigne(id: number): Promise<void> {
    await api.delete(`${BASE}/lignes/${id}`)
  },

  // ===== Debourses (DEV-05) =====
  async listDebourses(ligneId: number): Promise<DebourseDetail[]> {
    const response = await api.get<{ items: DebourseDetail[]; total: number }>(
      `${BASE}/lignes/${ligneId}/debourses`
    )
    return response.data.items
  },

  async createDebourse(data: DebourseDetailCreate): Promise<DebourseDetail> {
    const response = await api.post<DebourseDetail>(`${BASE}/debourses`, data)
    return response.data
  },

  async deleteDebourse(id: number): Promise<void> {
    await api.delete(`${BASE}/debourses/${id}`)
  },

  // ===== Dashboard (DEV-17) =====
  async getDashboard(): Promise<DashboardDevis> {
    const response = await api.get<DashboardDevis>(`${BASE}/dashboard`)
    return response.data
  },

  // ===== Journal (DEV-18) =====
  async listJournal(devisId: number, params?: {
    limit?: number
    offset?: number
  }): Promise<{ items: JournalDevisEntry[]; total: number }> {
    const response = await api.get<{ items: JournalDevisEntry[]; total: number }>(
      `${BASE}/devis/${devisId}/journal`,
      { params }
    )
    return response.data
  },

  // ===== Search (DEV-19) =====
  async searchDevis(query: string): Promise<Devis[]> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      `${BASE}/devis/search`,
      { params: { q: query } }
    )
    return response.data.items
  },
}
