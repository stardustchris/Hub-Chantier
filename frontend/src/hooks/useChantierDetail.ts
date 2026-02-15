/**
 * useChantierDetail - Hook pour la gestion d'un chantier en detail
 *
 * Extrait la logique metier de ChantierDetailPage:
 * - Chargement du chantier et navigation
 * - Mise a jour et suppression
 * - Changement de statut (avec optimistic updates)
 * - Gestion de l'equipe (conducteurs/chefs) (avec optimistic updates)
 *
 * Migration TanStack Query v5 avec optimistic updates pour UI instantanée
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  const queryClient = useQueryClient()

  // Local state (non-query related)
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })
  const [availableUsers, setAvailableUsers] = useState<User[]>([])

  // Modal states
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddUserModal, setShowAddUserModal] = useState<'conducteur' | 'chef' | 'ouvrier' | null>(null)

  // TanStack Query: Chantier data
  const {
    data: chantier = null,
    isLoading,
    refetch: refetchChantier,
  } = useQuery({
    queryKey: ['chantier-detail', chantierId],
    queryFn: async () => {
      try {
        return await chantiersService.getById(chantierId)
      } catch (error) {
        logger.error('Error loading chantier', error, { context: 'useChantierDetail' })
        addToast({ message: 'Erreur lors du chargement du chantier', type: 'error' })
        navigate('/chantiers')
        throw error
      }
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  })

  // Load navigation IDs (not using TanStack Query as it's lightweight)
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

  // Initial load navigation
  useEffect(() => {
    if (chantierId) {
      loadNavigation()
    }
  }, [chantierId, loadNavigation])

  // TanStack Query Mutation: Update chantier (optimistic update)
  const updateChantierMutation = useMutation({
    mutationFn: async (data: ChantierUpdate) => {
      return chantiersService.update(chantierId, data)
    },
    onMutate: async (data) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['chantier-detail', chantierId] })

      // Snapshot previous data
      const previous = queryClient.getQueryData<Chantier>(['chantier-detail', chantierId])

      // Optimistically update
      if (previous) {
        queryClient.setQueryData<Chantier>(['chantier-detail', chantierId], {
          ...previous,
          ...data,
        })
      }

      return { previous }
    },
    onError: (error, _vars, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(['chantier-detail', chantierId], context.previous)
      }
      logger.error('Error updating chantier', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors de la mise a jour', type: 'error' })
    },
    onSuccess: () => {
      setShowEditModal(false)
      addToast({ message: 'Chantier mis a jour', type: 'success' })
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['chantier-detail', chantierId] })
    },
  })

  const handleUpdateChantier = useCallback(async (data: ChantierUpdate) => {
    updateChantierMutation.mutate(data)
  }, [updateChantierMutation])

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

  // TanStack Query Mutation: Change status (optimistic update)
  const changeStatutMutation = useMutation({
    mutationFn: async (action: 'demarrer' | 'receptionner' | 'fermer') => {
      switch (action) {
        case 'demarrer':
          return chantiersService.demarrer(chantierId)
        case 'receptionner':
          return chantiersService.receptionner(chantierId)
        case 'fermer':
          return chantiersService.fermer(chantierId)
      }
    },
    onMutate: async (action) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['chantier-detail', chantierId] })

      // Snapshot previous data
      const previous = queryClient.getQueryData<Chantier>(['chantier-detail', chantierId])

      // Optimistically update status
      if (previous) {
        let newStatut: Chantier['statut']
        switch (action) {
          case 'demarrer':
            newStatut = 'en_cours'
            break
          case 'receptionner':
            newStatut = 'receptionne'
            break
          case 'fermer':
            newStatut = 'ferme'
            break
        }
        queryClient.setQueryData<Chantier>(['chantier-detail', chantierId], {
          ...previous,
          statut: newStatut,
        })
      }

      return { previous }
    },
    onError: (error, _vars, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(['chantier-detail', chantierId], context.previous)
      }
      logger.error('Error changing statut', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors du changement de statut', type: 'error' })
    },
    onSuccess: () => {
      addToast({ message: 'Statut mis a jour', type: 'success' })
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['chantier-detail', chantierId] })
    },
  })

  const handleChangeStatut = useCallback(async (action: 'demarrer' | 'receptionner' | 'fermer') => {
    changeStatutMutation.mutate(action)
  }, [changeStatutMutation])

  // TanStack Query Mutation: Add user to team (optimistic update)
  const addUserMutation = useMutation({
    mutationFn: async ({ userId, type }: { userId: string; type: 'conducteur' | 'chef' | 'ouvrier' }) => {
      if (type === 'conducteur') {
        return chantiersService.addConducteur(chantierId, userId)
      } else if (type === 'chef') {
        return chantiersService.addChef(chantierId, userId)
      } else {
        return chantiersService.addOuvrier(chantierId, userId)
      }
    },
    onMutate: async ({ userId, type }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['chantier-detail', chantierId] })

      // Snapshot previous data
      const previous = queryClient.getQueryData<Chantier>(['chantier-detail', chantierId])

      // Optimistically add user (simplified - real user data comes from server)
      if (previous) {
        const newUser: User = {
          id: userId,
          nom: '',
          prenom: '',
          email: '',
          role: type === 'chef' ? 'chef_chantier' : type,
          is_active: true,
        } as User

        const updated: Chantier = { ...previous }
        if (type === 'conducteur') {
          updated.conducteurs = [...previous.conducteurs, newUser]
        } else if (type === 'chef') {
          updated.chefs = [...previous.chefs, newUser]
        } else {
          updated.ouvriers = [...(previous.ouvriers || []), newUser]
        }

        queryClient.setQueryData<Chantier>(['chantier-detail', chantierId], updated)
      }

      return { previous }
    },
    onError: (error, _vars, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(['chantier-detail', chantierId], context.previous)
      }
      logger.error('Error adding user', error, { context: 'useChantierDetail' })
      addToast({ message: "Erreur lors de l'ajout", type: 'error' })
    },
    onSuccess: () => {
      setShowAddUserModal(null)
      addToast({ message: 'Utilisateur ajoute', type: 'success' })
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['chantier-detail', chantierId] })
    },
  })

  const handleAddUser = useCallback(async (userId: string) => {
    if (!showAddUserModal) return
    addUserMutation.mutate({ userId, type: showAddUserModal })
  }, [showAddUserModal, addUserMutation])

  // TanStack Query Mutation: Remove user from team (optimistic update with undo)
  const removeUserMutation = useMutation({
    mutationFn: async ({ userId, type }: { userId: string; type: 'conducteur' | 'chef' | 'ouvrier' }) => {
      if (type === 'conducteur') {
        return chantiersService.removeConducteur(chantierId, userId)
      } else if (type === 'chef') {
        return chantiersService.removeChef(chantierId, userId)
      } else {
        return chantiersService.removeOuvrier(chantierId, userId)
      }
    },
    onSuccess: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['chantier-detail', chantierId] })
    },
    onError: (error) => {
      logger.error('Error removing user', error, { context: 'useChantierDetail' })
      addToast({ message: 'Erreur lors du retrait', type: 'error', duration: 5000 })
      // Refetch to restore proper state
      queryClient.invalidateQueries({ queryKey: ['chantier-detail', chantierId] })
    },
  })

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

    // Snapshot previous data
    const previousChantier = chantier

    // Optimistically remove user
    const updatedChantier: Chantier = {
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
    queryClient.setQueryData<Chantier>(['chantier-detail', chantierId], updatedChantier)

    showUndoToast(
      `${removedUser.prenom} ${removedUser.nom} retire`,
      () => {
        // Undo: restore previous data
        queryClient.setQueryData(['chantier-detail', chantierId], previousChantier)
        addToast({ message: 'Retrait annule', type: 'success', duration: 3000 })
      },
      async () => {
        // Commit: execute mutation
        removeUserMutation.mutate({ userId, type })
      },
      5000
    )
  }, [chantier, chantierId, queryClient, showUndoToast, addToast, removeUserMutation])

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
    await refetchChantier()
    await loadNavigation()
  }, [refetchChantier, loadNavigation])

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
