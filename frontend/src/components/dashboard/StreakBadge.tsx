/**
 * StreakBadge - Badge affichant le nombre de jours consecutifs de pointage
 * CDC Section 5.4.1 - Gamification legere
 *
 * Niveaux visuels:
 * - 5-9 jours: badge dore
 * - 10-19 jours: badge dore avec animation pulse
 * - 20+ jours: badge platine
 */

import { Flame } from 'lucide-react'

interface StreakBadgeProps {
  /** Nombre de jours consecutifs */
  streak: number
}

export default function StreakBadge({ streak }: StreakBadgeProps) {
  // Ne rien afficher si pas de streak
  if (streak === 0) return null

  // Determiner le style selon le niveau
  const getBadgeStyle = () => {
    if (streak >= 20) {
      // Platine: gradient argente brillant
      return {
        gradient: 'from-gray-300 via-gray-100 to-gray-300',
        text: 'text-gray-800',
        icon: 'text-gray-800',
        border: 'border-gray-400',
        pulse: false,
      }
    }
    if (streak >= 10) {
      // Dore avec animation pulse
      return {
        gradient: 'from-yellow-400 via-yellow-300 to-yellow-400',
        text: 'text-yellow-900',
        icon: 'text-yellow-900',
        border: 'border-yellow-500',
        pulse: true,
      }
    }
    if (streak >= 5) {
      // Dore simple
      return {
        gradient: 'from-yellow-400 via-yellow-300 to-yellow-400',
        text: 'text-yellow-900',
        icon: 'text-yellow-900',
        border: 'border-yellow-500',
        pulse: false,
      }
    }

    // 1-4 jours: orange simple (encouragement)
    return {
      gradient: 'from-orange-400 to-orange-500',
      text: 'text-white',
      icon: 'text-white',
      border: 'border-orange-600',
      pulse: false,
    }
  }

  const style = getBadgeStyle()

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full
        bg-gradient-to-r ${style.gradient}
        border-2 ${style.border}
        shadow-md
        ${style.pulse ? 'animate-pulse' : ''}
      `}
      title={`${streak} jour${streak > 1 ? 's' : ''} consecutif${streak > 1 ? 's' : ''} de pointage`}
    >
      <Flame className={`w-4 h-4 ${style.icon}`} />
      <span className={`font-bold text-sm ${style.text}`}>
        {streak} jour{streak > 1 ? 's' : ''}
      </span>
    </div>
  )
}
