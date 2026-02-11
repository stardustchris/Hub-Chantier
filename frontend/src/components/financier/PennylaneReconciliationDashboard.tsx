/**
 * PennylaneReconciliationDashboard - Dashboard de reconciliation Pennylane
 * Module 18.12 - CONN-15
 *
 * Affiche :
 * - Statistiques de reconciliation (matches, en attente, rejetes)
 * - Informations de derniere sync
 * - Liste des reconciliations en attente avec actions
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Clock,
  FileText,
  Building2,
  ArrowRight,
  Search,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { pennylaneService } from '../../services/pennylane'
import { logger } from '../../services/logger'
import type {
  PennylanePendingReconciliation,
  PennylaneDashboard,
  PennylaneReconciliationStatus,
  ReconciliationAction,
} from '../../types/pennylane'
import { RECONCILIATION_STATUS_CONFIG } from '../../types/pennylane'
import { formatEUR } from '../../utils/format'

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatRelativeTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'A l\'instant'
  if (diffMins < 60) return `Il y a ${diffMins} min`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `Il y a ${diffHours}h`
  const diffDays = Math.floor(diffHours / 24)
  return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`
}

interface ReconciliationCardProps {
  reconciliation: PennylanePendingReconciliation
  onResolve: (id: number, action: ReconciliationAction, achatId?: number) => Promise<void>
  isLoading: boolean
}

function ReconciliationCard({ reconciliation, onResolve, isLoading }: ReconciliationCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [searchAchat, setSearchAchat] = useState('')
  const [showReassign, setShowReassign] = useState(false)
  const [searchResults, setSearchResults] = useState<Array<{
    id: number
    libelle: string
    montant_ht: number
    fournisseur_nom: string
    chantier_nom: string
  }>>([])
  const [searching, setSearching] = useState(false)

  const ecartPct = reconciliation.suggested_achat
    ? ((reconciliation.amount_ht - reconciliation.suggested_achat.montant_ht_prevu) /
        reconciliation.suggested_achat.montant_ht_prevu) * 100
    : 0

  const handleSearch = async () => {
    if (!searchAchat.trim()) return
    try {
      setSearching(true)
      const results = await pennylaneService.searchAchatsForReassign(searchAchat)
      setSearchResults(results)
    } catch (err) {
      logger.error('Erreur recherche achats', err, { context: 'ReconciliationCard' })
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg bg-white overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-blue-600" />
          <div>
            <p className="font-medium text-gray-900">
              {reconciliation.supplier_name} #{reconciliation.pennylane_invoice_id.slice(-8)}
            </p>
            <p className="text-sm text-gray-500">
              {reconciliation.code_analytique && (
                <span className="inline-flex items-center gap-1 mr-2">
                  <Building2 size={12} />
                  {reconciliation.code_analytique}
                </span>
              )}
              <span>{formatDate(reconciliation.invoice_date)}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold text-gray-900">{formatEUR(reconciliation.amount_ht)}</span>
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          {/* Suggested match */}
          {reconciliation.suggested_achat && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={16} className="text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Match suggere</span>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    Achat #{reconciliation.suggested_achat.id} - {reconciliation.suggested_achat.libelle}
                  </p>
                  <p className="text-sm text-gray-600">
                    {reconciliation.suggested_achat.fournisseur_nom} | {reconciliation.suggested_achat.chantier_nom}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    Previsionnel: {formatEUR(reconciliation.suggested_achat.montant_ht_prevu)}
                  </p>
                  <p className={`text-sm font-medium ${
                    Math.abs(ecartPct) <= 5 ? 'text-green-600' :
                    Math.abs(ecartPct) <= 10 ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    Ecart: {ecartPct > 0 ? '+' : ''}{ecartPct.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* No match found */}
          {!reconciliation.suggested_achat && (
            <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className="text-orange-600" />
                <span className="text-sm font-medium text-orange-800">
                  Aucun achat previsionnel correspondant trouve
                </span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-2">
            {reconciliation.suggested_achat && (
              <button
                onClick={() => onResolve(reconciliation.id, 'validate', reconciliation.suggested_achat?.id)}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                <CheckCircle size={16} />
                Valider le match
              </button>
            )}

            <button
              onClick={() => setShowReassign(!showReassign)}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <ArrowRight size={16} />
              Reaffecter
            </button>

            <button
              onClick={() => onResolve(reconciliation.id, 'reject')}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50 transition-colors"
            >
              <XCircle size={16} />
              Rejeter
            </button>
          </div>

          {/* Reassign search */}
          {showReassign && (
            <div className="mt-4 p-3 border border-gray-200 rounded-lg bg-white">
              <p className="text-sm font-medium text-gray-700 mb-2">Rechercher un achat a affecter</p>
              <div className="flex gap-2 mb-3">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={searchAchat}
                    onChange={(e) => setSearchAchat(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Libelle, fournisseur, chantier..."
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={searching || !searchAchat.trim()}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 text-sm"
                >
                  {searching ? <Loader2 size={16} className="animate-spin" /> : 'Rechercher'}
                </button>
              </div>

              {searchResults.length > 0 && (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {searchResults.map((achat) => (
                    <div
                      key={achat.id}
                      className="flex items-center justify-between p-2 border border-gray-200 rounded hover:bg-blue-50 cursor-pointer transition-colors"
                      onClick={() => onResolve(reconciliation.id, 'reassign', achat.id)}
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-900">{achat.libelle}</p>
                        <p className="text-xs text-gray-500">
                          {achat.fournisseur_nom} | {achat.chantier_nom}
                        </p>
                      </div>
                      <span className="text-sm font-medium">{formatEUR(achat.montant_ht)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface PennylaneReconciliationDashboardProps {
  onSyncTriggered?: () => void
}

export default function PennylaneReconciliationDashboard({ onSyncTriggered }: PennylaneReconciliationDashboardProps) {
  const [dashboard, setDashboard] = useState<PennylaneDashboard | null>(null)
  const [reconciliations, setReconciliations] = useState<PennylanePendingReconciliation[]>([])
  const [statusFilter, setStatusFilter] = useState<PennylaneReconciliationStatus | ''>('')
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [resolving, setResolving] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [dashboardData, reconciliationsData] = await Promise.all([
        pennylaneService.getDashboard(),
        pennylaneService.getPendingReconciliations(statusFilter || undefined),
      ])

      setDashboard(dashboardData)
      setReconciliations(reconciliationsData)
    } catch (err) {
      setError('Erreur lors du chargement des donnees')
      logger.error('Erreur chargement dashboard Pennylane', err, { context: 'PennylaneReconciliationDashboard' })
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSync = async () => {
    try {
      setSyncing(true)
      await pennylaneService.triggerSync(['supplier_invoices'])
      await loadData()
      onSyncTriggered?.()
    } catch (err) {
      setError('Erreur lors de la synchronisation')
      logger.error('Erreur sync Pennylane', err, { context: 'PennylaneReconciliationDashboard' })
    } finally {
      setSyncing(false)
    }
  }

  const handleResolve = async (id: number, action: ReconciliationAction, achatId?: number) => {
    try {
      setResolving(id)
      await pennylaneService.resolveReconciliation(id, action, achatId)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la resolution')
      logger.error('Erreur resolution reconciliation', err, { context: 'PennylaneReconciliationDashboard' })
    } finally {
      setResolving(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        <p>{error}</p>
        <button onClick={loadData} className="text-sm underline mt-1">
          Reessayer
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with sync button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Reconciliation Pennylane</h2>
          {dashboard?.last_sync && (
            <p className="text-sm text-gray-500">
              Derniere sync: {formatRelativeTime(dashboard.last_sync.completed_at || dashboard.last_sync.started_at)}
              {dashboard.last_sync.status === 'success' && (
                <span className="ml-2 text-green-600">
                  ({dashboard.last_sync.records_processed} traites)
                </span>
              )}
            </p>
          )}
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={16} className={syncing ? 'animate-spin' : ''} />
          {syncing ? 'Synchronisation...' : 'Sync manuelle'}
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-700">{dashboard?.validated_today || 0}</p>
              <p className="text-sm text-green-600">Valides aujourd'hui</p>
            </div>
          </div>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-700">{dashboard?.pending_count || 0}</p>
              <p className="text-sm text-orange-600">A verifier</p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-700">{dashboard?.rejected_today || 0}</p>
              <p className="text-sm text-red-600">Rejetes aujourd'hui</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500">Filtrer par statut:</span>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as PennylaneReconciliationStatus | '')}
          className="text-sm px-3 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tous</option>
          {Object.entries(RECONCILIATION_STATUS_CONFIG).map(([key, config]) => (
            <option key={key} value={key}>{config.label}</option>
          ))}
        </select>
      </div>

      {/* Reconciliations list */}
      <div className="space-y-3">
        {reconciliations.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto text-green-300 mb-3" />
            <p className="font-medium">Aucune reconciliation en attente</p>
            <p className="text-sm">Toutes les factures ont ete traitees</p>
          </div>
        ) : (
          reconciliations.map((reconciliation) => (
            <ReconciliationCard
              key={reconciliation.id}
              reconciliation={reconciliation}
              onResolve={handleResolve}
              isLoading={resolving === reconciliation.id}
            />
          ))
        )}
      </div>
    </div>
  )
}
