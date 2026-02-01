/**
 * DashboardFinancierPage - Vue d'ensemble financière
 * CDC Module 17 - FIN-11
 */

import { useState } from 'react'
import Layout from '../components/Layout'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Building2,
  Euro,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'

interface ChantierFinancier {
  id: string
  nom: string
  budget_prevu: number
  budget_realise: number
  taux_consommation: number
  statut: 'ok' | 'attention' | 'depassement'
}

export default function DashboardFinancierPage() {
  const [periode] = useState('mois') // 'semaine' | 'mois' | 'trimestre' | 'annee'

  const chantiers: ChantierFinancier[] = [
    {
      id: '1',
      nom: 'Villa Moderne Duplex',
      budget_prevu: 850000,
      budget_realise: 650000,
      taux_consommation: 76.5,
      statut: 'ok',
    },
    {
      id: '2',
      nom: 'Résidence Les Jardins',
      budget_prevu: 2100000,
      budget_realise: 1800000,
      taux_consommation: 85.7,
      statut: 'attention',
    },
    {
      id: '3',
      nom: 'École Jean Jaurès',
      budget_prevu: 500000,
      budget_realise: 520000,
      taux_consommation: 104.0,
      statut: 'depassement',
    },
  ]

  const totalBudgetPrevu = chantiers.reduce((sum, c) => sum + c.budget_prevu, 0)
  const totalBudgetRealise = chantiers.reduce((sum, c) => sum + c.budget_realise, 0)
  const tauxConsommationGlobal = (totalBudgetRealise / totalBudgetPrevu) * 100

  // Chiffres clés
  const depensesduMois = 285000
  const evolutionDepenses = +12.5 // pourcentage vs mois précédent
  const depensesMoyennesParJour = 9500
  const chantiersDansLeBudget = chantiers.filter((c) => c.statut === 'ok').length
  const chantiersEnDepassement = chantiers.filter((c) => c.statut === 'depassement').length

  const formatMontant = (montant: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(montant)
  }

  const getStatutConfig = (statut: ChantierFinancier['statut']) => {
    switch (statut) {
      case 'ok':
        return {
          label: 'Dans le budget',
          color: 'text-green-600 bg-green-100',
          icon: CheckCircle,
        }
      case 'attention':
        return {
          label: 'Attention',
          color: 'text-orange-600 bg-orange-100',
          icon: AlertTriangle,
        }
      case 'depassement':
        return {
          label: 'Dépassement',
          color: 'text-red-600 bg-red-100',
          icon: TrendingUp,
        }
    }
  }

  return (
    <Layout title="Dashboard Financier">
      <div className="space-y-6">
        {/* En-tête avec filtres */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Vue d'ensemble</h2>
            <select className="input w-48">
              <option value="mois">Ce mois</option>
              <option value="semaine">Cette semaine</option>
              <option value="trimestre">Ce trimestre</option>
              <option value="annee">Cette année</option>
            </select>
          </div>
        </div>

        {/* KPIs principaux */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Budget Total</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalBudgetPrevu)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatMontant(totalBudgetRealise)} réalisé
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
                <p className="text-sm text-gray-600">Dépenses du mois</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(depensesduMois)}
                </p>
                <div className="flex items-center gap-1 mt-1">
                  {evolutionDepenses > 0 ? (
                    <>
                      <ArrowUpRight className="w-3 h-3 text-red-500" />
                      <span className="text-xs text-red-500">
                        +{evolutionDepenses}% vs mois dernier
                      </span>
                    </>
                  ) : (
                    <>
                      <ArrowDownRight className="w-3 h-3 text-green-500" />
                      <span className="text-xs text-green-500">
                        {evolutionDepenses}% vs mois dernier
                      </span>
                    </>
                  )}
                </div>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Dépenses moy./jour</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(depensesMoyennesParJour)}
                </p>
                <p className="text-xs text-gray-500 mt-1">30 derniers jours</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Taux de consommation</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {tauxConsommationGlobal.toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {chantiersDansLeBudget} chantiers OK / {chantiersEnDepassement} dépassés
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Graphique de consommation budgétaire */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Consommation budgétaire globale
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Budget réalisé</span>
              <span className="font-semibold">{formatMontant(totalBudgetRealise)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 relative overflow-hidden">
              <div
                className={`h-4 rounded-full transition-all ${
                  tauxConsommationGlobal > 100
                    ? 'bg-red-500'
                    : tauxConsommationGlobal > 80
                    ? 'bg-orange-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(tauxConsommationGlobal, 100)}%` }}
              />
              {tauxConsommationGlobal > 100 && (
                <div className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">
                  Dépassement !
                </div>
              )}
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Budget prévu</span>
              <span className="font-semibold">{formatMontant(totalBudgetPrevu)}</span>
            </div>
          </div>
        </div>

        {/* Détail par chantier */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Détail par chantier</h3>
          <div className="space-y-4">
            {chantiers.map((chantier) => {
              const statutConfig = getStatutConfig(chantier.statut)
              const StatutIcon = statutConfig.icon

              return (
                <div
                  key={chantier.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{chantier.nom}</h4>
                        <p className="text-sm text-gray-500">
                          {formatMontant(chantier.budget_realise)} /{' '}
                          {formatMontant(chantier.budget_prevu)}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${statutConfig.color}`}
                    >
                      <StatutIcon className="w-3.5 h-3.5" />
                      {statutConfig.label}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">Taux de consommation</span>
                      <span className="font-medium">{chantier.taux_consommation.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          chantier.taux_consommation > 100
                            ? 'bg-red-500'
                            : chantier.taux_consommation > 80
                            ? 'bg-orange-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(chantier.taux_consommation, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Alertes et actions recommandées */}
        {chantiersEnDepassement > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-2">
                  Attention : {chantiersEnDepassement} chantier
                  {chantiersEnDepassement > 1 ? 's' : ''} en dépassement budgétaire
                </h3>
                <p className="text-sm text-red-700 mb-3">
                  Une révision des budgets est recommandée pour les chantiers suivants :
                </p>
                <ul className="space-y-1">
                  {chantiers
                    .filter((c) => c.statut === 'depassement')
                    .map((c) => (
                      <li key={c.id} className="text-sm text-red-800 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-red-600 rounded-full" />
                        {c.nom} - Dépassement de{' '}
                        {formatMontant(c.budget_realise - c.budget_prevu)}
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
