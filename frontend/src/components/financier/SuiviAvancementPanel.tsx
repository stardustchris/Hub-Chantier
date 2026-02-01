/**
 * SuiviAvancementPanel - Suivi croise avancement physique/financier (FIN-03)
 *
 * Affiche :
 * - Resume en haut: total montant affecte, progression moyenne
 * - Table: Tache, Statut, Progression (%), Lot, Montant HT, % Affecte, Montant affecte HT
 * - Barre de progression coloree pour chaque ligne
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, AlertCircle, BarChart3 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import type { SuiviAvancementItem } from '../../types'

interface SuiviAvancementPanelProps {
  chantierId: number
}

const formatEUR = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '0,00 EUR'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(num)
}

const formatPct = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '0 %'
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(num) + ' %'
}

const getProgressColor = (pct: number): string => {
  if (pct >= 100) return 'bg-green-500'
  if (pct >= 75) return 'bg-blue-500'
  if (pct >= 50) return 'bg-yellow-500'
  if (pct >= 25) return 'bg-orange-500'
  return 'bg-gray-400'
}

const getStatutBadge = (statut: string): { label: string; color: string } => {
  switch (statut) {
    case 'a_faire':
      return { label: 'A faire', color: '#9E9E9E' }
    case 'termine':
      return { label: 'Termine', color: '#4CAF50' }
    default:
      return { label: statut, color: '#9E9E9E' }
  }
}

export default function SuiviAvancementPanel({ chantierId }: SuiviAvancementPanelProps) {
  const [items, setItems] = useState<SuiviAvancementItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.getSuiviAvancement(chantierId)
      setItems(data)
    } catch (err) {
      setError('Erreur lors du chargement du suivi avancement')
      logger.error('Erreur chargement suivi avancement', err, { context: 'SuiviAvancementPanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Calculs resume
  const totalMontantAffecte = items.reduce((sum, item) => {
    return sum + parseFloat(item.montant_affecte_ht || '0')
  }, 0)

  const progressionMoyenne = items.length > 0
    ? items.reduce((sum, item) => sum + parseFloat(item.tache_progression_pct || '0'), 0) / items.length
    : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={loadData} className="text-sm underline mt-1">Reessayer</button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex items-center gap-2 p-4 border-b">
        <BarChart3 size={18} className="text-blue-600" />
        <h3 className="font-semibold text-gray-900">Suivi avancement physique / financier</h3>
      </div>

      {/* Resume KPI */}
      <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 border-b">
        <div className="text-center">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total montant affecte</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{formatEUR(totalMontantAffecte)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Progression moyenne</p>
          <div className="flex items-center justify-center gap-2 mt-1">
            <p className="text-lg font-bold text-gray-900">{formatPct(progressionMoyenne)}</p>
            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${getProgressColor(progressionMoyenne)}`}
                style={{ width: `${Math.min(progressionMoyenne, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Aucune donnee de suivi disponible
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Tache</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Progression</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Lot</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">% Affecte</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant affecte</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((item) => {
                const progression = parseFloat(item.tache_progression_pct || '0')
                const statutConfig = getStatutBadge(item.tache_statut)
                return (
                  <tr key={item.affectation_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-700 font-medium">{item.tache_titre}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: statutConfig.color + '20',
                          color: statutConfig.color,
                        }}
                      >
                        {statutConfig.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 justify-center">
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${getProgressColor(progression)}`}
                            style={{ width: `${Math.min(progression, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600 whitespace-nowrap">{formatPct(progression)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      <span className="font-mono text-xs text-gray-500">{item.lot_code}</span>{' '}
                      {item.lot_libelle}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700 whitespace-nowrap">
                      {formatEUR(item.lot_montant_prevu_ht)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700 whitespace-nowrap">
                      {formatPct(item.pourcentage_affectation)}
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900 whitespace-nowrap">
                      {formatEUR(item.montant_affecte_ht)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
