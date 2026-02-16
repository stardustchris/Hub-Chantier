/**
 * Hook pour calculer le streak de pointage (jours consecutifs)
 * CDC Section 5.4.1 - Gamification legere
 *
 * Calcule le nombre de jours ouvres consecutifs (lundi-vendredi)
 * ou l'utilisateur a pointe.
 *
 * Source de donnees: localStorage 'hub_pointage_history' (tableau de dates ISO)
 */

import { useEffect, useState, useCallback } from 'react'

const POINTAGE_HISTORY_KEY = 'hub_pointage_history'

/**
 * Verifie si une date est un jour ouvre (lundi-vendredi)
 */
function isWeekday(date: Date): boolean {
  const day = date.getDay()
  return day >= 1 && day <= 5 // 1=lundi, 5=vendredi
}

/**
 * Normalise une date au format YYYY-MM-DD (sans heure)
 */
function normalizeDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Retourne la date du jour ouvre precedent (excluant weekends)
 */
function getPreviousWeekday(date: Date): Date {
  const previous = new Date(date)
  previous.setDate(previous.getDate() - 1)

  // Si c'est dimanche (0), reculer de 2 jours pour atteindre vendredi
  if (previous.getDay() === 0) {
    previous.setDate(previous.getDate() - 2)
  }
  // Si c'est samedi (6), reculer de 1 jour pour atteindre vendredi
  else if (previous.getDay() === 6) {
    previous.setDate(previous.getDate() - 1)
  }

  return previous
}

/**
 * Calcule le streak de pointage depuis l'historique
 * Retourne le nombre de jours ouvres consecutifs
 */
function calculateStreak(history: string[]): number {
  if (history.length === 0) return 0

  // Trier les dates par ordre decroissant (plus recent en premier)
  const sortedDates = [...new Set(history)].sort((a, b) => b.localeCompare(a))

  const today = new Date()
  const todayNormalized = normalizeDate(today)

  // Si l'utilisateur n'a pas pointe aujourd'hui ET qu'on est un jour ouvre,
  // verifier s'il a pointe hier (pour continuer le streak)
  let currentDate: Date
  if (!sortedDates.includes(todayNormalized)) {
    // Si aujourd'hui est un jour ouvre et qu'il n'a pas pointe, streak = 0
    if (isWeekday(today)) {
      return 0
    }
    // Si c'est le weekend, commencer a verifier depuis le dernier jour ouvre
    currentDate = getPreviousWeekday(today)
  } else {
    // Commencer depuis aujourd'hui
    currentDate = today
  }

  let streak = 0

  // Remonter dans l'historique en comptant les jours consecutifs
  while (true) {
    const dateStr = normalizeDate(currentDate)

    // Si ce jour ouvre est dans l'historique, incrementer le streak
    if (sortedDates.includes(dateStr)) {
      streak++
    } else {
      // Streak casse
      break
    }

    // Passer au jour ouvre precedent
    currentDate = getPreviousWeekday(currentDate)

    // Limite de securite pour eviter les boucles infinies (1 an max)
    if (streak > 260) break
  }

  return streak
}

export interface UsePointageStreakReturn {
  /** Nombre de jours ouvres consecutifs de pointage */
  streak: number
  /** Ajouter la date du jour a l'historique (appele lors du clock-in) */
  recordToday: () => void
  /** Historique des dates de pointage */
  history: string[]
}

/**
 * Hook pour gerer le streak de pointage
 */
export function usePointageStreak(): UsePointageStreakReturn {
  const [history, setHistory] = useState<string[]>([])
  const [streak, setStreak] = useState(0)

  // Charger l'historique depuis localStorage au montage
  useEffect(() => {
    loadHistory()
  }, [])

  // Recalculer le streak quand l'historique change
  useEffect(() => {
    const newStreak = calculateStreak(history)
    setStreak(newStreak)
  }, [history])

  /**
   * Charge l'historique depuis localStorage
   */
  const loadHistory = () => {
    try {
      const stored = localStorage.getItem(POINTAGE_HISTORY_KEY)
      if (!stored) {
        setHistory([])
        return
      }

      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed)) {
        setHistory(parsed)
      } else {
        setHistory([])
      }
    } catch {
      // En cas d'erreur de parsing, reinitialiser
      localStorage.removeItem(POINTAGE_HISTORY_KEY)
      setHistory([])
    }
  }

  /**
   * Enregistre la date du jour dans l'historique (appele lors du clock-in)
   */
  const recordToday = useCallback(() => {
    const today = normalizeDate(new Date())

    setHistory((prev) => {
      // Eviter les doublons
      if (prev.includes(today)) return prev

      const updated = [...prev, today]

      // Sauvegarder dans localStorage
      try {
        localStorage.setItem(POINTAGE_HISTORY_KEY, JSON.stringify(updated))
      } catch {
        // Silently fail si localStorage non disponible
      }

      return updated
    })
  }, [])

  return {
    streak,
    recordToday,
    history,
  }
}
