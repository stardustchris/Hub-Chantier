/**
 * useChantierDetail - Hook pour la gestion d'un chantier en detail
 *
 * Extrait la logique metier de ChantierDetailPage:
 * - Chargement du chantier et navigation
 * - Mise a jour et suppression
 * - Changement de statut
 * - Gestion de l'equipe (conducteurs/chefs)
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { chantiersService, NavigationIds } from '../services/chantiers'
import { usersService } from '../services/users'
import { useToast } from '../contexts/ToastContext'
import { logger } from '../services/logger'
import type { Chantier, ChantierUpdate, User } from '../types'

interface UseChantierDetailOptions {
  chantierId: string
}

interface UseChantierDetailReturn {
  // Data
  chantier: Chantier | null
  navIds: NavigationIds
  availableUsers: User[]
  isLoading: boolean

  // Modal states
  showEditModal: boolean
  showAddUserModal: 'conducteur' | 'chef' | 'ouvrier' | null

  // Actions
  setShowEditModal: (show: boolean) => void
  openAddUserModal: (type: 'conducteur' | 'chef' | 'ouvrier') => void
  closeAddUserModal: () => void
  handleUpdateChantier: (data: ChantierUpdate) => Promise<void>
  handleDeleteChantier: () => void
  handleChangeStatut: (action: 'demarrer' | 'receptionner' | 'fermer') => Promise<void>
  handleAddUser: (userId: string) => Promise<void>
  handleRemoveUser: (userId: string, type: 'conducteur' | 'chef' | 'ouvrier') => void
  reload: () => Promise<void>
}

export function useChantierDetail({
  chantierId,
}: UseChantierDetailOptions): UseChantierDetailReturn {
  const navigate = useNavigate()
  const { showUndoToast, addToast } = useToast()

  // State
  const [chantier, setChantier] = useState<Chantier | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })
  const [availableUsers, setAvailableUsers] = useState<User[]>([])

  // Modal states
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddUserModal, setShowAddUserModal] = useState<'conducteur' | 'chef' | 'ouvrier' | null>(null)

  // Load chantier data
  const loadChantier = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await chantiersService.getById(chantierId)
      setChantier(data)
    } catch (error) {
      logger.error('Error loading chantier', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors du chargement du chantier', type: 'error' })
      navigate('/chantiers')
    } finally {
      setIsLoading(false)
    }
  }, [chantierId, addToast, navigate])

  // Load navigation IDs
  const loadNavigation = useCallback(async () => {
    try {
      const ids = await chantiersService.getNavigationIds(chantierId)
      setNavIds(ids)
    } catch (error) {
      logger.error('Error loading navigation', error, { context: 'useChantierDetail' })
    }
  }, [chantierId])

  // Load available users for team management
  const loadAvailableUsers = useCallback(async (role: 'conducteur' | 'chef' | 'ouvrier') => {
    try {
      const roleFilter = role === 'conducteur' ? 'conducteur' : role === 'chef' ? 'chef_chantier' : 'ouvrier'
      const response = await usersService.list({
        size: 100,
        role: roleFilter,
        is_active: true,
      })
      let existingIds: string[] = []
      if (role === 'conducteur') {
        existingIds = chantier?.conducteurs.map((u) => u.id) || []
      } else if (role === 'chef') {
        existingIds = chantier?.chefs.map((u) => u.id) || []
      } else {
        existingIds = chantier?.ouvriers?.map((u) => u.id) || []
      }
      setAvailableUsers(response.items.filter((u) => !existingIds.includes(u.id)))
    } catch (error) {
      logger.error('Error loading users', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors du chargement des utilisateurs', type: 'error' })
    }
  }, [chantier, addToast])

  // Initial load
  useEffect(() => {
    if (chantierId) {
      loadChantier()
      loadNavigation()
    }
  }, [chantierId, loadChantier, loadNavigation])

  // Update chantier
  const handleUpdateChantier = useCallback(async (data: ChantierUpdate) => {
    try {
      const updated = await chantiersService.update(chantierId, data)
      setChantier(updated)
      setShowEditModal(false)
      addToast({ message: 'Chantier mis a jour', type: 'success' })
    } catch (error) {
      logger.error('Error updating chantier', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors de la mise a jour', type: 'error' })
    }
  }, [chantierId, addToast])

  // Delete chantier with undo
  const handleDeleteChantier = useCallback(() => {
    if (!chantier) return

    const chantierName = chantier.nom
    navigate('/chantiers')

    showUndoToast(
      `Chantier "${chantierName}" supprime`,
      () => {
        navigate(`/chantiers/${chantierId}`)
        addToast({ message: 'Suppression annulee', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          await chantiersService.delete(chantierId)
        } catch (error) {
          logger.error('Error deleting chantier', error, { context: 'useChantierDetail' })
          addToast({ message: 'Erreur lors de la suppression', type: 'error', duration: 5000 })
        }
      },
      5000
    )
  }, [chantier, chantierId, navigate, showUndoToast, addToast])

  // Change status
  const handleChangeStatut = useCallback(async (action: 'demarrer' | 'receptionner' | 'fermer') => {
    try {
      let updated: Chantier
      switch (action) {
        case 'demarrer':
          updated = await chantiersService.demarrer(chantierId)
          break
        case 'receptionner':
          updated = await chantiersService.receptionner(chantierId)
          break
        case 'fermer':
          updated = await chantiersService.fermer(chantierId)
          break
      }
      setChantier(updated)
      addToast({ message: 'Statut mis a jour', type: 'success' })
    } catch (error) {
      logger.error('Error changing statut', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors du changement de statut', type: 'error' })
    }
  }, [chantierId, addToast])

  // Add user to team
  const handleAddUser = useCallback(async (userId: string) => {
    if (!showAddUserModal) return

    try {
      let updated: Chantier
      if (showAddUserModal === 'conducteur') {
        updated = await chantiersService.addConducteur(chantierId, userId)
      } else if (showAddUserModal === 'chef') {
        updated = await chantiersService.addChef(chantierId, userId)
      } else {
        updated = await chantiersService.addOuvrier(chantierId, userId)
      }
      setChantier(updated)
      setShowAddUserModal(null)
      addToast({ message: 'Utilisateur ajoute', type: 'success' })
    } catch (error) {
      logger.error('Error adding user', error, { context: 'useChantierDetail' })
      addToast({ message: "Erreur lors de l'ajout", type: 'error' })
    }
  }, [chantierId, showAddUserModal, addToast])

  // Remove user from team with undo
  const handleRemoveUser = useCallback((userId: string, type: 'conducteur' | 'chef' | 'ouvrier') => {
    if (!chantier) return

    let userList: User[]
    if (type === 'conducteur') {
      userList = chantier.conducteurs
    } else if (type === 'chef') {
      userList = chantier.chefs
    } else {
      userList = chantier.ouvriers || []
    }
    const removedUser = userList.find((u) => u.id === userId)
    if (!removedUser) return

    const previousChantier = chantier
    const updatedChantier = {
      ...chantier,
      conducteurs: type === 'conducteur'
        ? chantier.conducteurs.filter((u) => u.id !== userId)
        : chantier.conducteurs,
      chefs: type === 'chef'
        ? chantier.chefs.filter((u) => u.id !== userId)
        : chantier.chefs,
      ouvriers: type === 'ouvrier'
        ? (chantier.ouvriers || []).filter((u) => u.id !== userId)
        : chantier.ouvriers,
    }
    setChantier(updatedChantier)

    showUndoToast(
      `${removedUser.prenom} ${removedUser.nom} retire`,
      () => {
        setChantier(previousChantier)
        addToast({ message: 'Retrait annule', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          if (type === 'conducteur') {
            await chantiersService.removeConducteur(chantierId, userId)
          } else if (type === 'chef') {
            await chantiersService.removeChef(chantierId, userId)
          } else {
            await chantiersService.removeOuvrier(chantierId, userId)
          }
        } catch (error) {
          logger.error('Error removing user', error, { context: 'useChantierDetail' })
          setChantier(previousChantier)
          addToast({ message: 'Erreur lors du retrait', type: 'error', duration: 5000 })
        }
      },
      5000
    )
  }, [chantier, chantierId, showUndoToast, addToast])

  // Open add user modal
  const openAddUserModal = useCallback((type: 'conducteur' | 'chef' | 'ouvrier') => {
    loadAvailableUsers(type)
    setShowAddUserModal(type)
  }, [loadAvailableUsers])

  // Close add user modal
  const closeAddUserModal = useCallback(() => {
    setShowAddUserModal(null)
  }, [])

  // Reload function
  const reload = useCallback(async () => {
    await loadChantier()
    await loadNavigation()
  }, [loadChantier, loadNavigation])

  return {
    // Data
    chantier,
    navIds,
    availableUsers,
    isLoading,

    // Modal states
    showEditModal,
    showAddUserModal,

    // Actions
    setShowEditModal,
    openAddUserModal,
    closeAddUserModal,
    handleUpdateChantier,
    handleDeleteChantier,
    handleChangeStatut,
    handleAddUser,
    handleRemoveUser,
    reload,
  }
}

export default useChantierDetail
