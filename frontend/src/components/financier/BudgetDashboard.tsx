/**
 * BudgetDashboard - KPI cards et repartition par lot (FIN-11 + FIN-16)
 *
 * Affiche les indicateurs financiers cles d'un chantier :
 * - Banniere alertes actives (Phase 1)
 * - Budget revise HT
 * - Montant engage (avec jauge circulaire)
 * - Montant debourse (avec jauge circulaire)
 * - Reste a depenser (FIN-16)
 * - Marge estimee
 * - Repartition par lot
 */

import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Loader2, Wallet, Info } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import CircularGauge from './CircularGauge'
import EvolutionChart from './EvolutionChart'
import CamembertLots from './CamembertLots'
import BarresComparativesLots from './BarresComparativesLots'
import type { Budget, DashboardFinancier, AlerteDepassement } from '../../types'
import { formatEUR, formatPct } from '../../utils/format'

interface BudgetDashboardProps {
  chantierId: number
  budget: Budget
  onDashboardLoaded?: (dashboard: DashboardFinancier) => void
}

export default function BudgetDashboard({ chantierId, budget, onDashboardLoaded }: BudgetDashboardProps) {
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
      onDashboardLoaded?.(data)
    } catch (err) {
      setError('Erreur lors du chargement du dashboard financier')
      logger.error('Erreur chargement dashboard financier', err, { context: 'BudgetDashboard' })
    } finally {
      setLoading(false)
    }
  }, [chantierId, onDashboardLoaded])

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
  const debourseDepasse = Number(kpi.pct_realise) > 100
  const margeFaible = kpi.marge_estimee !== null && kpi.marge_estimee !== undefined && Number(kpi.marge_estimee) < 5
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

      {/* Banniere completude des donnees */}
      {(() => {
        const manquants: string[] = []
        if (kpi.marge_statut !== 'calculee') {
          manquants.push('Aucune situation de travaux — la marge est estimée sur le budget')
        }
        if (Number(kpi.total_realise) === 0 && Number(kpi.total_engage) > 0) {
          manquants.push('Aucun achat facturé — le déboursé réel est à 0')
        }

        return manquants.length > 0 ? (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-blue-900">Données incomplètes</p>
                <ul className="text-sm text-blue-700 mt-1 space-y-0.5">
                  {manquants.map((m, i) => <li key={i}>• {m}</li>)}
                </ul>
              </div>
            </div>
          </div>
        ) : null
      })()}

      {/* KPI Cards - 5 colonnes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {/* Budget revise */}
        <div className="bg-white border border-blue-200 rounded-xl p-4">
          <p className="text-sm text-gray-500 mb-1">Budget révisé HT</p>
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
            <p className="text-sm text-gray-500 mb-1">Engagé</p>
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

        {/* Déboursé */}
        <div className={`bg-white border rounded-xl p-4 ${debourseDepasse ? 'border-red-300' : 'border-green-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Déboursé</p>
            {debourseDepasse ? (
              <TrendingUp className="w-4 h-4 text-red-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-green-500" />
            )}
          </div>
          <p className={`text-2xl font-bold ${debourseDepasse ? 'text-red-600' : 'text-green-700'}`}>
            {formatEUR(kpi.total_realise)}
          </p>
          <div className="mt-2">
            <CircularGauge value={Number(kpi.pct_realise)} />
          </div>
        </div>

        {/* Reste a depenser (FIN-16) */}
        <div className={`bg-white border rounded-xl p-4 ${resteNegatif ? 'border-red-300' : 'border-blue-200'}`}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500 mb-1">Reste à dépenser</p>
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
            <p className="text-sm text-gray-500 mb-1">
              {kpi.marge_statut === 'calculee' && 'Marge (calculée)'}
              {kpi.marge_statut === 'estimee_budgetaire' && 'Consommation budget'}
              {kpi.marge_statut === 'partielle' && 'Marge (partielle)'}
              {kpi.marge_statut === 'en_attente' && 'Marge : en attente'}
              {!kpi.marge_statut && 'Marge estimée'}
            </p>
            {margeFaible && <AlertTriangle className="w-4 h-4 text-red-500" />}
          </div>
          <p className={`text-2xl font-bold ${
            kpi.marge_statut === 'en_attente' ? 'text-gray-400' :
            margeFaible ? 'text-red-600' : 'text-green-700'
          }`}>
            {kpi.marge_estimee === null || kpi.marge_estimee === undefined ? (
              <span className="text-gray-400">{formatPct(null)}</span>
            ) : Number(kpi.marge_estimee) < 0 ? (
              <span className="text-red-700">{formatPct(Number(kpi.marge_estimee))} PERTE</span>
            ) : (
              formatPct(Number(kpi.marge_estimee))
            )}
          </p>
          <p className="text-xs mt-2 flex items-center gap-1">
            {kpi.marge_statut === 'calculee' && (
              <span className="text-green-600 bg-green-50 px-2 py-0.5 rounded-full">Calculée (CA réel)</span>
            )}
            {kpi.marge_statut === 'estimee_budgetaire' && (
              <span className="text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full inline-flex items-center gap-1" title="Ceci n'est pas une marge commerciale. C'est le ratio (Budget - Engagé) / Budget.">
                Estimation budgétaire
                <AlertTriangle className="w-3 h-3" />
              </span>
            )}
            {kpi.marge_statut === 'partielle' && (
              <span className="text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full">Partielle</span>
            )}
            {kpi.marge_statut === 'en_attente' && (
              <span className="text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">En attente</span>
            )}
            {!kpi.marge_statut && (
              <span className="text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">Estimée (budget)</span>
            )}
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
          <h3 className="font-semibold text-gray-900 mb-4">Poids financier par lot</h3>
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
          <h3 className="font-semibold text-gray-900 mb-4">Suivi par lot</h3>
          <div className="space-y-3">
            {dashboard.repartition_par_lot.map((lot) => {
              const prevuHT = Number(lot.total_prevu_ht)
              const engageHT = Number(lot.engage)
              const realiseHT = Number(lot.realise)
              const pctEngage = prevuHT > 0 ? (engageHT / prevuHT) * 100 : 0
              const pctRealise = prevuHT > 0 ? (realiseHT / prevuHT) * 100 : 0
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
                        className="absolute inset-y-0 left-0 bg-amber-400 rounded-full"
                        style={{ width: `${Math.min(pctEngage, 100)}%` }}
                      />
                      <div
                        className="absolute inset-y-0 left-0 bg-emerald-600 rounded-full"
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
              <div className="w-3 h-3 rounded-full bg-amber-400" />
              <span>Engagé</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-emerald-600" />
              <span>Déboursé</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
