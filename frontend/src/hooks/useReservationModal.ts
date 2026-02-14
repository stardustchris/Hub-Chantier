/**
 * Hook personnalisé pour gérer l'état et les actions de ReservationModal.
 *
 * M13: Extraction de la logique du composant ReservationModal.
 *
 * @module hooks/useReservationModal
 */

import { useState, useEffect, useCallback } from 'react'
import type { Ressource, Reservation, ReservationCreate } from '../types/logistique'
import {
  createReservation,
  validerReservation,
  refuserReservation,
  annulerReservation,
} from '../services/logistique'

/**
 * Options de configuration du hook useReservationModal.
 */
export interface UseReservationModalOptions {
  /** Indique si le modal est ouvert */
  isOpen: boolean
  /** Ressource concernée par la réservation */
  ressource: Ressource
  /** Réservation existante (mode vue) ou null (mode création) */
  reservation?: Reservation | null
  /** Date initiale pour le formulaire (format YYYY-MM-DD) */
  initialDate?: string
  /** Heure de début initiale (format HH:MM) */
  initialHeureDebut?: string
  /** Heure de fin initiale (format HH:MM) */
  initialHeureFin?: string
  /** Callback appelé en cas de succès */
  onSuccess?: () => void
  /** Callback pour fermer le modal */
  onClose: () => void
}

/**
 * État et actions retournés par useReservationModal.
 */
export interface UseReservationModalReturn {
  /** Indicateur de chargement */
  loading: boolean
  /** Message d'erreur ou null */
  error: string | null
  /** Données du formulaire */
  formData: Partial<ReservationCreate>
  /** Motif de refus saisi */
  motifRefus: string
  /** Indique si le champ motif de refus est visible */
  showMotifRefus: boolean
  /** Met à jour les données du formulaire */
  setFormData: (data: Partial<ReservationCreate>) => void
  /** Met à jour le motif de refus */
  setMotifRefus: (motif: string) => void
  /** Affiche/masque le champ motif de refus */
  setShowMotifRefus: (show: boolean) => void
  /** Soumet le formulaire de création */
  handleSubmit: (e: React.FormEvent) => Promise<void>
  /** Valide la réservation */
  handleValider: () => Promise<void>
  /** Refuse la réservation */
  handleRefuser: () => Promise<void>
  /** Annule la réservation */
  handleAnnuler: () => Promise<void>
  /** Indique si on est en mode vue (vs création) */
  isViewMode: boolean
}

/**
 * Hook personnalisé pour gérer l'état et les actions d'un modal de réservation.
 *
 * Gère:
 * - L'état du formulaire de création
 * - Les actions de validation/refus/annulation
 * - Le chargement et les erreurs
 * - La réinitialisation à l'ouverture
 *
 * @example
 * ```tsx
 * const {
 *   loading,
 *   error,
 *   formData,
 *   setFormData,
 *   handleSubmit,
 *   handleValider,
 *   isViewMode,
 * } = useReservationModal({
 *   isOpen: true,
 *   ressource: myRessource,
 *   reservation: null,
 *   onSuccess: () => refetch(),
 *   onClose: () => setIsOpen(false),
 * })
 * ```
 *
 * @param options - Options de configuration
 * @returns État et actions du modal
 */
export function useReservationModal(
  options: UseReservationModalOptions
): UseReservationModalReturn {
  const {
    isOpen,
    ressource,
    reservation,
    initialDate,
    initialHeureDebut,
    initialHeureFin,
    onSuccess,
    onClose,
  } = options

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [motifRefus, setMotifRefus] = useState('')
  const [showMotifRefus, setShowMotifRefus] = useState(false)

  const [formData, setFormData] = useState<Partial<ReservationCreate>>({
    ressource_id: ressource.id,
    chantier_id: 0,
    date_reservation: initialDate || new Date().toISOString().split('T')[0],
    heure_debut: initialHeureDebut || ressource.heure_debut_defaut.substring(0, 5),
    heure_fin: initialHeureFin || ressource.heure_fin_defaut.substring(0, 5),
    commentaire: '',
  })

  const isViewMode = !!reservation

  // Réinitialise le formulaire à l'ouverture (mode création uniquement)
  useEffect(() => {
    if (isOpen && !reservation) {
      setFormData({
        ressource_id: ressource.id,
        chantier_id: 0,
        date_reservation: initialDate || new Date().toISOString().split('T')[0],
        heure_debut: initialHeureDebut || ressource.heure_debut_defaut.substring(0, 5),
        heure_fin: initialHeureFin || ressource.heure_fin_defaut.substring(0, 5),
        commentaire: '',
      })
      setError(null)
      setShowMotifRefus(false)
      setMotifRefus('')
    }
  }, [isOpen, reservation, ressource, initialDate, initialHeureDebut, initialHeureFin])

  /**
   * Soumet le formulaire pour créer une nouvelle réservation.
   */
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!formData.chantier_id) {
        setError('Veuillez sélectionner un chantier')
        return
      }

      try {
        setLoading(true)
        setError(null)
        await createReservation(formData as ReservationCreate)
        onSuccess?.()
        onClose()
      } catch (err: unknown) {
        const error = err as { response?: { status?: number; data?: { detail?: string } } }
        if (error.response?.status === 409) {
          setError('Conflit: ce créneau est déjà réservé')
        } else {
          setError(error.response?.data?.detail || 'Erreur lors de la création')
        }
      } finally {
        setLoading(false)
      }
    },
    [formData, onSuccess, onClose]
  )

  /**
   * Valide une réservation en attente.
   */
  const handleValider = useCallback(async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await validerReservation(reservation.id)
      onSuccess?.()
      onClose()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Erreur lors de la validation')
    } finally {
      setLoading(false)
    }
  }, [reservation, onSuccess, onClose])

  /**
   * Refuse une réservation avec un motif optionnel.
   */
  const handleRefuser = useCallback(async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await refuserReservation(reservation.id, motifRefus || undefined)
      onSuccess?.()
      onClose()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Erreur lors du refus')
    } finally {
      setLoading(false)
    }
  }, [reservation, motifRefus, onSuccess, onClose])

  /**
   * Annule une réservation validée.
   */
  const handleAnnuler = useCallback(async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await annulerReservation(reservation.id)
      onSuccess?.()
      onClose()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || "Erreur lors de l'annulation")
    } finally {
      setLoading(false)
    }
  }, [reservation, onSuccess, onClose])

  return {
    loading,
    error,
    formData,
    motifRefus,
    showMotifRefus,
    setFormData,
    setMotifRefus,
    setShowMotifRefus,
    handleSubmit,
    handleValider,
    handleRefuser,
    handleAnnuler,
    isViewMode,
  }
}
