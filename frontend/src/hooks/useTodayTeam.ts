/**
 * useTodayTeam - Hook pour charger l'équipe du jour depuis les affectations du planning
 * Affiche les personnes assignées aux mêmes chantiers que l'utilisateur connecté
 * Groupé par chantier pour permettre la synchro avec le planning en cours
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { planningService } from '../services/planning'
import { logger } from '../services/logger'

export interface TeamMember {
  id: string
  firstName: string
  lastName: string
  role: string
  color: string
  phone?: string
  chantierId?: string
  chantierName?: string
}

export interface ChantierTeam {
  chantierId: string
  chantierName: string
  members: TeamMember[]
}

export interface UseTodayTeamReturn {
  members: TeamMember[]
  /** Équipes groupées par chantier */
  teams: ChantierTeam[]
  /** Équipe filtrée pour un chantier donné */
  getTeamForChantier: (chantierId: string) => TeamMember[]
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
}

/** Couleurs par défaut pour les rôles */
const ROLE_COLORS: Record<string, string> = {
  admin: '#dc2626',       // red-600
  conducteur: '#2563eb',  // blue-600
  chef_chantier: '#16a34a', // green-600
  ouvrier: '#f97316',     // orange-500
  interimaire: '#8b5cf6', // violet-500
  sous_traitant: '#06b6d4', // cyan-500
}

/** Labels des rôles en français */
const ROLE_LABELS: Record<string, string> = {
  admin: 'Direction',
  conducteur: 'Conducteur de travaux',
  chef_chantier: 'Chef de chantier',
  ouvrier: 'Ouvrier',
  interimaire: 'Interimaire',
  sous_traitant: 'Sous-traitant',
}

function sortMembers(members: TeamMember[]): TeamMember[] {
  const roleOrder: Record<string, number> = {
    'Direction': 0,
    'Conducteur de travaux': 1,
    'Chef de chantier': 2,
    'Ouvrier': 3,
    'Interimaire': 4,
    'Sous-traitant': 5,
  }
  return [...members].sort((a, b) => {
    const orderA = roleOrder[a.role] ?? 99
    const orderB = roleOrder[b.role] ?? 99
    if (orderA !== orderB) return orderA - orderB
    return a.lastName.localeCompare(b.lastName)
  })
}

export function useTodayTeam(): UseTodayTeamReturn {
  const { user } = useAuth()
  const [allMembers, setAllMembers] = useState<TeamMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadTodayTeam = useCallback(async () => {
    if (!user?.id) {
      setAllMembers([])
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const today = new Date().toISOString().split('T')[0]

      // 1. Charger les affectations de l'utilisateur pour aujourd'hui
      const userAffectations = await planningService.getByUtilisateur(user.id, today, today)
      const userChantierIds = userAffectations.map(a => a.chantier_id)

      // Si l'utilisateur n'a pas d'affectation personnelle et est admin/conducteur,
      // charger toutes les affectations du jour
      let allAffectations = userAffectations
      if (userAffectations.length === 0 && (user.role === 'admin' || user.role === 'conducteur')) {
        allAffectations = await planningService.getAffectations({
          date_debut: today,
          date_fin: today,
        })
      } else if (userChantierIds.length > 0) {
        // 2. Charger toutes les affectations des mêmes chantiers
        allAffectations = await planningService.getAffectations({
          date_debut: today,
          date_fin: today,
        })
        // Filtrer pour ne garder que les affectations des mêmes chantiers
        allAffectations = allAffectations.filter(a => userChantierIds.includes(a.chantier_id))
      }

      // 3. Extraire les utilisateurs avec leur chantier
      const teamMembers: TeamMember[] = []
      // Dédupliquer par couple (utilisateur_id, chantier_id)
      const seen = new Set<string>()

      for (const affectation of allAffectations) {
        if (affectation.utilisateur_id === user.id) continue
        const key = `${affectation.utilisateur_id}-${affectation.chantier_id}`
        if (seen.has(key)) continue
        seen.add(key)

        const fullName = affectation.utilisateur_nom || 'Utilisateur'
        const nameParts = fullName.split(' ')
        const prenom = nameParts[0] || 'Utilisateur'
        const nom = nameParts.slice(1).join(' ') || ''
        const role = affectation.utilisateur_role || 'ouvrier'

        teamMembers.push({
          id: affectation.utilisateur_id,
          firstName: prenom,
          lastName: nom,
          role: ROLE_LABELS[role] || role,
          color: affectation.utilisateur_couleur || ROLE_COLORS[role] || '#6b7280',
          phone: undefined,
          chantierId: affectation.chantier_id,
          chantierName: affectation.chantier_nom || 'Chantier',
        })
      }

      setAllMembers(sortMembers(teamMembers))
    } catch (err) {
      logger.error('Erreur chargement équipe du jour', err)
      setError('Impossible de charger l\'équipe')
    } finally {
      setIsLoading(false)
    }
  }, [user?.id, user?.role])

  useEffect(() => {
    loadTodayTeam()
  }, [loadTodayTeam])

  // Grouper par chantier
  const teams = useMemo<ChantierTeam[]>(() => {
    const map = new Map<string, ChantierTeam>()
    for (const m of allMembers) {
      if (!m.chantierId) continue
      if (!map.has(m.chantierId)) {
        map.set(m.chantierId, {
          chantierId: m.chantierId,
          chantierName: m.chantierName || 'Chantier',
          members: [],
        })
      }
      map.get(m.chantierId)!.members.push(m)
    }
    return Array.from(map.values())
  }, [allMembers])

  // Dédupliquer les membres pour la vue "tous" (un membre sur plusieurs chantiers = une seule entrée)
  const uniqueMembers = useMemo(() => {
    const seen = new Set<string>()
    return allMembers.filter(m => {
      if (seen.has(m.id)) return false
      seen.add(m.id)
      return true
    })
  }, [allMembers])

  const getTeamForChantier = useCallback((chantierId: string) => {
    return allMembers.filter(m => m.chantierId === chantierId)
  }, [allMembers])

  return {
    members: uniqueMembers,
    teams,
    getTeamForChantier,
    isLoading,
    error,
    refresh: loadTodayTeam,
  }
}
