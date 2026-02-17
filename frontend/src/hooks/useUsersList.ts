/**
 * useUsersList - Hook pour la gestion de la liste des utilisateurs.
 *
 * Extrait de UsersListPage la logique metier:
 * - Chargement des statistiques par role
 * - Fonction de listing paginee (pour useListPage)
 * - Creation d'un utilisateur
 * - Invitation d'un utilisateur par email
 * - Activation/desactivation d'un utilisateur
 */

import { useState, useEffect, useCallback } from 'react'
import { usersService } from '../services/users'
import { authService } from '../services/auth'
import { logger } from '../services/logger'
import type { User, UserCreate, UserRole, PaginatedResponse } from '../types'

interface ListParams {
  page?: number
  size?: number
  search?: string
  role?: UserRole
  is_active?: boolean
  [key: string]: unknown
}

interface UseUsersListReturn {
  roleStats: Record<UserRole, number>
  loadRoleStats: () => Promise<void>
  fetchUsers: (params: ListParams) => Promise<PaginatedResponse<User>>
  handleCreateUser: (data: UserCreate) => Promise<void>
  handleInviteUser: (data: { email: string; nom: string; prenom: string; role: string }) => Promise<void>
  handleToggleActive: (user: User) => Promise<void>
}

interface UseUsersListOptions {
  addToast: (toast: { message: string; type: 'success' | 'error' | 'info' | 'warning' }) => void
}

export function useUsersList({ addToast }: UseUsersListOptions): UseUsersListReturn {
  const [roleStats, setRoleStats] = useState<Record<UserRole, number>>({
    admin: 0,
    conducteur: 0,
    chef_chantier: 0,
    compagnon: 0,
  })

  const fetchUsers = useCallback((params: ListParams): Promise<PaginatedResponse<User>> => {
    return usersService.list({
      page: params.page,
      size: params.size,
      search: params.search,
      role: params.role as UserRole | undefined,
      is_active: params.is_active as boolean | undefined,
    })
  }, [])

  const loadRoleStats = useCallback(async () => {
    try {
      const allUsers = await usersService.list({ size: 100 })
      const stats: Record<UserRole, number> = {
        admin: 0,
        conducteur: 0,
        chef_chantier: 0,
        compagnon: 0,
      }
      allUsers.items.forEach(u => {
        if (u.role in stats) {
          stats[u.role]++
        }
      })
      setRoleStats(stats)
    } catch (error) {
      logger.error('Error loading role stats', error, { context: 'useUsersList' })
    }
  }, [])

  useEffect(() => {
    loadRoleStats()
  }, [loadRoleStats])

  const handleCreateUser = useCallback(async (data: UserCreate) => {
    try {
      await usersService.create(data)
      addToast({ message: 'Utilisateur créé avec succès', type: 'success' })
      loadRoleStats()
    } catch (error) {
      logger.error('Error creating user', error, { context: 'useUsersList' })
      throw error
    }
  }, [addToast, loadRoleStats])

  const handleInviteUser = useCallback(async (data: { email: string; nom: string; prenom: string; role: string }) => {
    try {
      await authService.inviteUser(data)
      addToast({ message: `Invitation envoyée à ${data.email}`, type: 'success' })
      loadRoleStats()
    } catch (error) {
      logger.error('Error inviting user', error, { context: 'useUsersList', showToast: true })
      throw error
    }
  }, [addToast, loadRoleStats])

  const handleToggleActive = useCallback(async (user: User) => {
    try {
      if (user.is_active) {
        await usersService.deactivate(user.id)
      } else {
        await usersService.activate(user.id)
      }
      loadRoleStats()
    } catch (error) {
      logger.error('Erreur lors du changement de statut', error, { context: 'useUsersList', showToast: true })
    }
  }, [loadRoleStats])

  return {
    roleStats,
    loadRoleStats,
    fetchUsers,
    handleCreateUser,
    handleInviteUser,
    handleToggleActive,
  }
}

export default useUsersList
