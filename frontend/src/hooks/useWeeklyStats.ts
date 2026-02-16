/**
 * Hook pour récupérer les statistiques de travail de l'utilisateur
 * - Heures travaillées (semaine en cours)
 * - Jours travaillés (mois en cours)
 * - Congés pris / total annuel (en jours)
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { pointagesService } from '../services/pointages'
import { tachesService } from '../services/taches'
import { planningService } from '../services/planning'
import { logger } from '../services/logger'

interface WorkStats {
  // Semaine en cours
  hoursWorked: string
  hoursWorkedDecimal: number
  hoursProgress: number
  // Mois en cours
  joursTravailesMois: number
  joursTotalMois: number
  // Congés annuels
  congesPris: number
  congesTotal: number
  // Tâches (pour QuickActions badge)
  tasksCompleted: number
  tasksTotal: number
  isLoading: boolean
}

// Heures de travail hebdomadaires standard (35h en France)
const WEEKLY_HOURS_TARGET = 35
// Congés annuels standard BTP
const CONGES_ANNUELS_TOTAL = 25

// Noms de chantiers spéciaux (congés/absences)
const CONGES_NOMS = ['conges payes', 'rtt', 'absence', 'congés payés']

function isCongeChantier(chantierNom: string | undefined | null): boolean {
  if (!chantierNom) return false
  const lower = chantierNom.toLowerCase()
  return CONGES_NOMS.some(n => lower.includes(n))
}

function getWeekBounds(): { start: string; end: string } {
  const now = new Date()
  const dayOfWeek = now.getDay()
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

function getMonthBounds(): { start: string; end: string } {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), 1)
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  }
}

function getYearBounds(): { start: string; end: string } {
  const now = new Date()
  return {
    start: `${now.getFullYear()}-01-01`,
    end: `${now.getFullYear()}-12-31`,
  }
}

function formatHours(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h${minutes.toString().padStart(2, '0')}`
}

function getJoursOuvresMois(): number {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const lastDay = new Date(year, month + 1, 0).getDate()
  let count = 0
  for (let d = 1; d <= lastDay; d++) {
    const day = new Date(year, month, d).getDay()
    if (day !== 0 && day !== 6) count++
  }
  return count
}

export function useWeeklyStats(): WorkStats {
  const { user } = useAuth()
  const [stats, setStats] = useState<WorkStats>({
    hoursWorked: '0h00',
    hoursWorkedDecimal: 0,
    hoursProgress: 0,
    joursTravailesMois: 0,
    joursTotalMois: getJoursOuvresMois(),
    congesPris: 0,
    congesTotal: CONGES_ANNUELS_TOTAL,
    tasksCompleted: 0,
    tasksTotal: 0,
    isLoading: true,
  })

  const loadStats = useCallback(async () => {
    if (!user?.id) return

    try {
      const userId = parseInt(user.id, 10)
      const weekBounds = getWeekBounds()
      const monthBounds = getMonthBounds()
      const yearBounds = getYearBounds()

      // 1. Heures travaillées cette semaine
      const weekPointages = await pointagesService.list({
        utilisateur_id: userId,
        date_debut: weekBounds.start,
        date_fin: weekBounds.end,
      })

      let totalMinutes = 0
      for (const pointage of weekPointages.items) {
        if (pointage.total_heures_decimal) {
          totalMinutes += Math.round(pointage.total_heures_decimal * 60)
        }
      }

      const hoursWorked = formatHours(totalMinutes)
      const hoursWorkedDecimal = totalMinutes / 60
      const hoursProgress = Math.min(100, Math.round((totalMinutes / (WEEKLY_HOURS_TARGET * 60)) * 100))

      // 2. Jours travaillés ce mois (dates uniques hors congés)
      const monthPointages = await pointagesService.list({
        utilisateur_id: userId,
        date_debut: monthBounds.start,
        date_fin: monthBounds.end,
        page_size: 100,
      })

      const datesTravailleurs = new Set<string>()
      for (const p of monthPointages.items) {
        if (!isCongeChantier(p.chantier_nom)) {
          datesTravailleurs.add(p.date_pointage)
        }
      }
      const joursTravailesMois = datesTravailleurs.size

      // 3. Congés pris cette année (pointages sur chantiers congé/RTT)
      const yearPointages = await pointagesService.list({
        utilisateur_id: userId,
        date_debut: yearBounds.start,
        date_fin: yearBounds.end,
        page_size: 100,
      })

      let congesMinutes = 0
      for (const p of yearPointages.items) {
        if (isCongeChantier(p.chantier_nom)) {
          if (p.total_heures_decimal) {
            congesMinutes += Math.round(p.total_heures_decimal * 60)
          }
        }
      }
      // 1 jour = 7h = 420 min, arrondi au 0.5 jour
      const congesPris = Math.round((congesMinutes / 420) * 2) / 2

      // 4. Tâches (pour badge QuickActions)
      let tasksCompleted = 0
      let tasksTotal = 0
      try {
        const affectations = await planningService.getByUtilisateur(user.id, weekBounds.start, weekBounds.end)
        const chantierIds = [...new Set(affectations.map(a => parseInt(a.chantier_id, 10)))]
        for (const chantierId of chantierIds) {
          try {
            const tachesResponse = await tachesService.listByChantier(chantierId, {
              size: 100,
              include_sous_taches: false,
            })
            for (const tache of tachesResponse.items) {
              tasksTotal++
              if (tache.statut === 'termine') {
                tasksCompleted++
              }
            }
          } catch {
            // Ignorer les erreurs de chargement de tâches
          }
        }
      } catch (error) {
        logger.warn('Could not load tasks stats', { error })
      }

      setStats({
        hoursWorked,
        hoursWorkedDecimal,
        hoursProgress,
        joursTravailesMois,
        joursTotalMois: getJoursOuvresMois(),
        congesPris,
        congesTotal: CONGES_ANNUELS_TOTAL,
        tasksCompleted,
        tasksTotal,
        isLoading: false,
      })
    } catch (error) {
      logger.error('Error loading work stats', error)
      setStats(prev => ({ ...prev, isLoading: false }))
    }
  }, [user?.id])

  useEffect(() => {
    loadStats()
  }, [loadStats])

  return stats
}
