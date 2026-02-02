/**
 * BudgetsPage - Gestion des budgets par chantier
 * CDC Module 17 - FIN-01, FIN-02
 *
 * Connecté à l'API : GET /api/financier/chantiers/{id}/dashboard-financier
 */

import { useState, useEffect, useCallback } from 'react'
import Layout from '../components/Layout'
import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { Chantier, KPIFinancier } from '../types'
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Search,
  Euro,
  Calendar,
  Building2,
  Loader2,
} from 'lucide-react'

interface BudgetChantier {
  chantier: Chantier
  kpi: KPIFinancier | null
}

export default function BudgetsPage() {
  const [budgetChantiers, setBudgetChantiers] = useState<BudgetChantier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Charger les chantiers actifs
      const chantiersData = await chantiersService.list()
      const chantiersList: Chantier[] = Array.isArray(chantiersData)
        ? chantiersData
        : (chantiersData as { items?: Chantier[] }).items || []

      // Charger le dashboard financier de chaque chantier
      const results: BudgetChantier[] = await Promise.all(
        chantiersList.map(async (chantier) => {
          try {
            const dashboard = await financierService.getDashboardFinancier(Number(chantier.id))
            return { chantier, kpi: dashboard.kpi }
          } catch {
            // Pas de budget pour ce chantier = KPI null
            return { chantier, kpi: null }
          }
        })
      )

      // Ne garder que les chantiers qui ont un budget
      setBudgetChantiers(results.filter((r) => r.kpi !== null))
    } catch (err) {
      logger.error('Erreur chargement budgets', err, { context: 'BudgetsPage' })
      setError('Impossible de charger les budgets')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const getStatut = (kpi: KPIFinancier): 'actif' | 'depasse' | 'termine' => {
    if (kpi.pct_engage > 100) return 'depasse'
    if (kpi.pct_realise >= 100) return 'termine'
    return 'actif'
  }

  const getStatutColor = (statut: string) => {
    switch (statut) {
      case 'actif':
        return 'bg-green-100 text-green-800'
      case 'termine':
        return 'bg-gray-100 text-gray-800'
      case 'depasse':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatutLabel = (statut: string) => {
    switch (statut) {
      case 'actif': return 'Actif'
      case 'termine': return 'Terminé'
      case 'depasse': return 'Dépassé'
      default: return statut
    }
  }

  const formatMontant = (montant: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(montant)
  }

  const filteredBudgets = budgetChantiers.filter((bc) =>
    bc.chantier.nom.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calcul des totaux
  const totalPrevu = budgetChantiers.reduce((sum, bc) => sum + (bc.kpi?.montant_revise_ht || 0), 0)
  const totalEngage = budgetChantiers.reduce((sum, bc) => sum + (bc.kpi?.total_engage || 0), 0)
  const totalRealise = budgetChantiers.reduce((sum, bc) => sum + (bc.kpi?.total_realise || 0), 0)

  return (
    <Layout title="Budgets">
      <div className="space-y-6">
        {/* En-tête avec statistiques globales */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Budget Prévisionnel</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalPrevu)}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Euro className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Engagé</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalEngage)}
                </p>
                {totalPrevu > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    {((totalEngage / totalPrevu) * 100).toFixed(1)}% du prévu
                  </p>
                )}
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Déboursé</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalRealise)}
                </p>
                {totalPrevu > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    {((totalRealise / totalPrevu) * 100).toFixed(1)}% du prévu
                  </p>
                )}
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Barre de recherche */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="relative flex-1 w-full md:w-auto">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher un chantier..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <Loader2 className="w-8 h-8 text-blue-500 mx-auto mb-3 animate-spin" />
            <p className="text-gray-500">Chargement des budgets...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-red-700">{error}</p>
            <button onClick={loadData} className="ml-auto btn btn-outline text-sm">
              Réessayer
            </button>
          </div>
        )}

        {/* Liste des budgets */}
        {!loading && !error && (
          <div className="space-y-4">
            {filteredBudgets.map((bc) => {
              const kpi = bc.kpi!
              const statut = getStatut(kpi)
              const tauxConsommation = kpi.pct_realise
              const tauxEngagement = kpi.pct_engage

              return (
                <div
                  key={bc.chantier.id}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{bc.chantier.nom}</h3>
                        <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {bc.chantier.date_debut_prevue
                              ? new Date(bc.chantier.date_debut_prevue + 'T00:00:00').toLocaleDateString('fr-FR')
                              : '—'}{' '}
                            -{' '}
                            {bc.chantier.date_fin_prevue
                              ? new Date(bc.chantier.date_fin_prevue + 'T00:00:00').toLocaleDateString('fr-FR')
                              : '—'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getStatutColor(statut)}`}
                    >
                      {getStatutLabel(statut)}
                    </span>
                  </div>

                  {/* Montants */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-500">Prévu</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {formatMontant(kpi.montant_revise_ht)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Engagé</p>
                      <p className="text-lg font-semibold text-orange-600">
                        {formatMontant(kpi.total_engage)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Déboursé</p>
                      <p className="text-lg font-semibold text-green-600">
                        {formatMontant(kpi.total_realise)}
                      </p>
                    </div>
                  </div>

                  {/* Barres de progression */}
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Taux de consommation</span>
                        <span className="font-medium">{tauxConsommation.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            tauxConsommation > 100
                              ? 'bg-red-500'
                              : tauxConsommation > 80
                              ? 'bg-orange-500'
                              : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(tauxConsommation, 100)}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Taux d'engagement</span>
                        <span className="font-medium">{tauxEngagement.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            tauxEngagement > 100
                              ? 'bg-red-500'
                              : tauxEngagement > 80
                              ? 'bg-orange-500'
                              : 'bg-blue-500'
                          }`}
                          style={{ width: `${Math.min(tauxEngagement, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Alerte si dépassement */}
                  {statut === 'depasse' && (
                    <div className="mt-4 flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-red-800">Budget dépassé</p>
                        <p className="text-xs text-red-600 mt-1">
                          Dépassement de{' '}
                          {formatMontant(kpi.total_engage - kpi.montant_revise_ht)}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {!loading && !error && filteredBudgets.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Aucun budget trouvé</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
