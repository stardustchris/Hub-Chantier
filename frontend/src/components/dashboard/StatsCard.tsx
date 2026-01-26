/**
 * StatsCard - Carte statistiques hebdomadaires
 * CDC Section 2 - KPI adaptes au role
 * Cliquable pour accéder aux feuilles d'heures
 */

import { useNavigate } from 'react-router-dom'

interface StatsCardProps {
  hoursWorked?: string
  hoursProgress?: number
  tasksCompleted?: number
  tasksTotal?: number
}

export default function StatsCard({
  hoursWorked = '32h15',
  hoursProgress = 80,
  tasksCompleted = 8,
  tasksTotal = 12,
}: StatsCardProps) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate('/feuilles-heures')}
      className="bg-white rounded-2xl p-5 shadow-lg cursor-pointer hover:shadow-xl transition-shadow"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && navigate('/feuilles-heures')}
      title="Voir les feuilles d'heures"
    >
      <h3 className="font-semibold text-gray-800 mb-4">Cette semaine</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">Heures travaillees</span>
            <span className="font-bold text-xl text-gray-900">{hoursWorked}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-300"
              style={{ width: `${hoursProgress}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Taches terminees</span>
            <span className="font-bold text-xl text-green-600">
              {tasksCompleted}/{tasksTotal}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
