/**
 * ValidationDashboard - Tableau de bord de validation des feuilles d'heures
 * Affiche les métriques clés pour les validateurs (admin/conducteur/chef)
 */

import { useMemo } from 'react'
import { Clock, CheckCircle, TrendingUp } from 'lucide-react'
import type { VueCompagnon } from '../../types'

interface ValidationDashboardProps {
  vueCompagnons: VueCompagnon[]
  selectablePointagesCount: number
}

interface StatCard {
  label: string
  value: string | number
  icon: React.ElementType
  color: string
  bgColor: string
}

export default function ValidationDashboard({ vueCompagnons, selectablePointagesCount }: ValidationDashboardProps) {
  // Calcul des statistiques à partir des données disponibles
  const stats = useMemo(() => {
    let totalHeuresSemaine = 0
    let totalPointages = 0
    let totalValides = 0

    vueCompagnons.forEach((vue) => {
      // Total heures de la semaine pour cet utilisateur
      totalHeuresSemaine += vue.total_heures_decimal

      // Compter tous les pointages par statut
      vue.chantiers.forEach((chantier) => {
        Object.values(chantier.pointages_par_jour).forEach((pointagesJour) => {
          pointagesJour.forEach((pointage) => {
            totalPointages++
            if (pointage.statut === 'valide') {
              totalValides++
            }
          })
        })
      })
    })

    // Taux de validation (% de pointages validés / total)
    const tauxValidation = totalPointages > 0 ? Math.round((totalValides / totalPointages) * 100) : 0

    return {
      totalHeuresSemaine,
      totalPointages,
      totalValides,
      tauxValidation,
    }
  }, [vueCompagnons])

  // Configuration des cards
  const cards: StatCard[] = useMemo(() => {
    return [
      {
        label: 'En attente de validation',
        value: selectablePointagesCount,
        icon: Clock,
        color: '#F59E0B',
        bgColor: '#FEF3C7',
      },
      {
        label: 'Total heures cette semaine',
        value: `${stats.totalHeuresSemaine.toFixed(1)}h`,
        icon: TrendingUp,
        color: '#3B82F6',
        bgColor: '#DBEAFE',
      },
      {
        label: 'Taux de validation',
        value: `${stats.tauxValidation}%`,
        icon: CheckCircle,
        color: stats.tauxValidation >= 80 ? '#10B981' : stats.tauxValidation >= 50 ? '#F59E0B' : '#EF4444',
        bgColor: stats.tauxValidation >= 80 ? '#D1FAE5' : stats.tauxValidation >= 50 ? '#FEF3C7' : '#FEE2E2',
      },
      {
        label: 'Pointages validés',
        value: `${stats.totalValides}/${stats.totalPointages}`,
        icon: CheckCircle,
        color: '#10B981',
        bgColor: '#D1FAE5',
      },
    ]
  }, [selectablePointagesCount, stats])

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Tableau de bord de validation</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 flex items-start gap-3"
            >
              <div
                className="p-2 rounded-lg flex-shrink-0"
                style={{ backgroundColor: card.bgColor }}
              >
                <Icon className="w-5 h-5" style={{ color: card.color }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-2xl font-bold text-gray-900 tabular-nums">{card.value}</p>
                <p className="text-xs text-gray-600 mt-1">{card.label}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
