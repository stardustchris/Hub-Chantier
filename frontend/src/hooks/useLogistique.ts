/**
 * useLogistique - Hook pour la gestion de la logistique
 *
 * Extrait la logique metier de LogistiquePage:
 * - Chargement des chantiers et reservations
 * - Gestion des permissions
 * - Gestion des modals de reservation
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { chantiersService } from '../services/chantiers'
import { listReservationsEnAttente, listRessources } from '../api/logistique'
import { logger } from '../services/logger'
import type { Ressource, Reservation } from '../types/logistique'
import type { Chantier } from '../types'

type TabType = 'ressources' | 'planning' | 'en-attente'

interface UseLogistiqueReturn {
  // User permissions
  isAdmin: boolean
  canValidate: boolean

  // Tab state
  activeTab: TabType
  setActiveTab: (tab: TabType) => void

  // Data
  chantiers: Chantier[]
  reservationsEnAttente: Reservation[]

  // Resource selection
  selectedRessource: Ressource | null
  setSelectedRessource: (ressource: Ressource | null) => void

  // Reservation selection
  selectedReservation: Reservation | null
  setSelectedReservation: (reservation: Reservation | null) => void

  // Modal state
  showModal: boolean
  setShowModal: (show: boolean) => void
  modalInitialData: {
    date?: string
    heureDebut?: string
    heureFin?: string
  }

  // Actions
  handleSelectRessource: (ressource: Ressource) => void
  handleCreateReservation: (date: string, heureDebut: string, heureFin: string) => void
  handleSelectReservation: (reservation: Reservation) => void
  handleSelectPendingReservation: (reservation: Reservation) => Promise<void>
  handleModalClose: () => void
  handleModalSuccess: () => void

  // Tabs configuration
  tabs: { id: TabType; label: string; badge?: number }[]
}

export function useLogistique(): UseLogistiqueReturn {
  const { user } = useAuth()

  // Permissions
  const isAdmin = user?.role === 'admin'
  const canValidate = user?.role === 'admin' || user?.role === 'conducteur' || user?.role === 'chef_chantier'

  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('ressources')

  // Data state
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [reservationsEnAttente, setReservationsEnAttente] = useState<Reservation[]>([])

  // Selection state
  const [selectedRessource, setSelectedRessource] = useState<Ressource | null>(null)
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null)

  // Modal state
  const [showModal, setShowModal] = useState(false)
  const [modalInitialData, setModalInitialData] = useState<{
    date?: string
    heureDebut?: string
    heureFin?: string
  }>({})

  // Load chantiers
  const loadChantiers = useCallback(async () => {
    try {
      const data = await chantiersService.list({ size: 500 })
      setChantiers(data?.items || [])
    } catch (err) {
      logger.error('Erreur chargement chantiers', err, { context: 'useLogistique' })
    }
  }, [])

  // Load pending reservations
  const loadReservationsEnAttente = useCallback(async () => {
    try {
      const data = await listReservationsEnAttente()
      setReservationsEnAttente(data?.items || [])
    } catch (err) {
      logger.error('Erreur chargement reservations en attente', err, { context: 'useLogistique' })
    }
  }, [])

  // Initial data load
  useEffect(() => {
    loadChantiers()
    if (canValidate) {
      loadReservationsEnAttente()
    }
  }, [canValidate, loadChantiers, loadReservationsEnAttente])

  // Handle resource selection
  const handleSelectRessource = useCallback((ressource: Ressource) => {
    setSelectedRessource(ressource)
    setActiveTab('planning')
  }, [])

  // Handle create reservation (from calendar click)
  const handleCreateReservation = useCallback((date: string, heureDebut: string, heureFin: string) => {
    setModalInitialData({ date, heureDebut, heureFin })
    setSelectedReservation(null)
    setShowModal(true)
  }, [])

  // Handle select existing reservation
  const handleSelectReservation = useCallback((reservation: Reservation) => {
    setSelectedReservation(reservation)
    setShowModal(true)
  }, [])

  // Handle select pending reservation (from en-attente tab)
  const handleSelectPendingReservation = useCallback(async (reservation: Reservation) => {
    try {
      const data = await listRessources({ limit: 1000 })
      const ressource = (data?.items || []).find((r: Ressource) => r.id === reservation.ressource_id)
      if (ressource) {
        setSelectedRessource(ressource)
        setSelectedReservation(reservation)
        setShowModal(true)
      }
    } catch (err) {
      logger.error('Erreur chargement ressource', err, { context: 'useLogistique' })
    }
  }, [])

  // Handle modal close
  const handleModalClose = useCallback(() => {
    setShowModal(false)
    setSelectedReservation(null)
    setModalInitialData({})
  }, [])

  // Handle modal success
  const handleModalSuccess = useCallback(() => {
    if (canValidate) {
      loadReservationsEnAttente()
    }
  }, [canValidate, loadReservationsEnAttente])

  // Tabs configuration
  const tabs: { id: TabType; label: string; badge?: number }[] = [
    { id: 'ressources', label: 'Ressources' },
    { id: 'planning', label: 'Planning' },
  ]

  if (canValidate) {
    tabs.push({
      id: 'en-attente',
      label: 'En attente',
      badge: reservationsEnAttente.length,
    })
  }

  return {
    // Permissions
    isAdmin,
    canValidate,

    // Tab state
    activeTab,
    setActiveTab,

    // Data
    chantiers,
    reservationsEnAttente,

    // Selection
    selectedRessource,
    setSelectedRessource,
    selectedReservation,
    setSelectedReservation,

    // Modal
    showModal,
    setShowModal,
    modalInitialData,

    // Actions
    handleSelectRessource,
    handleCreateReservation,
    handleSelectReservation,
    handleSelectPendingReservation,
    handleModalClose,
    handleModalSuccess,

    // Tabs
    tabs,
  }
}

export default useLogistique
