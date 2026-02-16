/**
 * WeeklyProgressCard - Carte de progression hebdomadaire
 * CDC Section 5.4.2 - Gamification legere
 *
 * Affiche les heures loguees cette semaine vs objectif
 * avec barre de progression et code couleur
 */

import { Clock, TrendingUp } from 'lucide-react'
import { useEffect, useState } from 'react'

const WEEKLY_HOURS_KEY = 'hub_weekly_hours'
const WEEKLY_GOAL_KEY = 'hub_weekly_goal'
const DEFAULT_GOAL = 35

interface WeeklyProgressCardProps {
  /** Heures travaillees cette semaine (optionnel, sinon charge depuis localStorage) */
  hoursWorked?: number
  /** Objectif hebdomadaire en heures (par defaut 35h) */
  weeklyGoal?: number
}

/**
 * Parse une duree au format "HH:MM" ou "XXhYY" en heures decimales
 */
function parseHoursToDecimal(hoursStr: string): number {
  // Format "HH:MM"
  if (hoursStr.includes(':')) {
    const [hours, minutes] = hoursStr.split(':').map(Number)
    return hours + minutes / 60
  }

  // Format "XXhYY"
  if (hoursStr.includes('h')) {
    const [hours, minutes] = hoursStr.split('h').map(Number)
    return hours + (minutes || 0) / 60
  }

  // Format decimal
  return parseFloat(hoursStr) || 0
}

export default function WeeklyProgressCard({
  hoursWorked,
  weeklyGoal,
}: WeeklyProgressCardProps) {
  const [hours, setHours] = useState(0)
  const [goal, setGoal] = useState(DEFAULT_GOAL)

  // Charger les donnees depuis localStorage au montage
  useEffect(() => {
    loadWeeklyData()
  }, [])

  // Utiliser les props si fournies
  useEffect(() => {
    if (hoursWorked !== undefined) {
      setHours(hoursWorked)
    }
  }, [hoursWorked])

  useEffect(() => {
    if (weeklyGoal !== undefined) {
      setGoal(weeklyGoal)
    }
  }, [weeklyGoal])

  /**
   * Charge les donnees depuis localStorage
   */
  const loadWeeklyData = () => {
    try {
      // Charger les heures travaillees
      const storedHours = localStorage.getItem(WEEKLY_HOURS_KEY)
      if (storedHours) {
        const parsed = parseHoursToDecimal(storedHours)
        setHours(parsed)
      }

      // Charger l'objectif personnalise
      const storedGoal = localStorage.getItem(WEEKLY_GOAL_KEY)
      if (storedGoal) {
        const parsed = parseInt(storedGoal, 10)
        if (!isNaN(parsed) && parsed > 0) {
          setGoal(parsed)
        }
      }
    } catch {
      // En cas d'erreur, garder les valeurs par defaut
    }
  }

  // Calculer le pourcentage de progression
  const progress = Math.min((hours / goal) * 100, 100)

  // Determiner la couleur selon le pourcentage
  const getProgressColor = () => {
    if (progress >= 80) return 'bg-green-500' // Vert: objectif atteint ou presque
    if (progress >= 50) return 'bg-orange-500' // Orange: a mi-parcours
    return 'bg-red-500' // Rouge: en retard
  }

  const getTextColor = () => {
    if (progress >= 80) return 'text-green-700'
    if (progress >= 50) return 'text-orange-700'
    return 'text-red-700'
  }

  // Formater les heures pour l'affichage
  const formatHours = (h: number): string => {
    return `${Math.floor(h)}h${String(Math.round((h % 1) * 60)).padStart(2, '0')}`
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg border-2 border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-600" />
          Progression hebdomadaire
        </h3>
        {progress >= 80 && (
          <TrendingUp className="w-5 h-5 text-green-600" />
        )}
      </div>

      {/* Barre de progression circulaire (ou lineaire pour simplicite) */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <span className={`text-2xl font-bold ${getTextColor()}`}>
            {formatHours(hours)}
          </span>
          <span className="text-sm text-gray-600">
            / {formatHours(goal)}
          </span>
        </div>

        {/* Barre de progression lineaire */}
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${getProgressColor()} rounded-full transition-all duration-500 ease-out`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Message d'encouragement */}
      <p className="text-xs text-gray-600 text-center">
        {progress >= 100 ? (
          <span className="text-green-700 font-semibold">
            Objectif atteint ! Excellent travail
          </span>
        ) : progress >= 80 ? (
          <span className="text-green-700">
            Plus que {formatHours(goal - hours)} pour atteindre l'objectif
          </span>
        ) : progress >= 50 ? (
          <span className="text-orange-700">
            Vous etes a mi-parcours, continuez&nbsp;!
          </span>
        ) : (
          <span className="text-gray-600">
            Encore {formatHours(goal - hours)} a faire cette semaine
          </span>
        )}
      </p>
    </div>
  )
}
