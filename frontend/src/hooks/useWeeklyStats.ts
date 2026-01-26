/**
 * Hook pour récupérer les statistiques hebdomadaires de l'utilisateur
 * - Heures travaillées (depuis les pointages)
 * - Tâches terminées (depuis les tâches assignées)
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { pointagesService } from '../services/pointages'
import { tachesService } from '../services/taches'
import { planningService } from '../services/planning'
import { logger } from '../services/logger'

interface WeeklyStats {
  hoursWorked: string
  hoursProgress: number
  tasksCompleted: number
  tasksTotal: number
  isLoading: boolean
}

// Heures de travail hebdomadaires standard (35h en France)
const WEEKLY_HOURS_TARGET = 35

function getWeekBounds(): { start: string; end: string } {
  const now = new Date()
  const dayOfWeek = now.getDay()
  // Lundi = 1, donc on recule de (dayOfWeek - 1) jours, ou 6 si dimanche
  const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1

  const monday = new Date(now)
  monday.setDate(now.getDate() - daysToMonday)
  monday.setHours(0, 0, 0, 0)

  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)

  return {
    start: monday.toISOString().split('T')[0],
    end: sunday.toISOString().split('T')[0],
  }
}

function formatHours(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h${minutes.toString().padStart(2, '0')}`
}

export function useWeeklyStats(): WeeklyStats {
  const { user } = useAuth()
  const [stats, setStats] = useState<WeeklyStats>({
    hoursWorked: '0h00',
    hoursProgress: 0,
    tasksCompleted: 0,
    tasksTotal: 0,
    isLoading: true,
  })

  const loadStats = useCallback(async () => {
    if (!user?.id) return

    try {
      const { start, end } = getWeekBounds()
      const userId = parseInt(user.id, 10)

      // Charger les pointages de la semaine pour l'utilisateur
      const pointagesResponse = await pointagesService.list({
        utilisateur_id: userId,
        date_debut: start,
        date_fin: end,
      })

      // Calculer le total des heures
      let totalMinutes = 0
      for (const pointage of pointagesResponse.items) {
        // total_heures_decimal est en heures décimales (ex: 8.5 = 8h30)
        if (pointage.total_heures_decimal) {
          totalMinutes += Math.round(pointage.total_heures_decimal * 60)
        }
      }

      const hoursWorked = formatHours(totalMinutes)
      const hoursProgress = Math.min(100, Math.round((totalMinutes / (WEEKLY_HOURS_TARGET * 60)) * 100))

      // Charger les tâches assignées à l'utilisateur via les affectations
      let tasksCompleted = 0
      let tasksTotal = 0

      try {
        // Récupérer les affectations de l'utilisateur pour la semaine
        const affectations = await planningService.getByUtilisateur(user.id, start, end)

        // Pour chaque chantier unique, récupérer les tâches
        const chantierIds = [...new Set(affectations.map(a => parseInt(a.chantier_id, 10)))]

        for (const chantierId of chantierIds) {
          try {
            const tachesResponse = await tachesService.listByChantier(chantierId, {
              size: 100,
              include_sous_taches: false,
            })

            // Compter les tâches terminées vs total
            for (const tache of tachesResponse.items) {
              tasksTotal++
              if (tache.statut === 'termine' || tache.statut === 'valide') {
                tasksCompleted++
              }
            }
          } catch {
            // Ignorer les erreurs de chargement de tâches pour un chantier
          }
        }
      } catch (error) {
        logger.warn('Could not load tasks stats', { error })
      }

      setStats({
        hoursWorked,
        hoursProgress,
        tasksCompleted,
        tasksTotal,
        isLoading: false,
      })
    } catch (error) {
      logger.error('Error loading weekly stats', error)
      setStats(prev => ({ ...prev, isLoading: false }))
    }
  }, [user?.id])

  useEffect(() => {
    loadStats()
  }, [loadStats])

  return stats
}
