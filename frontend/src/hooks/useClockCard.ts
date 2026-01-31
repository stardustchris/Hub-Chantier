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
import type { Pointage } from '../types'

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

  // Charger l'état du pointage depuis le backend au montage
  useEffect(() => {
    loadClockStateFromBackend()
  }, [user?.id])

  /**
   * Charge l'état du pointage depuis le backend (source de vérité)
   * Fallback sur sessionStorage si le backend échoue
   */
  const loadClockStateFromBackend = async () => {
    if (!user?.id) return

    const userId = Number(user.id)
    if (isNaN(userId)) return

    const today = new Date().toISOString().split('T')[0]

    try {
      // 1. Essayer de charger depuis le backend
      const response = await pointagesService.list({
        utilisateur_id: userId,
        date_debut: today,
        date_fin: today,
        page: 1,
        page_size: 10,
      })

      // Chercher un pointage pour aujourd'hui
      const todayPointage = response.items.find(p => p.date_pointage === today)

      if (todayPointage) {
        // Reconstituer l'état depuis le pointage backend
        const state: ClockState = {
          date: today,
          pointageId: todayPointage.id,
          chantierId: String(todayPointage.chantier_id),
          // Extraire clockInTime et clockOutTime depuis heures_normales si disponible
          // Format attendu : "08:00" pour 8h
          clockInTime: extractClockInTime(todayPointage),
          // clockOutTime est undefined si le pointage est en brouillon (clock-in uniquement)
          clockOutTime: extractClockOutTime(todayPointage),
        }

        setClockState(state)
        saveClockState(state)
        logger.info('Pointage chargé depuis le backend', { pointageId: todayPointage.id })
        return
      }

      // 2. Si pas de pointage backend, essayer sessionStorage
      loadClockStateFromSession(today)
    } catch (err) {
      logger.warn('Impossible de charger le pointage depuis le backend, fallback sessionStorage', err)
      // 3. Fallback sur sessionStorage en cas d'erreur réseau
      loadClockStateFromSession(today)
    }
  }

  /**
   * Charge l'état du pointage depuis sessionStorage (fallback)
   */
  const loadClockStateFromSession = (today: string) => {
    try {
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
        logger.info('Pointage chargé depuis sessionStorage (cache local)')
      } else {
        sessionStorage.removeItem(CLOCK_STORAGE_KEY)
      }
    } catch {
      // En cas d'erreur de parsing, supprimer les données corrompues
      sessionStorage.removeItem(CLOCK_STORAGE_KEY)
    }
  }

  /**
   * Extrait l'heure d'arrivée depuis un pointage backend
   *
   * Stratégie:
   * - Le backend ne stocke pas explicitement clockInTime
   * - On utilise created_at comme heure d'arrivée (moment où le pointage a été créé)
   * - C'est une approximation raisonnable pour la carte de pointage dashboard
   */
  const extractClockInTime = (pointage: Pointage): string | undefined => {
    if (pointage.created_at) {
      const date = new Date(pointage.created_at)
      return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    }
    return undefined
  }

  /**
   * Extrait l'heure de départ depuis un pointage backend
   *
   * Stratégie:
   * - Si le pointage a des heures_normales ET est validé/soumis, on calcule clockOutTime
   * - clockOutTime = clockInTime + heures_normales
   * - Si le pointage est en brouillon, pas de clockOutTime (en cours de pointage)
   */
  const extractClockOutTime = (pointage: Pointage): string | undefined => {
    // Si brouillon, pas de clockOutTime (l'utilisateur n'a pointé que l'arrivée)
    if (pointage.statut === 'brouillon') {
      return undefined
    }

    // Si validé/soumis et a des heures_normales, calculer clockOutTime
    if (pointage.heures_normales && pointage.heures_normales !== '00:00') {
      const clockInTime = extractClockInTime(pointage)
      if (!clockInTime) return undefined

      const [inH, inM] = clockInTime.split(':').map(Number)
      const [durationH, durationM] = pointage.heures_normales.split(':').map(Number)

      const totalMinutes = (inH * 60 + inM) + (durationH * 60 + durationM)
      const outH = Math.floor(totalMinutes / 60) % 24 // Mod 24 pour gérer les débordements
      const outM = totalMinutes % 60

      return `${String(outH).padStart(2, '0')}:${String(outM).padStart(2, '0')}`
    }
    return undefined
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
   * NOUVEAU : Crée immédiatement un pointage "brouillon" sur le backend
   */
  const handleClockIn = useCallback(async () => {
    const now = new Date()
    const today = now.toISOString().split('T')[0]
    const timeStr = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })

    // 1. Créer l'état local immédiatement (UX réactive)
    const tempState: ClockState = {
      date: today,
      clockInTime: timeStr,
    }

    addToast({
      message: `Arrivee pointee a ${timeStr}. Bonne journee de travail !`,
      type: 'success',
    })

    // 2. Créer un pointage "brouillon" sur le backend (async)
    // On utilise setClockState avec callback pour accéder à l'état actuel (chantierId)
    setClockState(prevState => {
      const chantierId = prevState?.chantierId
      const finalState = { ...tempState, chantierId }

      // Sauvegarder immédiatement
      saveClockState(finalState)

      // Créer le pointage backend en arrière-plan
      if (user?.id && chantierId) {
        const userId = Number(user.id)
        const chantierIdNum = Number(chantierId)

        if (!isNaN(userId) && !isNaN(chantierIdNum)) {
          pointagesService.create({
            utilisateur_id: userId,
            chantier_id: chantierIdNum,
            date_pointage: today,
            heures_normales: '00:00', // Brouillon : pas encore d'heures
          }, userId)
            .then(pointage => {
              // Mettre à jour l'état avec l'ID du pointage backend
              const updatedState = { ...finalState, pointageId: pointage.id }
              setClockState(updatedState)
              saveClockState(updatedState)
              logger.info('Pointage brouillon créé', { pointageId: pointage.id })
            })
            .catch(err => {
              logger.error('Erreur création pointage brouillon', err)
              // L'état local est déjà sauvegardé, on peut continuer
            })
        }
      }

      return finalState
    })
  }, [addToast, user?.id])

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
