/**
 * Hook pour gérer la logique de pointage (clock-in/out)
 * Extrait de DashboardPage pour améliorer la maintenabilité
 */
import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../contexts/ToastContext'

// Clé localStorage pour le pointage du jour
const CLOCK_STORAGE_KEY = 'hub_chantier_clock_today'

export interface ClockState {
  date: string
  clockInTime?: string
  clockOutTime?: string
}

export interface UseClockCardReturn {
  clockState: ClockState | null
  isClockedIn: boolean
  showEditModal: boolean
  editTimeType: 'arrival' | 'departure'
  editTimeValue: string
  setEditTimeValue: (value: string) => void
  handleClockIn: () => void
  handleClockOut: () => void
  handleEditTime: (type: 'arrival' | 'departure', currentTime?: string) => void
  handleSaveEditedTime: () => void
  closeEditModal: () => void
}

/**
 * Hook pour gérer le pointage journalier
 */
export function useClockCard(): UseClockCardReturn {
  const { addToast } = useToast()
  const [clockState, setClockState] = useState<ClockState | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editTimeType, setEditTimeType] = useState<'arrival' | 'departure'>('arrival')
  const [editTimeValue, setEditTimeValue] = useState('')

  // Charger l'état du pointage depuis localStorage au montage
  useEffect(() => {
    loadClockState()
  }, [])

  /**
   * Charge l'état du pointage depuis localStorage avec validation
   */
  const loadClockState = () => {
    try {
      const today = new Date().toISOString().split('T')[0]
      const stored = localStorage.getItem(CLOCK_STORAGE_KEY)

      if (!stored) return

      const state = JSON.parse(stored) as ClockState

      // Valider le schéma
      if (!state.date || typeof state.date !== 'string') {
        localStorage.removeItem(CLOCK_STORAGE_KEY)
        return
      }

      // Réinitialiser si c'est un nouveau jour
      if (state.date === today) {
        setClockState(state)
      } else {
        localStorage.removeItem(CLOCK_STORAGE_KEY)
      }
    } catch {
      // En cas d'erreur de parsing, supprimer les données corrompues
      localStorage.removeItem(CLOCK_STORAGE_KEY)
    }
  }

  /**
   * Sauvegarde l'état du pointage dans localStorage
   */
  const saveClockState = (state: ClockState) => {
    try {
      localStorage.setItem(CLOCK_STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Silently fail si localStorage non disponible
    }
  }

  /**
   * Enregistre l'heure d'arrivée
   */
  const handleClockIn = useCallback(() => {
    const now = new Date()
    const today = now.toISOString().split('T')[0]
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

    const newState: ClockState = {
      date: today,
      clockInTime: timeStr,
    }
    setClockState(newState)
    saveClockState(newState)
    addToast({
      message: `Arrivee pointee a ${timeStr}. Bonne journee de travail !`,
      type: 'success',
    })
  }, [addToast])

  /**
   * Enregistre l'heure de départ
   */
  const handleClockOut = useCallback(() => {
    const now = new Date()
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

    setClockState(prev => {
      if (!prev) return null
      const newState = { ...prev, clockOutTime: timeStr }
      saveClockState(newState)
      return newState
    })
    addToast({
      message: `Depart pointe a ${timeStr}. A demain !`,
      type: 'success',
    })
  }, [addToast])

  /**
   * Ouvre la modal d'édition d'heure
   */
  const handleEditTime = useCallback((type: 'arrival' | 'departure', currentTime?: string) => {
    setEditTimeType(type)
    setEditTimeValue(currentTime || '')
    setShowEditModal(true)
  }, [])

  /**
   * Sauvegarde l'heure modifiée
   */
  const handleSaveEditedTime = useCallback(() => {
    if (!editTimeValue) return

    setClockState(prev => {
      const today = new Date().toISOString().split('T')[0]

      if (!prev) {
        const newState: ClockState = {
          date: today,
          clockInTime: editTimeType === 'arrival' ? editTimeValue : undefined,
          clockOutTime: editTimeType === 'departure' ? editTimeValue : undefined,
        }
        saveClockState(newState)
        return newState
      }

      const newState = {
        ...prev,
        [editTimeType === 'arrival' ? 'clockInTime' : 'clockOutTime']: editTimeValue,
      }
      saveClockState(newState)
      return newState
    })

    setShowEditModal(false)
    addToast({
      message: `Heure modifiee: ${editTimeValue}`,
      type: 'success',
    })
  }, [editTimeType, editTimeValue, addToast])

  /**
   * Ferme la modal d'édition
   */
  const closeEditModal = useCallback(() => {
    setShowEditModal(false)
  }, [])

  return {
    clockState,
    isClockedIn: !!clockState?.clockInTime && !clockState?.clockOutTime,
    showEditModal,
    editTimeType,
    editTimeValue,
    setEditTimeValue,
    handleClockIn,
    handleClockOut,
    handleEditTime,
    handleSaveEditedTime,
    closeEditModal,
  }
}

export default useClockCard
