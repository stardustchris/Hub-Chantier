import api from './api'
import type {
  Fournisseur,
  FournisseurCreate,
  FournisseurUpdate,
  Budget,
  BudgetCreate,
  BudgetUpdate,
  LotBudgetaire,
  LotBudgetaireCreate,
  LotBudgetaireUpdate,
  Achat,
  AchatCreate,
  AchatUpdate,
  DashboardFinancier,
  JournalFinancierEntry,
} from '../types'

const BASE = '/api/financier'

export const financierService = {
  // ===== Fournisseurs (FIN-14) =====
  async listFournisseurs(params?: {
    type?: string
    actif_seulement?: boolean
    limit?: number
    offset?: number
  }): Promise<{ items: Fournisseur[]; total: number }> {
    const response = await api.get<{ items: Fournisseur[]; total: number }>(
      `${BASE}/fournisseurs`,
      { params }
    )
    return response.data
  },

  async getFournisseur(id: number): Promise<Fournisseur> {
    const response = await api.get<Fournisseur>(`${BASE}/fournisseurs/${id}`)
    return response.data
  },

  async createFournisseur(data: FournisseurCreate): Promise<Fournisseur> {
    const response = await api.post<Fournisseur>(`${BASE}/fournisseurs`, data)
    return response.data
  },

  async updateFournisseur(id: number, data: FournisseurUpdate): Promise<Fournisseur> {
    const response = await api.put<Fournisseur>(`${BASE}/fournisseurs/${id}`, data)
    return response.data
  },

  async deleteFournisseur(id: number): Promise<void> {
    await api.delete(`${BASE}/fournisseurs/${id}`)
  },

  // ===== Budgets (FIN-01) =====
  async getBudgetByChantier(chantierId: number): Promise<Budget | null> {
    try {
      const response = await api.get<Budget>(`${BASE}/chantiers/${chantierId}/budget`)
      return response.data
    } catch (error: unknown) {
      const err = error as { response?: { status?: number } }
      if (err.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  async createBudget(data: BudgetCreate): Promise<Budget> {
    const response = await api.post<Budget>(`${BASE}/budgets`, data)
    return response.data
  },

  async updateBudget(id: number, data: BudgetUpdate): Promise<Budget> {
    const response = await api.put<Budget>(`${BASE}/budgets/${id}`, data)
    return response.data
  },

  // ===== Lots budgetaires (FIN-02) =====
  async listLots(budgetId: number): Promise<LotBudgetaire[]> {
    const response = await api.get<{ items: LotBudgetaire[]; total: number }>(`${BASE}/budgets/${budgetId}/lots`)
    return response.data.items
  },

  async createLot(data: LotBudgetaireCreate): Promise<LotBudgetaire> {
    const response = await api.post<LotBudgetaire>(`${BASE}/lots-budgetaires`, data)
    return response.data
  },

  async updateLot(id: number, data: LotBudgetaireUpdate): Promise<LotBudgetaire> {
    const response = await api.put<LotBudgetaire>(`${BASE}/lots-budgetaires/${id}`, data)
    return response.data
  },

  async deleteLot(id: number): Promise<void> {
    await api.delete(`${BASE}/lots-budgetaires/${id}`)
  },

  // ===== Achats (FIN-05, FIN-06) =====
  async listAchats(params?: {
    chantier_id?: number
    statut?: string
    limit?: number
    offset?: number
  }): Promise<{ items: Achat[]; total: number }> {
    const response = await api.get<{ items: Achat[]; total: number }>(
      `${BASE}/achats`,
      { params }
    )
    return response.data
  },

  async listAchatsEnAttente(): Promise<Achat[]> {
    const response = await api.get<{ items: Achat[]; total: number }>(`${BASE}/achats/en-attente`)
    return response.data.items
  },

  async getAchat(id: number): Promise<Achat> {
    const response = await api.get<Achat>(`${BASE}/achats/${id}`)
    return response.data
  },

  async createAchat(data: AchatCreate): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats`, data)
    return response.data
  },

  async updateAchat(id: number, data: AchatUpdate): Promise<Achat> {
    const response = await api.put<Achat>(`${BASE}/achats/${id}`, data)
    return response.data
  },

  async validerAchat(id: number): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats/${id}/valider`)
    return response.data
  },

  async refuserAchat(id: number, motif: string): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats/${id}/refuser`, { motif })
    return response.data
  },

  async commanderAchat(id: number): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats/${id}/commander`)
    return response.data
  },

  async livrerAchat(id: number): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats/${id}/livrer`)
    return response.data
  },

  async facturerAchat(id: number, numero_facture: string): Promise<Achat> {
    const response = await api.post<Achat>(`${BASE}/achats/${id}/facturer`, { numero_facture })
    return response.data
  },

  // ===== Dashboard (FIN-11) =====
  async getDashboardFinancier(chantierId: number): Promise<DashboardFinancier> {
    const response = await api.get<DashboardFinancier>(
      `${BASE}/chantiers/${chantierId}/dashboard-financier`
    )
    return response.data
  },

  // ===== Journal (FIN-15) =====
  async listJournal(params?: {
    entite_type?: string
    entite_id?: number
    limit?: number
    offset?: number
  }): Promise<{ items: JournalFinancierEntry[]; total: number }> {
    const response = await api.get<{ items: JournalFinancierEntry[]; total: number }>(
      `${BASE}/journal-financier`,
      { params }
    )
    return response.data
  },
}
