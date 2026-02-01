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
  JournalDevisEntry,
  DashboardDevis,
} from '../types'

// Backend router: APIRouter(prefix="/devis") -> mounted at /api/devis
const BASE = '/api/devis'
// Articles have a separate router: APIRouter(prefix="/articles-devis")
const ARTICLES_BASE = '/api/articles-devis'

export const devisService = {
  // ===== Articles (DEV-01) =====
  async listArticles(params?: {
    categorie?: string
    search?: string
    actif?: boolean
    limit?: number
    offset?: number
  }): Promise<{ items: Article[]; total: number }> {
    const response = await api.get<{ items: Article[]; total: number }>(
      ARTICLES_BASE,
      { params }
    )
    return response.data
  },

  async getArticle(id: number): Promise<Article> {
    const response = await api.get<Article>(`${ARTICLES_BASE}/${id}`)
    return response.data
  },

  async createArticle(data: ArticleCreate): Promise<Article> {
    const response = await api.post<Article>(ARTICLES_BASE, data)
    return response.data
  },

  async updateArticle(id: number, data: ArticleUpdate): Promise<Article> {
    const response = await api.put<Article>(`${ARTICLES_BASE}/${id}`, data)
    return response.data
  },

  async deleteArticle(id: number): Promise<void> {
    await api.delete(`${ARTICLES_BASE}/${id}`)
  },

  // ===== Devis (DEV-03) =====
  async listDevis(params?: {
    statut?: string
    client_nom?: string
    date_min?: string
    date_max?: string
    montant_min?: number
    montant_max?: number
    search?: string
    commercial_id?: number
    limit?: number
    offset?: number
  }): Promise<{ items: Devis[]; total: number }> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      BASE,
      { params }
    )
    return response.data
  },

  async getDevis(id: number): Promise<DevisDetail> {
    const response = await api.get<DevisDetail>(`${BASE}/${id}`)
    return response.data
  },

  async createDevis(data: DevisCreate): Promise<Devis> {
    const response = await api.post<Devis>(BASE, data)
    return response.data
  },

  async updateDevis(id: number, data: DevisUpdate): Promise<Devis> {
    const response = await api.put<Devis>(`${BASE}/${id}`, data)
    return response.data
  },

  async deleteDevis(id: number): Promise<void> {
    await api.delete(`${BASE}/${id}`)
  },

  // ===== Workflow (DEV-15) =====
  async soumettreDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/soumettre`)
    return response.data
  },

  async validerDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/valider`)
    return response.data
  },

  async retournerBrouillon(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/retourner-brouillon`)
    return response.data
  },

  async accepterDevis(id: number): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/accepter`)
    return response.data
  },

  async refuserDevis(id: number, motif: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/refuser`, { motif })
    return response.data
  },

  async marquerPerdu(id: number, motif: string): Promise<Devis> {
    const response = await api.post<Devis>(`${BASE}/${id}/perdu`, { motif })
    return response.data
  },

  // ===== Calcul totaux (DEV-06) =====
  async calculerTotaux(id: number): Promise<Record<string, unknown>> {
    const response = await api.post<Record<string, unknown>>(`${BASE}/${id}/calculer`)
    return response.data
  },

  // ===== Lots (DEV-03) =====
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
      `${BASE}/${devisId}/journal`,
      { params }
    )
    return response.data
  },

  // ===== Search (DEV-19) =====
  async searchDevis(params?: {
    client_nom?: string
    statut?: string
    date_min?: string
    date_max?: string
    montant_min?: number
    montant_max?: number
    commercial_id?: number
    search?: string
    limit?: number
    offset?: number
  }): Promise<{ items: Devis[]; total: number }> {
    const response = await api.get<{ items: Devis[]; total: number }>(
      `${BASE}/search`,
      { params }
    )
    return response.data
  },
}
