/**
 * TeamLeaderboardCard - Classement équipe hebdomadaire
 * CDC Section 5.4.3 - Gamification légère
 *
 * Affiche un classement des membres de l'équipe basé sur leurs heures loguées vs planifiées
 * Top 3 avec indicateurs visuels (🥇🥈🥉)
 * Compact, max 5 visibles, scrollable si plus
 */

import { memo } from 'react'
import { Trophy, TrendingUp } from 'lucide-react'

interface TeamMemberStats {
  id: string
  name: string
  hoursLogged: number
  hoursPlanned: number
}

interface TeamLeaderboardCardProps {
  members: TeamMemberStats[]
  className?: string
}

/**
 * Calcule le pourcentage de progression (heures loguées / heures planifiées)
 */
function calculateProgress(logged: number, planned: number): number {
  if (planned === 0) return 0
  return Math.round((logged / planned) * 100)
}

/**
 * Retourne l'emoji de médaille pour le top 3
 */
function getMedalEmoji(rank: number): string | null {
  switch (rank) {
    case 1:
      return '🥇'
    case 2:
      return '🥈'
    case 3:
      return '🥉'
    default:
      return null
  }
}

/**
 * Retourne la couleur de la barre de progression selon le pourcentage
 */
function getProgressColor(percentage: number): string {
  if (percentage >= 100) return 'bg-green-500'
  if (percentage >= 80) return 'bg-green-400'
  if (percentage >= 50) return 'bg-orange-400'
  return 'bg-gray-300'
}

/**
 * Retourne la couleur du texte selon le pourcentage
 */
function getTextColor(percentage: number): string {
  if (percentage >= 100) return 'text-green-700'
  if (percentage >= 80) return 'text-green-600'
  if (percentage >= 50) return 'text-orange-600'
  return 'text-gray-600'
}

function TeamLeaderboardCard({ members, className = '' }: TeamLeaderboardCardProps) {
  // Trier les membres par pourcentage décroissant
  const sortedMembers = [...members]
    .map((member) => ({
      ...member,
      percentage: calculateProgress(member.hoursLogged, member.hoursPlanned),
    }))
    .sort((a, b) => b.percentage - a.percentage)

  // Limiter à 5 membres visibles, scrollable si plus
  const hasMoreThan5 = sortedMembers.length > 5

  return (
    <div className={`bg-white rounded-2xl p-5 shadow-lg border-2 border-gray-200 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-500" />
          Classement équipe
        </h3>
        <TrendingUp className="w-5 h-5 text-blue-600" />
      </div>

      {sortedMembers.length === 0 ? (
        <div className="text-center py-8">
          <Trophy className="w-12 h-12 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">Aucune donnée disponible</p>
        </div>
      ) : (
        <div
          className={`space-y-3 ${hasMoreThan5 ? 'max-h-[320px] overflow-y-auto pr-2 scrollbar-thin' : ''}`}
          style={{ scrollbarWidth: 'thin' }}
        >
          {sortedMembers.map((member, index) => {
            const rank = index + 1
            const medal = getMedalEmoji(rank)
            const progressColor = getProgressColor(member.percentage)
            const textColor = getTextColor(member.percentage)

            return (
              <div
                key={member.id}
                className={`
                  p-3 rounded-xl border transition-all
                  ${rank <= 3 ? 'bg-gradient-to-r from-yellow-50 to-white border-yellow-200' : 'bg-gray-50 border-gray-200'}
                `}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className="text-lg font-bold text-gray-400 w-6 shrink-0">
                      #{rank}
                    </span>
                    {medal && <span className="text-xl shrink-0">{medal}</span>}
                    <span className="font-medium text-gray-800 truncate">
                      {member.name}
                    </span>
                  </div>
                  <span className={`font-bold text-sm ${textColor} shrink-0 ml-2`}>
                    {member.percentage}%
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                  <span>
                    {member.hoursLogged.toFixed(1)}h / {member.hoursPlanned.toFixed(1)}h
                  </span>
                </div>

                {/* Barre de progression */}
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${progressColor} rounded-full transition-all duration-500 ease-out`}
                    style={{ width: `${Math.min(member.percentage, 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Footer avec indication de semaine */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Classement de la semaine en cours
        </p>
      </div>
    </div>
  )
}

export default memo(TeamLeaderboardCard)
