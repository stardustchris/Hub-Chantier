/**
 * BudgetDashboard - KPI cards et repartition par lot (FIN-11 + FIN-16)
 *
 * Affiche les indicateurs financiers cles d'un chantier :
 * - Banniere alertes actives (Phase 1)
 * - Budget revise HT
 * - Montant engage (avec jauge circulaire)
 * - Montant realise (avec jauge circulaire)
 * - Reste a depenser (FIN-16)
 * - Marge estimee
 * - Repartition par lot
 */

import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Loader2, Wallet } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import CircularGauge from './CircularGauge'
import EvolutionChart from './EvolutionChart'
import CamembertLots from './CamembertLots'
import BarresComparativesLots from './BarresComparativesLots'
import type { Budget, DashboardFinancier, AlerteDepassement } from '../../types'

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
  const [alertes, setAlertes] = useState<AlerteDepassement[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [data, alertesData] = await Promise.all([
        financierService.getDashboardFinancier(chantierId),
        financierService.listAlertes(chantierId, true).catch(() => [] as AlerteDepassement[]),
      ])
      setDashboard(data)
      setAlertes(alertesData)
    } catch (err) {
      setError('Erreur lors du chargement du dashboard financier')
      logger.error('Erreur chargement dashboard financier', err, { context: 'BudgetDashboard' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

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
  const resteNegatif = Number(kpi.reste_a_depenser) < 0

  return (
    <div className="space-y-6">
      {/* Banniere alertes actives */}
      {alertes.length > 0 && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded-r-lg" role="alert" aria-label={`${alertes.length} alerte${alertes.length > 1 ? 's' : ''} budgetaire${alertes.length > 1 ? 's' : ''}`}>
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-orange-900">
                {alertes.length} alerte{alertes.length > 1 ? 's' : ''} budgetaire{alertes.length > 1 ? 's' : ''}
              </p>
              <ul className="text-sm text-orange-700 mt-1 space-y-0.5">
                {alertes.slice(0, 3).map(a => (
                  <li key={a.id}>- {a.message}</li>
                ))}
                {alertes.length > 3 && (
                  <li className="text-orange-500 text-xs">
                    + {alertes.length - 3} autre{alertes.length - 3 > 1 ? 's' : ''}
                  </li>
                )}
              </ul>
            </div>
            <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-orange-200 text-orange-800 text-sm font-bold flex-shrink-0">
              {alertes.length}
            </span>
          </div>
        </div>
      )}

      {/* KPI Cards - 5 colonnes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
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
            <CircularGauge
              value={Number(kpi.pct_engage)}
              thresholds={{ warning: Number(budget.seuil_alerte_pct), danger: 100 }}
            />
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
            <CircularGauge value={Number(kpi.pct_realise)} />
          </div>
        </div>

        {/* Reste a depenser (FIN-16) */}
        <div className={`bg-white border rounded-xl p-4 ${resteNegatif ? 'border-red-300' : 'border-blue-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Reste a depenser</p>
            <Wallet className={`w-4 h-4 ${resteNegatif ? 'text-red-500' : 'text-blue-500'}`} />
          </div>
          <p className={`text-2xl font-bold ${resteNegatif ? 'text-red-600' : 'text-blue-700'}`}>
            {formatEUR(kpi.reste_a_depenser)}
          </p>
          <div className="mt-2">
            <CircularGauge
              value={Number(kpi.pct_reste)}
              color={resteNegatif ? '#ef4444' : '#3b82f6'}
              thresholds={{ warning: 80, danger: 100 }}
            />
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

      {/* Graphiques Phase 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white border rounded-xl p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Evolution financiere</h3>
          <EvolutionChart chantierId={chantierId} />
        </div>
        <div className="bg-white border rounded-xl p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Repartition par lot</h3>
          <CamembertLots lots={dashboard?.repartition_par_lot || []} />
        </div>
      </div>
      {dashboard?.repartition_par_lot && dashboard.repartition_par_lot.length > 0 && (
        <div className="bg-white border rounded-xl p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Comparaison par lot</h3>
          <BarresComparativesLots lots={dashboard.repartition_par_lot} />
        </div>
      )}

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
