/**
 * Types TypeScript pour l'integration Pennylane Inbound
 * Module 18.12 - Import donnees comptables
 */

// ===== Synchronisation =====

export type PennylaneSyncStatus = 'running' | 'success' | 'failed'
export type PennylaneSyncType = 'supplier_invoices' | 'customer_payments' | 'suppliers' | 'full'

export interface PennylaneSyncResult {
  id?: number
  sync_type: PennylaneSyncType | string
  started_at: string
  completed_at?: string
  records_processed: number
  records_created: number
  records_updated: number
  records_pending: number
  status: PennylaneSyncStatus
  error_message?: string
}

// ===== Reconciliation =====

export type PennylaneReconciliationStatus = 'pending' | 'validated' | 'rejected' | 'reassigned'

export interface SuggestedAchat {
  id: number
  libelle: string
  montant_ht_prevu: number
  fournisseur_nom: string
  chantier_nom: string
}

export interface PennylanePendingReconciliation {
  id: number
  pennylane_invoice_id: string
  supplier_name: string
  supplier_siret?: string
  amount_ht: number
  code_analytique?: string
  invoice_date: string
  suggested_achat_id?: number
  suggested_achat?: SuggestedAchat
  status: PennylaneReconciliationStatus
  resolved_by?: number
  resolved_at?: string
  created_at: string
}

export type ReconciliationAction = 'validate' | 'reject' | 'reassign'

export interface ReconciliationResolveRequest {
  action: ReconciliationAction
  achat_id?: number
}

// ===== Mappings Analytiques =====

export interface PennylaneMapping {
  id: number
  code_analytique: string
  chantier_id: number
  chantier_nom: string
  created_at: string
  created_by?: number
}

export interface PennylaneMappingCreate {
  code_analytique: string
  chantier_id: number
}

// ===== Dashboard =====

export interface PennylaneDashboard {
  last_sync?: PennylaneSyncResult
  pending_count: number
  validated_today: number
  rejected_today: number
  sync_enabled: boolean
  next_sync_at?: string
}

// ===== Configuration des statuts =====

export const RECONCILIATION_STATUS_CONFIG: Record<PennylaneReconciliationStatus, { label: string; color: string; bgColor: string }> = {
  pending: { label: 'En attente', color: '#F59E0B', bgColor: '#FEF3C7' },
  validated: { label: 'Valide', color: '#10B981', bgColor: '#D1FAE5' },
  rejected: { label: 'Rejete', color: '#EF4444', bgColor: '#FEE2E2' },
  reassigned: { label: 'Reaffecte', color: '#3B82F6', bgColor: '#DBEAFE' },
}

export const SYNC_STATUS_CONFIG: Record<PennylaneSyncStatus, { label: string; color: string; bgColor: string }> = {
  running: { label: 'En cours', color: '#3B82F6', bgColor: '#DBEAFE' },
  success: { label: 'Succes', color: '#10B981', bgColor: '#D1FAE5' },
  failed: { label: 'Echec', color: '#EF4444', bgColor: '#FEE2E2' },
}

export const SYNC_TYPE_LABELS: Record<PennylaneSyncType, string> = {
  supplier_invoices: 'Factures fournisseurs',
  customer_payments: 'Encaissements clients',
  suppliers: 'Fournisseurs',
  full: 'Synchronisation complete',
}
