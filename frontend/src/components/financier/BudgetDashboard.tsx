/**
 * BudgetDashboard - KPI cards et repartition par lot (FIN-11)
 *
 * Affiche les indicateurs financiers cles d'un chantier :
 * - Budget revise HT
 * - Montant engage (avec alerte si > seuil)
 * - Montant realise
 * - Marge estimee
 */

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import type { Budget, DashboardFinancier } from '../../types'

interface BudgetDashboardProps {
  chantierId: number
  budget: Budget
}

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const formatPct = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'percent', minimumFractionDigits: 1 }).format(value / 100)

export default function BudgetDashboard({ chantierId, budget }: BudgetDashboardProps) {
  const [dashboard, setDashboard] = useState<DashboardFinancier | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboard()
  }, [chantierId])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.getDashboardFinancier(chantierId)
      setDashboard(data)
    } catch (err) {
      setError('Erreur lors du chargement du dashboard financier')
      logger.error('Erreur chargement dashboard financier', err, { context: 'BudgetDashboard' })
    } finally {
      setLoading(false)
    }
  }

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

  const kpi = dashboard?.kpi
  if (!kpi) return null

  const engageAlerte = Number(kpi.pct_engage) > Number(budget.seuil_alerte_pct)
  const realiseDepasse = Number(kpi.pct_realise) > 100
  const margeFaible = Number(kpi.marge_estimee) < 5

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Budget revise */}
        <div className="bg-white border border-blue-200 rounded-xl p-4">
          <p className="text-sm text-gray-500 mb-1">Budget revise HT</p>
          <p className="text-2xl font-bold text-blue-700">
            {formatEUR(kpi.montant_revise_ht)}
          </p>
          <div className="mt-2 flex items-center gap-1">
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              Initial: {formatEUR(budget.montant_initial_ht)}
            </span>
          </div>
        </div>

        {/* Engage */}
        <div className={`bg-white border rounded-xl p-4 ${engageAlerte ? 'border-orange-300' : 'border-green-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Engage</p>
            {engageAlerte && <AlertTriangle className="w-4 h-4 text-orange-500" />}
          </div>
          <p className={`text-2xl font-bold ${engageAlerte ? 'text-orange-600' : 'text-green-700'}`}>
            {formatEUR(kpi.total_engage)}
          </p>
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-500">{formatPct(kpi.pct_engage)} du budget</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  engageAlerte ? 'bg-orange-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(kpi.pct_engage, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Realise */}
        <div className={`bg-white border rounded-xl p-4 ${realiseDepasse ? 'border-red-300' : 'border-green-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Realise</p>
            {realiseDepasse ? (
              <TrendingUp className="w-4 h-4 text-red-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-green-500" />
            )}
          </div>
          <p className={`text-2xl font-bold ${realiseDepasse ? 'text-red-600' : 'text-green-700'}`}>
            {formatEUR(kpi.total_realise)}
          </p>
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-500">{formatPct(kpi.pct_realise)} du budget</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  realiseDepasse ? 'bg-red-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(kpi.pct_realise, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Marge */}
        <div className={`bg-white border rounded-xl p-4 ${margeFaible ? 'border-red-300' : 'border-green-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Marge estimee</p>
            {margeFaible && <AlertTriangle className="w-4 h-4 text-red-500" />}
          </div>
          <p className={`text-2xl font-bold ${margeFaible ? 'text-red-600' : 'text-green-700'}`}>
            {formatPct(kpi.marge_estimee)}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {margeFaible ? 'Marge inferieure a 5%' : 'Marge correcte'}
          </p>
        </div>
      </div>

      {/* Repartition par lot */}
      {dashboard?.repartition_par_lot && dashboard.repartition_par_lot.length > 0 && (
        <div className="bg-white border rounded-xl p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Repartition par lot</h3>
          <div className="space-y-3">
            {dashboard.repartition_par_lot.map((lot) => {
              const pctEngage = lot.total_prevu_ht > 0 ? (lot.engage / lot.total_prevu_ht) * 100 : 0
              const pctRealise = lot.total_prevu_ht > 0 ? (lot.realise / lot.total_prevu_ht) * 100 : 0
              return (
                <div key={lot.lot_id} className="border-b border-gray-100 last:border-0 pb-3 last:pb-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono bg-gray-100 px-1.5 py-0.5 rounded">
                        {lot.code_lot}
                      </span>
                      <span className="text-sm font-medium text-gray-700">{lot.libelle}</span>
                    </div>
                    <span className="text-sm text-gray-500">{formatEUR(lot.total_prevu_ht)}</span>
                  </div>
                  <div className="flex gap-2 items-center">
                    <div className="flex-1 bg-gray-100 rounded-full h-3 relative overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-blue-400 rounded-full"
                        style={{ width: `${Math.min(pctEngage, 100)}%` }}
                      />
                      <div
                        className="absolute inset-y-0 left-0 bg-green-500 rounded-full"
                        style={{ width: `${Math.min(pctRealise, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">
                      {pctRealise.toFixed(0)}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
          <div className="flex items-center gap-4 mt-4 pt-3 border-t text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-blue-400" />
              <span>Engage</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>Realise</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
