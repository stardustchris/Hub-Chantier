/**
 * AlertesPanel - Alertes de depassement budgetaire (FIN-12)
 *
 * Affiche :
 * - Alertes actives (non-acquittees) en haut avec style warning
 * - Liste de toutes les alertes: type, message, pourcentage, montant
 * - Bouton Acquitter
 * - Bouton "Verifier maintenant" pour declencher une verification
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import type { AlerteDepassement } from '../../types'
import { TYPE_ALERTE_LABELS } from '../../types'

interface AlertesPanelProps {
  chantierId: number
}

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatPct = (value: number): string =>
  value.toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %'

export default function AlertesPanel({ chantierId }: AlertesPanelProps) {
  const { user } = useAuth()
  const [alertes, setAlertes] = useState<AlerteDepassement[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [verifying, setVerifying] = useState(false)

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  const loadAlertes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listAlertes(chantierId)
      setAlertes(data)
    } catch (err) {
      setError('Erreur lors du chargement des alertes')
      logger.error('Erreur chargement alertes', err, { context: 'AlertesPanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadAlertes()
  }, [loadAlertes])

  const handleAcquitter = async (id: number) => {
    try {
      const updated = await financierService.acquitterAlerte(id)
      setAlertes(prev => prev.map(a => a.id === updated.id ? updated : a))
    } catch (err) {
      console.error('Erreur acquittement alerte:', err)
    }
  }

  const handleVerifier = async () => {
    try {
      setVerifying(true)
      await financierService.verifierDepassement(chantierId)
      await loadAlertes()
    } catch (err) {
      console.error('Erreur verification depassement:', err)
    } finally {
      setVerifying(false)
    }
  }

  const alertesActives = alertes.filter(a => !a.est_acquittee)
  const alertesAcquittees = alertes.filter(a => a.est_acquittee)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with verify button */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Alertes de depassement</h3>
        {canManage && (
          <button
            onClick={handleVerifier}
            disabled={verifying}
            className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={verifying ? 'animate-spin' : ''} />
            {verifying ? 'Verification...' : 'Verifier maintenant'}
          </button>
        )}
      </div>

      {/* Active alerts */}
      {alertesActives.length > 0 && (
        <div className="space-y-2">
          {alertesActives.map((alerte) => (
            <div
              key={alerte.id}
              className="bg-amber-50 border border-amber-300 rounded-xl p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-200 text-amber-800">
                        {TYPE_ALERTE_LABELS[alerte.type_alerte]}
                      </span>
                      <span className="text-xs text-gray-500">{formatDate(alerte.created_at)}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{alerte.message}</p>
                    <div className="flex flex-wrap gap-4 mt-2 text-xs text-gray-600">
                      <span>Atteint : {formatPct(alerte.pourcentage_atteint)}</span>
                      <span>Seuil : {formatPct(alerte.seuil_configure)}</span>
                      <span>Budget : {formatEUR(alerte.montant_budget_ht)}</span>
                      <span>Montant atteint : {formatEUR(alerte.montant_atteint_ht)}</span>
                    </div>
                  </div>
                </div>
                {canManage && (
                  <button
                    onClick={() => handleAcquitter(alerte.id)}
                    className="flex items-center gap-1 px-3 py-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 text-sm transition-colors flex-shrink-0"
                  >
                    <CheckCircle size={14} />
                    Acquitter
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {alertesActives.length === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
          <p className="text-sm text-green-700">Aucune alerte active</p>
        </div>
      )}

      {/* Acknowledged alerts */}
      {alertesAcquittees.length > 0 && (
        <div className="bg-white border rounded-xl">
          <div className="p-4 border-b">
            <h4 className="font-semibold text-gray-900 text-sm">Alertes acquittees ({alertesAcquittees.length})</h4>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Message</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Pourcentage</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Montant</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {alertesAcquittees.map((alerte) => (
                  <tr key={alerte.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(alerte.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        {TYPE_ALERTE_LABELS[alerte.type_alerte]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 max-w-[300px] truncate">
                      {alerte.message}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500">
                      {formatPct(alerte.pourcentage_atteint)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500 whitespace-nowrap">
                      {formatEUR(alerte.montant_atteint_ht)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
