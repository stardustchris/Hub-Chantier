/**
 * useUserDetail - Hook pour la gestion du detail d'un utilisateur.
 *
 * Extrait de UserDetailPage la logique metier:
 * - Chargement de l'utilisateur et de la navigation prev/next
 * - Mise a jour du profil (photo, informations)
 * - Activation/desactivation du compte
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usersService, NavigationIds } from '../services/users'
import { logger } from '../services/logger'
import type { User, UserUpdate } from '../types'

interface UseUserDetailReturn {
  user: User | null
  isLoading: boolean
  navIds: NavigationIds
  loadUser: () => Promise<void>
  handlePhotoUpload: (url: string) => Promise<void>
  handleUpdateUser: (data: UserUpdate) => Promise<void>
  handleToggleActive: () => Promise<void>
}

export function useUserDetail(userId: string): UseUserDetailReturn {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })

  const loadUser = async () => {
    try {
      setIsLoading(true)
      const data = await usersService.getById(userId)
      setUser(data)
    } catch (error) {
      logger.error('Error loading user', error, { context: 'useUserDetail' })
      navigate('/utilisateurs')
    } finally {
      setIsLoading(false)
    }
  }

  const loadNavigation = async () => {
    const ids = await usersService.getNavigationIds(userId)
    setNavIds(ids)
  }

  useEffect(() => {
    if (userId) {
      loadUser()
      loadNavigation()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId])

  const handlePhotoUpload = async (url: string) => {
    try {
      const updated = await usersService.update(userId, { photo_profil: url } as UserUpdate)
      setUser(updated)
    } catch (error) {
      logger.error('Erreur lors de la mise a jour de la photo', error, { context: 'useUserDetail', showToast: true })
    }
  }

  const handleUpdateUser = async (data: UserUpdate) => {
    try {
      const updated = await usersService.update(userId, data)
      setUser(updated)
    } catch (error) {
      logger.error('Erreur lors de la mise a jour', error, { context: 'useUserDetail', showToast: true })
    }
  }

  const handleToggleActive = async () => {
    if (!user) return

    try {
      let updated: User
      if (user.is_active) {
        updated = await usersService.deactivate(userId)
      } else {
        updated = await usersService.activate(userId)
      }
      setUser(updated)
    } catch (error) {
      logger.error('Erreur lors du changement de statut', error, { context: 'useUserDetail', showToast: true })
    }
  }

  return {
    user,
    isLoading,
    navIds,
    loadUser,
    handlePhotoUpload,
    handleUpdateUser,
    handleToggleActive,
  }
}

export default useUserDetail
