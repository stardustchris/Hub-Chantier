/**
 * useTodayPlanning - Hook pour charger les affectations du jour de l'utilisateur connecté
 * Utilisé par TodayPlanningCard sur le Dashboard
 *
 * Comportement selon le rôle:
 * - Admin/Conducteur: Si pas d'affectation personnelle, affiche tous les chantiers du jour
 * - Chef de chantier/Compagnon: Affiche uniquement leurs propres affectations
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { planningService } from '../services/planning'
import { chantiersService } from '../services/chantiers'
import type { Affectation, Chantier } from '../types'
import { logger } from '../services/logger'

interface PlanningSlot {
  id: string
  chantierId?: string
  startTime: string
  endTime: string
  period: 'morning' | 'afternoon' | 'break'
  siteName?: string
  siteAddress?: string
  status?: 'in_progress' | 'planned' | 'completed'
  /** Statut réel du chantier (ouvert, en_cours, receptionne, ferme) */
  chantierStatut?: 'ouvert' | 'en_cours' | 'receptionne' | 'ferme'
  siteLatitude?: number
  siteLongitude?: number
  tasks?: { id: string; name: string; priority: 'urgent' | 'high' | 'medium' | 'low' }[]
  isPersonalAffectation?: boolean // true si l'utilisateur est personnellement affecté
  /** Chef de chantier principal */
  chefChantier?: {
    id: string
    prenom: string
    nom: string
    telephone?: string
  }
}

export interface UseTodayPlanningReturn {
  slots: PlanningSlot[]
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

/**
 * Détermine la période (matin/après-midi) selon l'heure
 */
function getPeriod(heureDebut: string): 'morning' | 'afternoon' {
  const hour = parseInt(heureDebut.split(':')[0], 10)
  return hour < 12 ? 'morning' : 'afternoon'
}

/**
 * Détermine le statut selon l'heure actuelle
 */
function getStatus(heureDebut: string, heureFin: string): 'in_progress' | 'planned' | 'completed' {
  const now = new Date()
  const currentMinutes = now.getHours() * 60 + now.getMinutes()

  const [startHour, startMin] = heureDebut.split(':').map(Number)
  const [endHour, endMin] = heureFin.split(':').map(Number)

  const startMinutes = startHour * 60 + startMin
  const endMinutes = endHour * 60 + endMin

  if (currentMinutes >= endMinutes) return 'completed'
  if (currentMinutes >= startMinutes) return 'in_progress'
  return 'planned'
}

/**
 * Convertit une affectation en slot de planning
 */
function affectationToSlot(
  affectation: Affectation,
  chantier?: Chantier,
  isPersonal = true
): PlanningSlot {
  const heureDebut = affectation.heure_debut || '08:00'
  const heureFin = affectation.heure_fin || '17:00'

  // Récupérer le premier chef de chantier s'il existe
  const chefChantier = chantier?.chefs?.[0]
    ? {
        id: chantier.chefs[0].id,
        prenom: chantier.chefs[0].prenom,
        nom: chantier.chefs[0].nom,
        telephone: chantier.chefs[0].telephone,
      }
    : undefined

  return {
    id: affectation.id,
    chantierId: affectation.chantier_id,
    startTime: heureDebut,
    endTime: heureFin,
    period: getPeriod(heureDebut),
    siteName: chantier?.nom || affectation.chantier_nom || 'Chantier inconnu',
    siteAddress: chantier?.adresse || '',
    siteLatitude: chantier?.latitude,
    siteLongitude: chantier?.longitude,
    status: getStatus(heureDebut, heureFin),
    chantierStatut: chantier?.statut, // Statut réel du chantier
    tasks: affectation.note
      ? [{ id: '1', name: affectation.note, priority: 'medium' as const }]
      : undefined,
    isPersonalAffectation: isPersonal,
    chefChantier,
  }
}

/**
 * Ajoute la pause déjeuner entre les slots matin et après-midi
 */
function addLunchBreak(slots: PlanningSlot[]): PlanningSlot[] {
  const morningSlots = slots.filter(s => s.period === 'morning')
  const afternoonSlots = slots.filter(s => s.period === 'afternoon')

  if (morningSlots.length > 0 && afternoonSlots.length > 0) {
    // Trouver l'heure de fin du dernier slot matin
    const lastMorningEnd = morningSlots.reduce((max, s) => {
      return s.endTime > max ? s.endTime : max
    }, '00:00')

    // Trouver l'heure de début du premier slot après-midi
    const firstAfternoonStart = afternoonSlots.reduce((min, s) => {
      return s.startTime < min ? s.startTime : min
    }, '23:59')

    // Ajouter pause déjeuner si il y a un écart
    if (lastMorningEnd < firstAfternoonStart) {
      const breakSlot: PlanningSlot = {
        id: 'break-lunch',
        startTime: lastMorningEnd,
        endTime: firstAfternoonStart,
        period: 'break',
      }
      return [...morningSlots, breakSlot, ...afternoonSlots]
    }
  }

  return slots
}

export function useTodayPlanning(): UseTodayPlanningReturn {
  const { user } = useAuth()
  const [affectations, setAffectations] = useState<Affectation[]>([])
  const [isPersonalView, setIsPersonalView] = useState(true) // true si affectations personnelles
  const [chantiers, setChantiers] = useState<Map<string, Chantier>>(new Map())
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Vérifier si l'utilisateur est admin ou conducteur (vue d'ensemble)
  const isAdminOrConducteur = user?.role === 'admin' || user?.role === 'conducteur'

