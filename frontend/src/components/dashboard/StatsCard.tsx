/**
 * StatsCard - Carte statistiques de travail
 * Affiche: heures semaine, jours mois, congés annuels
 * Cliquable pour accéder aux feuilles d'heures
 */

import { useNavigate } from 'react-router-dom'
import { Clock, Calendar, TreePalm } from 'lucide-react'

interface StatsCardProps {
  hoursWorked?: string
  hoursProgress?: number
  joursTravailesMois?: number
  joursTotalMois?: number
  congesPris?: number
  congesTotal?: number
}

export default function StatsCard({
  hoursWorked = '0h00',
  hoursProgress = 0,
  joursTravailesMois = 0,
  joursTotalMois = 22,
  congesPris = 0,
  congesTotal = 25,
}: StatsCardProps) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate('/feuilles-heures')}
      className="bg-white rounded-2xl p-5 shadow-lg cursor-pointer hover-lift"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && navigate('/feuilles-heures')}
      title="Voir les feuilles d'heures"
    >
      <h3 className="font-semibold text-gray-800 mb-4">Heures travaillees</h3>
      <div className="space-y-3">
        {/* Heures de la semaine en cours */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-sm text-gray-600 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              Semaine en cours
            </span>
            <span className="font-bold text-lg text-gray-900">{hoursWorked}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-300"
              style={{ width: `${hoursProgress}%` }}
            />
          </div>
          <div className="text-xs text-gray-600 text-right mt-0.5">/ 35h</div>
        </div>

        {/* Jours travaillés du mois */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" />
            Jours travailles (mois)
          </span>
          <span className="font-bold text-lg text-gray-900">
            {joursTravailesMois}<span className="text-sm font-normal text-gray-500">/{joursTotalMois}</span>
          </span>
        </div>

        {/* Congés pris */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 flex items-center gap-1.5">
            <TreePalm className="w-3.5 h-3.5" />
            Conges pris (annee)
          </span>
          <span className="font-bold text-lg text-gray-900">
            {congesPris}<span className="text-sm font-normal text-gray-500">/{congesTotal}j</span>
          </span>
        </div>
      </div>
    </div>
  )
}
