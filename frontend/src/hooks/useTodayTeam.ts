/**
 * useTodayTeam - Hook pour charger l'équipe du jour depuis les affectations du planning
 * Affiche les personnes assignées aux mêmes chantiers que l'utilisateur connecté
 */

import { useState, useEffect, useCallback } from 'react'
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
}

export interface UseTodayTeamReturn {
  members: TeamMember[]
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

export function useTodayTeam(): UseTodayTeamReturn {
  const { user } = useAuth()
  const [members, setMembers] = useState<TeamMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadTodayTeam = useCallback(async () => {
    if (!user?.id) {
      setMembers([])
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

      // 3. Extraire les utilisateurs uniques (exclure l'utilisateur connecté)
      const seenUserIds = new Set<string>()
      const teamMembers: TeamMember[] = []

      for (const affectation of allAffectations) {
        if (affectation.utilisateur_id === user.id) continue // Exclure soi-même
        if (seenUserIds.has(affectation.utilisateur_id)) continue // Éviter les doublons
        seenUserIds.add(affectation.utilisateur_id)

        // Utiliser les infos disponibles dans l'affectation
        // utilisateur_nom contient le nom complet "Prenom Nom"
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
          // Note: utilisateur_telephone n'est pas dans l'interface Affectation actuelle
          phone: undefined,
        })
      }

      // Trier par rôle (chef de chantier en premier, puis alphabétique)
      teamMembers.sort((a, b) => {
        // Priorité des rôles
        const roleOrder: Record<string, number> = {
          'Direction': 0,
          'Conducteur de travaux': 1,
          'Chef de chantier': 2,
          'Ouvrier': 3,
          'Interimaire': 4,
          'Sous-traitant': 5,
        }
        const orderA = roleOrder[a.role] ?? 99
        const orderB = roleOrder[b.role] ?? 99
        if (orderA !== orderB) return orderA - orderB
        // Puis alphabétique
        return a.lastName.localeCompare(b.lastName)
      })

      setMembers(teamMembers)
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

  return {
    members,
    isLoading,
    error,
    refresh: loadTodayTeam,
  }
}
