/**
 * PennylaneSyncHistory - Historique des synchronisations Pennylane
 * Module 18.12 - CONN-10
 *
 * Affiche la liste des synchronisations passees avec :
 * - Date/heure
 * - Type de sync
 * - Statut (success/failed/running)
 * - Nombre de records traites
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  AlertCircle,
  Activity,
} from 'lucide-react'
import { pennylaneService } from '../../services/pennylane'
import { logger } from '../../services/logger'
import type { PennylaneSyncResult, PennylaneSyncType } from '../../types/pennylane'
import { SYNC_STATUS_CONFIG, SYNC_TYPE_LABELS } from '../../types/pennylane'

const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatDuration = (startStr: string, endStr?: string): string => {
  if (!endStr) return 'En cours...'
  const start = new Date(startStr)
  const end = new Date(endStr)
  const diffMs = end.getTime() - start.getTime()
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return `${diffSec}s`
  const diffMin = Math.floor(diffSec / 60)
  const remainingSec = diffSec % 60
  return `${diffMin}min ${remainingSec}s`
}

interface PennylaneSyncHistoryProps {
  refreshTrigger?: number
}

export default function PennylaneSyncHistory({ refreshTrigger }: PennylaneSyncHistoryProps) {
  const [history, setHistory] = useState<PennylaneSyncResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [syncing, setSyncing] = useState(false)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const historyData = await pennylaneService.getSyncHistory(50)
      setHistory(historyData)
    } catch (err) {
      setError('Erreur lors du chargement de l\'historique')
      logger.error('Erreur chargement historique Pennylane', err, { context: 'PennylaneSyncHistory' })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData, refreshTrigger])

  const handleSync = async (syncType: PennylaneSyncType) => {
    try {
      setSyncing(true)
      await pennylaneService.triggerSync([syncType])
      await loadData()
    } catch (err) {
      setError('Erreur lors de la synchronisation')
      logger.error('Erreur sync Pennylane', err, { context: 'PennylaneSyncHistory' })
    } finally {
      setSyncing(false)
    }
  }

  const getStatusIcon = (status: PennylaneSyncResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Historique des synchronisations</h2>
          <p className="text-sm text-gray-500">
            Consultez les dernieres synchronisations avec Pennylane
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Actualiser
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
          <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
          <div>
            <p>{error}</p>
            <button onClick={() => setError(null)} className="text-sm underline mt-1">
              Fermer
            </button>
          </div>
        </div>
      )}

      {/* Quick sync buttons */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <h3 className="font-medium text-blue-900 mb-3">Lancer une synchronisation</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleSync('supplier_invoices')}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 disabled:opacity-50 transition-colors"
          >
            <FileText size={16} />
            Factures fournisseurs
          </button>
          <button
            onClick={() => handleSync('customer_payments')}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 disabled:opacity-50 transition-colors"
          >
            <Activity size={16} />
            Encaissements
          </button>
          <button
            onClick={() => handleSync('suppliers')}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 disabled:opacity-50 transition-colors"
          >
            <RefreshCw size={16} />
            Fournisseurs
          </button>
          <button
            onClick={() => handleSync('full')}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {syncing && <Loader2 size={16} className="animate-spin" />}
            Sync complete
          </button>
        </div>
      </div>

      {/* History list */}
      {history.length === 0 ? (
        <div className="text-center py-12 text-gray-600 bg-gray-50 rounded-xl">
          <Clock className="w-12 h-12 mx-auto text-gray-500 mb-3" />
          <p className="font-medium">Aucune synchronisation enregistree</p>
          <p className="text-sm">Lancez une synchronisation pour commencer</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Traites</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Crees</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Maj</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">En attente</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Duree</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {history.map((sync, index) => {
                const statusConfig = SYNC_STATUS_CONFIG[sync.status]
                const syncTypeLabel = SYNC_TYPE_LABELS[sync.sync_type as PennylaneSyncType] || sync.sync_type

                return (
                  <tr key={sync.id || index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDateTime(sync.started_at)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-gray-900">{syncTypeLabel}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-center gap-1.5">
                        {getStatusIcon(sync.status)}
                        <span
                          className="px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{
                            backgroundColor: statusConfig.bgColor,
                            color: statusConfig.color,
                          }}
                        >
                          {statusConfig.label}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900">
                      {sync.records_processed}
                    </td>
                    <td className="px-4 py-3 text-right text-green-600">
                      +{sync.records_created}
                    </td>
                    <td className="px-4 py-3 text-right text-blue-600">
                      {sync.records_updated}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {sync.records_pending > 0 ? (
                        <span className="text-orange-600 font-medium">{sync.records_pending}</span>
                      ) : (
                        <span className="text-gray-600">0</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 whitespace-nowrap">
                      {formatDuration(sync.started_at, sync.completed_at)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {/* Error message row for failed syncs */}
          {history.some((s) => s.status === 'failed' && s.error_message) && (
            <div className="border-t border-gray-200 p-4">
              <h4 className="font-medium text-red-700 mb-2">Erreurs recentes</h4>
              {history
                .filter((s) => s.status === 'failed' && s.error_message)
                .slice(0, 3)
                .map((sync, index) => (
                  <div
                    key={index}
                    className="text-sm text-red-600 bg-red-50 p-2 rounded mb-2 last:mb-0 break-words overflow-hidden"
                  >
                    <span className="font-medium">{formatDateTime(sync.started_at)}:</span>{' '}
                    {sync.error_message}
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Stats summary */}
      {history.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {history.filter((s) => s.status === 'success').length}
            </p>
            <p className="text-sm text-gray-500">Reussies</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {history.filter((s) => s.status === 'failed').length}
            </p>
            <p className="text-sm text-gray-500">Echecs</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {history.reduce((sum, s) => sum + s.records_processed, 0)}
            </p>
            <p className="text-sm text-gray-500">Total traites</p>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {history.reduce((sum, s) => sum + s.records_created, 0)}
            </p>
            <p className="text-sm text-gray-500">Total crees</p>
          </div>
        </div>
      )}
    </div>
  )
}
