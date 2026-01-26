/**
 * Hook pour charger les données logistique d'un chantier
 * Affiche les réservations de matériel actives et à venir
 */

import { useState, useEffect, useCallback } from 'react'
import type { Reservation } from '../types/logistique'
import {
  initializeMockData,
  getTodayReservationsByChantier,
  getUpcomingReservationsByChantier,
} from '../services/logistiqueMockData'
import { logger } from '../services/logger'

interface ChantierLogistiqueStats {
  /** Nombre de réservations aujourd'hui */
  todayCount: number
  /** Nombre de réservations à venir (7 jours) */
  upcomingCount: number
  /** Nombre de réservations en attente de validation */
  pendingCount: number
}

interface UseChantierLogistiqueReturn {
  /** Réservations du jour */
  todayReservations: Reservation[]
  /** Réservations à venir (7 prochains jours) */
  upcomingReservations: Reservation[]
  /** Statistiques */
  stats: ChantierLogistiqueStats
  /** Chargement en cours */
  isLoading: boolean
  /** Erreur éventuelle */
  error: string | null
  /** Recharger les données */
  refresh: () => void
}

export function useChantierLogistique(chantierId: number | string): UseChantierLogistiqueReturn {
  const [todayReservations, setTodayReservations] = useState<Reservation[]>([])
  const [upcomingReservations, setUpcomingReservations] = useState<Reservation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const numericChantierId = typeof chantierId === 'string' ? parseInt(chantierId, 10) : chantierId

  const loadData = useCallback(() => {
    if (!numericChantierId || isNaN(numericChantierId)) {
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Initialiser les données mock si nécessaire
      initializeMockData()

      // Charger les réservations du jour
      const today = getTodayReservationsByChantier(numericChantierId)
      setTodayReservations(today)

      // Charger les réservations à venir
      const upcoming = getUpcomingReservationsByChantier(numericChantierId)
      setUpcomingReservations(upcoming)
    } catch (err) {
      logger.error('Error loading chantier logistique', err)
      setError('Impossible de charger les données logistique')
    } finally {
      setIsLoading(false)
    }
  }, [numericChantierId])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Calculer les stats
  const stats: ChantierLogistiqueStats = {
    todayCount: todayReservations.length,
    upcomingCount: upcomingReservations.length,
    pendingCount: upcomingReservations.filter((r) => r.statut === 'en_attente').length,
  }

  return {
    todayReservations,
    upcomingReservations,
    stats,
    isLoading,
    error,
    refresh: loadData,
  }
}