  const loadTodayAffectations = useCallback(async () => {
    if (!user?.id) {
      setAffectations([])
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const today = new Date().toISOString().split('T')[0]

      // Charger les affectations de l'utilisateur pour aujourd'hui
      let todayAffectations = await planningService.getByUtilisateur(user.id, today, today)
      let personalView = true

      // Si admin/conducteur sans affectation personnelle, charger toutes les affectations du jour
      if (isAdminOrConducteur && todayAffectations.length === 0) {
        const allAffectations = await planningService.getAffectations({
          date_debut: today,
          date_fin: today,
        })

        // Dédupliquer par chantier (garder une seule entrée par chantier)
        const chantiersSeen = new Set<string>()
        todayAffectations = allAffectations.filter(a => {
          if (chantiersSeen.has(a.chantier_id)) return false
          chantiersSeen.add(a.chantier_id)
          return true
        })
        personalView = false // Ce sont des affectations d'équipe, pas personnelles
      }

      setAffectations(todayAffectations)
      setIsPersonalView(personalView)

      // Charger les détails des chantiers pour avoir les adresses
      const chantierIds = [...new Set(todayAffectations.map(a => a.chantier_id))]
      const chantiersMap = new Map<string, Chantier>()

      await Promise.all(
        chantierIds.map(async (id) => {
          try {
            const chantier = await chantiersService.getById(id)
            chantiersMap.set(id, chantier)
          } catch (err) {
            logger.warn('Chantier non trouvé', { chantierId: id })
          }
        })
      )

      setChantiers(chantiersMap)
    } catch (err) {
      logger.error('Erreur chargement planning du jour', err)
      setError('Impossible de charger votre planning')
    } finally {
      setIsLoading(false)
    }
  }, [user?.id, isAdminOrConducteur])

  useEffect(() => {
    loadTodayAffectations()
  }, [loadTodayAffectations])

  // Convertir les affectations en slots triés par heure
  const slots = useMemo(() => {
    if (affectations.length === 0) return []

    const rawSlots = affectations
      .map(a => affectationToSlot(a, chantiers.get(a.chantier_id), isPersonalView))
      .sort((a, b) => a.startTime.localeCompare(b.startTime))

    return addLunchBreak(rawSlots)
  }, [affectations, chantiers, isPersonalView])

  return {
    slots,
    isLoading,
    error,
    refresh: loadTodayAffectations,
  }
}
