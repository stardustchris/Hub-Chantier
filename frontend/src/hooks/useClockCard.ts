/**
 * Hook pour gérer la logique de pointage (clock-in/out)
 * Extrait de DashboardPage pour améliorer la maintenabilité
 *
 * Persiste le pointage côté serveur via pointagesService :
 * - Clock-in : enregistre l'heure d'arrivée en local
 * - Clock-out : calcule les heures travaillées et crée un pointage backend
 */
import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../contexts/ToastContext'
import { useAuth } from '../contexts/AuthContext'
import { pointagesService } from '../services/pointages'
import { logger } from '../services/logger'

// Clé sessionStorage pour le pointage du jour (évite manipulation localStorage)
const CLOCK_STORAGE_KEY = 'hub_chantier_clock_today'

export interface ClockState {
  date: string
  clockInTime?: string
  clockOutTime?: string
  /** ID du pointage backend (set après sync réussie) */
  pointageId?: number
  /** ID du chantier associé */
  chantierId?: string
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
  /** Définir le chantier pour le pointage du jour */
  setChantierId: (id: string) => void
}

/**
 * Calcule la différence entre deux heures HH:MM et retourne au format HH:MM
 */
function computeHoursWorked(clockIn: string, clockOut: string): string {
  const [inH, inM] = clockIn.split(':').map(Number)
  const [outH, outM] = clockOut.split(':').map(Number)

  let totalMinutes = (outH * 60 + outM) - (inH * 60 + inM)
  if (totalMinutes < 0) totalMinutes = 0

  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

/**
 * Hook pour gérer le pointage journalier
 */
export function useClockCard(): UseClockCardReturn {
  const { addToast } = useToast()
  const { user } = useAuth()
  const [clockState, setClockState] = useState<ClockState | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editTimeType, setEditTimeType] = useState<'arrival' | 'departure'>('arrival')
  const [editTimeValue, setEditTimeValue] = useState('')

  // Charger l'état du pointage depuis sessionStorage au montage
  useEffect(() => {
    loadClockState()
  }, [])

  /**
   * Charge l'état du pointage depuis sessionStorage avec validation
   */
  const loadClockState = () => {
    try {
      const today = new Date().toISOString().split('T')[0]
      const stored = sessionStorage.getItem(CLOCK_STORAGE_KEY)

      if (!stored) return

      const state = JSON.parse(stored) as ClockState

      // Valider le schéma
      if (!state.date || typeof state.date !== 'string') {
        sessionStorage.removeItem(CLOCK_STORAGE_KEY)
        return
      }

      // Réinitialiser si c'est un nouveau jour
      if (state.date === today) {
        setClockState(state)
      } else {
        sessionStorage.removeItem(CLOCK_STORAGE_KEY)
      }
    } catch {
      // En cas d'erreur de parsing, supprimer les données corrompues
      sessionStorage.removeItem(CLOCK_STORAGE_KEY)
    }
  }

  /**
   * Sauvegarde l'état du pointage dans sessionStorage
   */
  const saveClockState = (state: ClockState) => {
    try {
      sessionStorage.setItem(CLOCK_STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Silently fail si sessionStorage non disponible
    }
  }

  /**
   * Définir le chantier ID pour le pointage
   */
  const setChantierId = useCallback((id: string) => {
    setClockState(prev => {
      if (!prev) return prev
      if (prev.chantierId === id) return prev
      const newState = { ...prev, chantierId: id }
      saveClockState(newState)
      return newState
    })
  }, [])

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
   * Synchonise le pointage avec le backend
   */
  const syncPointageToBackend = useCallback(async (state: ClockState) => {
    if (!user?.id || !state.clockInTime || !state.clockOutTime) return

    const userId = Number(user.id)
    if (isNaN(userId)) return

    const heuresNormales = computeHoursWorked(state.clockInTime, state.clockOutTime)

    // Si déjà un pointage backend, mettre à jour
    if (state.pointageId) {
      try {
        await pointagesService.update(state.pointageId, {
          heures_normales: heuresNormales,
        }, userId)
        logger.info('Pointage mis à jour', { pointageId: state.pointageId, heuresNormales })
      } catch (err) {
        logger.error('Erreur mise à jour pointage', err)
      }
      return
    }

    // Créer un nouveau pointage
    const chantierId = state.chantierId ? Number(state.chantierId) : null
    if (!chantierId) {
      logger.warn('Pas de chantier associé au pointage, sync ignorée')
      return
    }

    try {
      const pointage = await pointagesService.create({
        utilisateur_id: userId,
        chantier_id: chantierId,
        date_pointage: state.date,
        heures_normales: heuresNormales,
      }, userId)

      // Sauvegarder l'ID du pointage pour pouvoir le mettre à jour
      const updatedState = { ...state, pointageId: pointage.id }
      setClockState(updatedState)
      saveClockState(updatedState)
      logger.info('Pointage créé', { pointageId: pointage.id, heuresNormales })
    } catch (err) {
      logger.error('Erreur création pointage backend', err)
      addToast({
        message: 'Pointage enregistré localement (synchronisation en attente)',
        type: 'warning',
      })
    }
  }, [user?.id, addToast])

  /**
   * Enregistre l'heure de départ et sync avec le backend
   */
  const handleClockOut = useCallback(() => {
    const now = new Date()
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

    setClockState(prev => {
      if (!prev) return null
      const newState = { ...prev, clockOutTime: timeStr }
      saveClockState(newState)

      // Sync async avec le backend
      syncPointageToBackend(newState)

      return newState
    })
    addToast({
      message: `Depart pointe a ${timeStr}. A demain !`,
      type: 'success',
    })
  }, [addToast, syncPointageToBackend])

  /**
   * Ouvre la modal d'édition d'heure
   */
  const handleEditTime = useCallback((type: 'arrival' | 'departure', currentTime?: string) => {
    setEditTimeType(type)
    setEditTimeValue(currentTime || '')
    setShowEditModal(true)
  }, [])

  /**
   * Sauvegarde l'heure modifiée et re-sync si départ modifié
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

      // Re-sync si les deux heures sont renseignées
      if (newState.clockInTime && newState.clockOutTime) {
        syncPointageToBackend(newState)
      }

      return newState
    })

    setShowEditModal(false)
    addToast({
      message: `Heure modifiee: ${editTimeValue}`,
      type: 'success',
    })
  }, [editTimeType, editTimeValue, addToast, syncPointageToBackend])

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
    setChantierId,
  }
}

export default useClockCard
