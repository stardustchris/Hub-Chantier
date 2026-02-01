/**
 * BudgetsPage - Gestion des budgets par chantier
 * CDC Module 17 - FIN-01, FIN-02
 */

import { useState } from 'react'
import Layout from '../components/Layout'
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Plus,
  Search,
  Filter,
  Euro,
  Calendar,
  Building2,
} from 'lucide-react'

interface Budget {
  id: string
  chantier_nom: string
  montant_prevu: number
  montant_engage: number
  montant_realise: number
  date_debut: string
  date_fin: string
  statut: 'actif' | 'termine' | 'depasse'
}

export default function BudgetsPage() {
  const [budgets] = useState<Budget[]>([
    {
      id: '1',
      chantier_nom: 'Villa Moderne Duplex',
      montant_prevu: 850000,
      montant_engage: 720000,
      montant_realise: 650000,
      date_debut: '2026-01-15',
      date_fin: '2026-08-30',
      statut: 'actif',
    },
    {
      id: '2',
      chantier_nom: 'Résidence Les Jardins',
      montant_prevu: 2100000,
      montant_engage: 1950000,
      montant_realise: 1800000,
      date_debut: '2025-10-01',
      date_fin: '2026-12-31',
      statut: 'actif',
    },
    {
      id: '3',
      chantier_nom: 'École Jean Jaurès',
      montant_prevu: 500000,
      montant_engage: 520000,
      montant_realise: 480000,
      date_debut: '2025-09-01',
      date_fin: '2026-03-31',
      statut: 'depasse',
    },
  ])

  const [searchQuery, setSearchQuery] = useState('')

  const getTauxConsommation = (budget: Budget) => {
    return (budget.montant_realise / budget.montant_prevu) * 100
  }

  const getTauxEngagement = (budget: Budget) => {
    return (budget.montant_engage / budget.montant_prevu) * 100
  }

  const getStatutColor = (statut: Budget['statut']) => {
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

  const formatMontant = (montant: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(montant)
  }

  const filteredBudgets = budgets.filter((budget) =>
    budget.chantier_nom.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calcul des totaux
  const totalPrevu = budgets.reduce((sum, b) => sum + b.montant_prevu, 0)
  const totalEngage = budgets.reduce((sum, b) => sum + b.montant_engage, 0)
  const totalRealise = budgets.reduce((sum, b) => sum + b.montant_realise, 0)

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
                <p className="text-xs text-gray-500 mt-1">
                  {((totalEngage / totalPrevu) * 100).toFixed(1)}% du prévu
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Réalisé</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalRealise)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {((totalRealise / totalPrevu) * 100).toFixed(1)}% du prévu
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Barre d'actions */}
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
            <div className="flex gap-2 w-full md:w-auto">
              <button className="btn btn-outline flex items-center gap-2">
                <Filter className="w-4 h-4" />
                Filtrer
              </button>
              <button className="btn btn-primary flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Nouveau budget
              </button>
            </div>
          </div>
        </div>

        {/* Liste des budgets */}
        <div className="space-y-4">
          {filteredBudgets.map((budget) => {
            const tauxConsommation = getTauxConsommation(budget)
            const tauxEngagement = getTauxEngagement(budget)

            return (
              <div
                key={budget.id}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{budget.chantier_nom}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(budget.date_debut).toLocaleDateString('fr-FR')} -{' '}
                          {new Date(budget.date_fin).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStatutColor(
                      budget.statut
                    )}`}
                  >
                    {budget.statut === 'actif' && 'Actif'}
                    {budget.statut === 'termine' && 'Terminé'}
                    {budget.statut === 'depasse' && 'Dépassé'}
                  </span>
                </div>

                {/* Montants */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Prévu</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatMontant(budget.montant_prevu)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Engagé</p>
                    <p className="text-lg font-semibold text-orange-600">
                      {formatMontant(budget.montant_engage)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Réalisé</p>
                    <p className="text-lg font-semibold text-green-600">
                      {formatMontant(budget.montant_realise)}
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
                {budget.statut === 'depasse' && (
                  <div className="mt-4 flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Budget dépassé</p>
                      <p className="text-xs text-red-600 mt-1">
                        Dépassement de{' '}
                        {formatMontant(budget.montant_engage - budget.montant_prevu)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {filteredBudgets.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Aucun budget trouvé</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
