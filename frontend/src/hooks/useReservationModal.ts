/**
 * Hook personnalisé pour gérer l'état et les actions de ReservationModal.
 *
 * M13: Extraction de la logique du composant ReservationModal.
 * Migration TanStack Query v5 avec optimistic updates pour validation/refus instantanés
 *
 * @module hooks/useReservationModal
 */

import { useState, useEffect, useCallback } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
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

  const queryClient = useQueryClient()

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

  // TanStack Query Mutation: Create reservation
  const createMutation = useMutation({
    mutationFn: async (data: ReservationCreate) => {
      return createReservation(data)
    },
    onSuccess: () => {
      // Invalidate queries that might display reservations
      queryClient.invalidateQueries({ queryKey: ['reservations'] })
      queryClient.invalidateQueries({ queryKey: ['reservations-en-attente'] })
      onSuccess?.()
      onClose()
    },
    onError: (err: unknown) => {
      const error = err as { response?: { status?: number; data?: { detail?: string } } }
      if (error.response?.status === 409) {
        setError('Conflit: ce créneau est déjà réservé')
      } else {
        setError(error.response?.data?.detail || 'Erreur lors de la création')
      }
    },
  })

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

      setError(null)
      createMutation.mutate(formData as ReservationCreate)
    },
    [formData, createMutation]
  )

  /**
   * TanStack Query Mutation: Valider une réservation (optimistic update)
   */
  const validerMutation = useMutation({
    mutationFn: async (reservationId: number) => {
      return validerReservation(reservationId)
    },
    onMutate: async (reservationId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['reservations'] })
      await queryClient.cancelQueries({ queryKey: ['reservations-en-attente'] })

      // Snapshot previous data
      const previousEnAttente = queryClient.getQueryData(['reservations-en-attente'])
      const previousReservations = queryClient.getQueriesData({ queryKey: ['reservations'] })

      // Optimistically update: change status to 'validee'
      queryClient.setQueriesData({ queryKey: ['reservations-en-attente'] }, (old: unknown) => {
        if (!old || typeof old !== 'object' || !('items' in old)) return old
        const data = old as { items: Reservation[] }
        if (!data.items) return old
        return {
          ...data,
          items: data.items.filter((r: Reservation) => r.id !== reservationId),
        }
      })

      queryClient.setQueriesData({ queryKey: ['reservations'] }, (old: unknown) => {
        if (!old || typeof old !== 'object' || !('items' in old)) return old
        const data = old as { items: Reservation[] }
        if (!data.items) return old
        return {
          ...data,
          items: data.items.map((r: Reservation) =>
            r.id === reservationId ? { ...r, statut: 'validee' as const } : r
          ),
        }
      })

      return { previousEnAttente, previousReservations }
    },
    onError: (err: unknown, _vars, context) => {
      // Rollback on error
      if (context?.previousEnAttente) {
        queryClient.setQueryData(['reservations-en-attente'], context.previousEnAttente)
      }
      context?.previousReservations?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data)
      })

      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Erreur lors de la validation')
    },
    onSuccess: () => {
      onSuccess?.()
      onClose()
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['reservations'] })
      queryClient.invalidateQueries({ queryKey: ['reservations-en-attente'] })
    },
  })

  const handleValider = useCallback(async () => {
    if (!reservation) return
    setError(null)
    validerMutation.mutate(reservation.id)
  }, [reservation, validerMutation])

  /**
   * TanStack Query Mutation: Refuser une réservation (optimistic update)
   */
  const refuserMutation = useMutation({
    mutationFn: async ({ reservationId, motif }: { reservationId: number; motif?: string }) => {
      return refuserReservation(reservationId, motif)
    },
    onMutate: async ({ reservationId }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['reservations'] })
      await queryClient.cancelQueries({ queryKey: ['reservations-en-attente'] })

      // Snapshot previous data
      const previousEnAttente = queryClient.getQueryData(['reservations-en-attente'])
      const previousReservations = queryClient.getQueriesData({ queryKey: ['reservations'] })

      // Optimistically update: change status to 'refusee'
      queryClient.setQueriesData({ queryKey: ['reservations-en-attente'] }, (old: unknown) => {
        if (!old || typeof old !== 'object' || !('items' in old)) return old
        const data = old as { items: Reservation[] }
        if (!data.items) return old
        return {
          ...data,
          items: data.items.filter((r: Reservation) => r.id !== reservationId),
        }
      })

      queryClient.setQueriesData({ queryKey: ['reservations'] }, (old: unknown) => {
        if (!old || typeof old !== 'object' || !('items' in old)) return old
        const data = old as { items: Reservation[] }
        if (!data.items) return old
        return {
          ...data,
          items: data.items.map((r: Reservation) =>
            r.id === reservationId ? { ...r, statut: 'refusee' as const } : r
          ),
        }
      })

      return { previousEnAttente, previousReservations }
    },
    onError: (err: unknown, _vars, context) => {
      // Rollback on error
      if (context?.previousEnAttente) {
        queryClient.setQueryData(['reservations-en-attente'], context.previousEnAttente)
      }
      context?.previousReservations?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data)
      })

      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Erreur lors du refus')
    },
    onSuccess: () => {
      onSuccess?.()
      onClose()
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['reservations'] })
      queryClient.invalidateQueries({ queryKey: ['reservations-en-attente'] })
    },
  })

  const handleRefuser = useCallback(async () => {
    if (!reservation) return
    setError(null)
    refuserMutation.mutate({ reservationId: reservation.id, motif: motifRefus || undefined })
  }, [reservation, motifRefus, refuserMutation])

  /**
   * TanStack Query Mutation: Annuler une réservation (optimistic update)
   */
  const annulerMutation = useMutation({
    mutationFn: async (reservationId: number) => {
      return annulerReservation(reservationId)
    },
    onMutate: async (reservationId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['reservations'] })

      // Snapshot previous data
      const previousReservations = queryClient.getQueriesData({ queryKey: ['reservations'] })

      // Optimistically update: change status to 'annulee'
      queryClient.setQueriesData({ queryKey: ['reservations'] }, (old: unknown) => {
        if (!old || typeof old !== 'object' || !('items' in old)) return old
        const data = old as { items: Reservation[] }
        if (!data.items) return old
        return {
          ...data,
          items: data.items.map((r: Reservation) =>
            r.id === reservationId ? { ...r, statut: 'annulee' as const } : r
          ),
        }
      })

      return { previousReservations }
    },
    onError: (err: unknown, _vars, context) => {
      // Rollback on error
      context?.previousReservations?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data)
      })

      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || "Erreur lors de l'annulation")
    },
    onSuccess: () => {
      onSuccess?.()
      onClose()
    },
    onSettled: () => {
      // Invalidate to refetch authoritative data
      queryClient.invalidateQueries({ queryKey: ['reservations'] })
    },
  })

  const handleAnnuler = useCallback(async () => {
    if (!reservation) return
    setError(null)
    annulerMutation.mutate(reservation.id)
  }, [reservation, annulerMutation])

  // Aggregate loading state from all mutations
  const loading = createMutation.isPending || validerMutation.isPending || refuserMutation.isPending || annulerMutation.isPending

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
