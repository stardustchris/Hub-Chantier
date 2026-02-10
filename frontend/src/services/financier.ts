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
  EvolutionFinanciere,
  JournalFinancierEntry,
  AvenantBudgetaire,
  AvenantCreate,
  AvenantUpdate,
  SituationTravaux,
  SituationCreate,
  SituationUpdate,
  FactureClient,
  FactureFromSituationCreate,
  FactureAcompteCreate,
  CoutMainOeuvreSummary,
  CoutMaterielSummary,
  AlerteDepassement,
  VueConsolidee,
  SuggestionsFinancieres,
  AffectationBudgetTache,
  AffectationBudgetTacheCreate,
  AnalyseIAConsolidee,
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

  async appliquerTemplateGO(budgetId: number): Promise<LotBudgetaire[]> {
    const response = await api.post<LotBudgetaire[]>(`${BASE}/budgets/${budgetId}/template-go`)
    return response.data
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

  // ===== Evolution financiere (FIN-17) =====
  async getEvolutionFinanciere(chantierId: number): Promise<EvolutionFinanciere> {
    const response = await api.get<EvolutionFinanciere>(
      `${BASE}/chantiers/${chantierId}/evolution-financiere`
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

  // ===== Avenants (FIN-04) =====
  async listAvenants(budgetId: number): Promise<AvenantBudgetaire[]> {
    const response = await api.get<{ items: AvenantBudgetaire[]; total: number }>(
      `${BASE}/budgets/${budgetId}/avenants`
    )
    return response.data.items
  },

  async createAvenant(data: AvenantCreate): Promise<AvenantBudgetaire> {
    const response = await api.post<AvenantBudgetaire>(`${BASE}/avenants`, data)
    return response.data
  },

  async updateAvenant(id: number, data: AvenantUpdate): Promise<AvenantBudgetaire> {
    const response = await api.put<AvenantBudgetaire>(`${BASE}/avenants/${id}`, data)
    return response.data
  },

  async validerAvenant(id: number): Promise<AvenantBudgetaire> {
    const response = await api.post<AvenantBudgetaire>(`${BASE}/avenants/${id}/valider`)
    return response.data
  },

  async deleteAvenant(id: number): Promise<void> {
    await api.delete(`${BASE}/avenants/${id}`)
  },

  // ===== Situations (FIN-07) =====
  async listSituations(chantierId: number): Promise<SituationTravaux[]> {
    const response = await api.get<{ items: SituationTravaux[]; total: number }>(
      `${BASE}/chantiers/${chantierId}/situations`
    )
    return response.data.items
  },

  async getSituation(id: number): Promise<SituationTravaux> {
    const response = await api.get<SituationTravaux>(`${BASE}/situations/${id}`)
    return response.data
  },

  async createSituation(data: SituationCreate): Promise<SituationTravaux> {
    const response = await api.post<SituationTravaux>(`${BASE}/situations`, data)
    return response.data
  },

  async updateSituation(id: number, data: SituationUpdate): Promise<SituationTravaux> {
    const response = await api.put<SituationTravaux>(`${BASE}/situations/${id}`, data)
    return response.data
  },

  async soumettreSituation(id: number): Promise<SituationTravaux> {
    const response = await api.post<SituationTravaux>(`${BASE}/situations/${id}/soumettre`)
    return response.data
  },

  async validerSituation(id: number): Promise<SituationTravaux> {
    const response = await api.post<SituationTravaux>(`${BASE}/situations/${id}/valider`)
    return response.data
  },

  async validerClientSituation(id: number): Promise<SituationTravaux> {
    const response = await api.post<SituationTravaux>(`${BASE}/situations/${id}/valider-client`)
    return response.data
  },

  async deleteSituation(id: number): Promise<void> {
    await api.delete(`${BASE}/situations/${id}`)
  },

  // ===== Factures (FIN-08) =====
  async listFactures(chantierId: number): Promise<FactureClient[]> {
    const response = await api.get<{ items: FactureClient[]; total: number }>(
      `${BASE}/chantiers/${chantierId}/factures`
    )
    return response.data.items
  },

  async getFacture(id: number): Promise<FactureClient> {
    const response = await api.get<FactureClient>(`${BASE}/factures/${id}`)
    return response.data
  },

  async createFactureFromSituation(data: FactureFromSituationCreate): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/from-situation`, data)
    return response.data
  },

  async createFactureAcompte(data: FactureAcompteCreate): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/acompte`, data)
    return response.data
  },

  async emettreFacture(id: number): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/${id}/emettre`)
    return response.data
  },

  async envoyerFacture(id: number): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/${id}/envoyer`)
    return response.data
  },

  async payerFacture(id: number): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/${id}/payer`)
    return response.data
  },

  async annulerFacture(id: number): Promise<FactureClient> {
    const response = await api.post<FactureClient>(`${BASE}/factures/${id}/annuler`)
    return response.data
  },

  // ===== Couts main-d'oeuvre (FIN-09) =====
  async getCoutsMainOeuvre(chantierId: number, params?: { date_debut?: string; date_fin?: string }): Promise<CoutMainOeuvreSummary> {
    const response = await api.get<CoutMainOeuvreSummary>(
      `${BASE}/chantiers/${chantierId}/couts-main-oeuvre`,
      { params }
    )
    return response.data
  },

  // ===== Couts materiel (FIN-10) =====
  async getCoutsMateriel(chantierId: number, params?: { date_debut?: string; date_fin?: string }): Promise<CoutMaterielSummary> {
    const response = await api.get<CoutMaterielSummary>(
      `${BASE}/chantiers/${chantierId}/couts-materiel`,
      { params }
    )
    return response.data
  },

  // ===== Alertes (FIN-12) =====
  async listAlertes(chantierId: number, nonAcquitteesSeulement?: boolean): Promise<AlerteDepassement[]> {
    const response = await api.get<{ items: AlerteDepassement[]; total: number }>(
      `${BASE}/chantiers/${chantierId}/alertes`,
      { params: { non_acquittees_seulement: nonAcquitteesSeulement } }
    )
    return response.data.items
  },

  async verifierDepassement(chantierId: number): Promise<AlerteDepassement | null> {
    try {
      const response = await api.post<AlerteDepassement>(
        `${BASE}/chantiers/${chantierId}/alertes/verifier`
      )
      return response.data
    } catch (error: unknown) {
      const err = error as { response?: { status?: number } }
      if (err.response?.status === 200) return null
      throw error
    }
  },

  async acquitterAlerte(id: number): Promise<AlerteDepassement> {
    const response = await api.post<AlerteDepassement>(`${BASE}/alertes/${id}/acquitter`)
    return response.data
  },

  // ===== Vue consolidee multi-chantiers (FIN-20) =====
  async getConsolidation(chantierIds: number[]): Promise<VueConsolidee> {
    const ids = chantierIds.join(',')
    const response = await api.get<VueConsolidee>(
      `${BASE}/finances/consolidation`,
      { params: { chantier_ids: ids } }
    )
    return response.data
  },

  // ===== Analyse IA consolidée multi-chantiers (Gemini 3 Flash) =====
  async getAnalyseIAConsolidee(chantierIds: number[]): Promise<AnalyseIAConsolidee> {
    const ids = chantierIds.join(',')
    const response = await api.get<AnalyseIAConsolidee>(
      `${BASE}/finances/consolidation/ia`,
      { params: { chantier_ids: ids } }
    )
    return response.data
  },

  // ===== Suggestions IA (FIN-21) =====
  async getSuggestions(chantierId: number): Promise<SuggestionsFinancieres> {
    const response = await api.get<SuggestionsFinancieres>(
      `${BASE}/chantiers/${chantierId}/suggestions`
    )
    return response.data
  },

  // ===== Affectations budget-tache (FIN-03) =====
  async getAffectationsByChantier(chantierId: number): Promise<AffectationBudgetTache[]> {
    const response = await api.get<{ items: AffectationBudgetTache[]; total: number }>(
      `${BASE}/chantiers/${chantierId}/affectations`
    )
    return response.data.items
  },

  async getAffectationsByTache(tacheId: number): Promise<AffectationBudgetTache[]> {
    const response = await api.get<{ items: AffectationBudgetTache[]; total: number }>(
      `${BASE}/taches/${tacheId}/affectations`
    )
    return response.data.items
  },

  async createAffectation(lotId: number, data: AffectationBudgetTacheCreate): Promise<AffectationBudgetTache> {
    const response = await api.post<AffectationBudgetTache>(
      `${BASE}/lots-budgetaires/${lotId}/affectations`,
      data
    )
    return response.data
  },

  async deleteAffectation(affectationId: number): Promise<void> {
    await api.delete(`${BASE}/affectations/${affectationId}`)
  },

  // ===== Export comptable (FIN-13) =====
  async exportComptable(chantierId: number, format: 'csv' | 'xlsx'): Promise<Blob> {
    const response = await api.get(
      `${BASE}/chantiers/${chantierId}/export-comptable`,
      {
        params: { format },
        responseType: 'blob',
      }
    )
    return response.data as Blob
  },
}
