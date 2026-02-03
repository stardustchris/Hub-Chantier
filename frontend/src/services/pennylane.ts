/**
 * Service API pour l'integration Pennylane Inbound
 * Module 18.12 - Import donnees comptables
 */

import api from './api'
import type {
  PennylaneSyncResult,
  PennylanePendingReconciliation,
  PennylaneMapping,
  PennylaneMappingCreate,
  PennylaneDashboard,
  ReconciliationAction,
  PennylaneReconciliationStatus,
  PennylaneSyncType,
} from '../types/pennylane'

const BASE = '/api/financier/pennylane'

export const pennylaneService = {
  // ===== Dashboard =====

  /**
   * Recupere les donnees du dashboard Pennylane
   */
  async getDashboard(): Promise<PennylaneDashboard> {
    const response = await api.get<PennylaneDashboard>(`${BASE}/dashboard`)
    return response.data
  },

  // ===== Synchronisation =====

  /**
   * Declenche une synchronisation manuelle avec Pennylane
   * @param syncTypes Types de synchronisation a effectuer
   */
  async triggerSync(syncTypes: PennylaneSyncType[]): Promise<PennylaneSyncResult> {
    const response = await api.post<PennylaneSyncResult>(`${BASE}/sync`, {
      sync_types: syncTypes,
    })
    return response.data
  },

  /**
   * Recupere l'historique des synchronisations
   * @param limit Nombre maximum de resultats
   */
  async getSyncHistory(limit = 20): Promise<PennylaneSyncResult[]> {
    const response = await api.get<{ items: PennylaneSyncResult[]; total: number }>(
      `${BASE}/sync-history`,
      { params: { limit } }
    )
    return response.data.items
  },

  // ===== Reconciliation =====

  /**
   * Recupere les reconciliations en attente
   * @param status Filtre par statut (optionnel)
   */
  async getPendingReconciliations(
    status?: PennylaneReconciliationStatus
  ): Promise<PennylanePendingReconciliation[]> {
    const response = await api.get<{ items: PennylanePendingReconciliation[]; total: number }>(
      `${BASE}/pending`,
      { params: status ? { status } : undefined }
    )
    return response.data.items
  },

  /**
   * Recupere le compte des reconciliations par statut
   */
  async getReconciliationCounts(): Promise<Record<PennylaneReconciliationStatus, number>> {
    const response = await api.get<Record<PennylaneReconciliationStatus, number>>(
      `${BASE}/pending/counts`
    )
    return response.data
  },

  /**
   * Resoud une reconciliation (valider, rejeter ou reaffecter)
   * @param id ID de la reconciliation
   * @param action Action a effectuer
   * @param achatId ID de l'achat cible (pour reaffectation)
   */
  async resolveReconciliation(
    id: number,
    action: ReconciliationAction,
    achatId?: number
  ): Promise<PennylanePendingReconciliation> {
    const response = await api.post<PennylanePendingReconciliation>(
      `${BASE}/reconcile/${id}`,
      { action, achat_id: achatId }
    )
    return response.data
  },

  // ===== Mappings Analytiques =====

  /**
   * Recupere la liste des mappings codes analytiques -> chantiers
   */
  async getMappings(): Promise<PennylaneMapping[]> {
    const response = await api.get<{ items: PennylaneMapping[]; total: number }>(
      `${BASE}/mappings`
    )
    return response.data.items
  },

  /**
   * Cree un nouveau mapping code analytique -> chantier
   * @param data Donnees du mapping
   */
  async createMapping(data: PennylaneMappingCreate): Promise<PennylaneMapping> {
    const response = await api.post<PennylaneMapping>(`${BASE}/mappings`, data)
    return response.data
  },

  /**
   * Supprime un mapping
   * @param id ID du mapping
   */
  async deleteMapping(id: number): Promise<void> {
    await api.delete(`${BASE}/mappings/${id}`)
  },

  // ===== Recherche Achats =====

  /**
   * Recherche des achats candidats pour reassignation
   * @param query Terme de recherche
   * @param chantierId Filtre par chantier (optionnel)
   */
  async searchAchatsForReassign(
    query: string,
    chantierId?: number
  ): Promise<Array<{ id: number; libelle: string; montant_ht: number; fournisseur_nom: string; chantier_nom: string }>> {
    const response = await api.get<{ items: Array<{ id: number; libelle: string; montant_ht: number; fournisseur_nom: string; chantier_nom: string }> }>(
      `${BASE}/search-achats`,
      { params: { q: query, chantier_id: chantierId } }
    )
    return response.data.items
  },
}
