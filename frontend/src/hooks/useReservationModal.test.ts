/**
 * Tests pour le hook useReservationModal
 * Gestion des reservations de ressources logistiques
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useReservationModal } from './useReservationModal'
import type { Ressource, Reservation } from '../types/logistique'

// Mocks
vi.mock('../api/logistique', () => ({
  createReservation: vi.fn(),
  validerReservation: vi.fn(),
  refuserReservation: vi.fn(),
  annulerReservation: vi.fn(),
}))

import {
  createReservation,
  validerReservation,
  refuserReservation,
  annulerReservation,
} from '../api/logistique'

const mockRessource: Ressource = {
  id: 1,
  nom: 'Camion Benne',
  type_ressource: 'vehicule',
  description: 'Camion pour transport materiaux',
  disponible: true,
  heure_debut_defaut: '07:00:00',
  heure_fin_defaut: '17:00:00',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
}

const mockReservation: Reservation = {
  id: 1,
  ressource_id: 1,
  chantier_id: 1,
  utilisateur_id: 1,
  date_reservation: '2024-01-15',
  heure_debut: '08:00',
  heure_fin: '12:00',
  statut: 'en_attente',
  commentaire: 'Test reservation',
  created_at: '2024-01-10',
  updated_at: '2024-01-10',
}

describe('useReservationModal', () => {
  const mockOnSuccess = vi.fn()
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('etat initial - mode creation', () => {
    it('initialise avec les valeurs par defaut', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.isViewMode).toBe(false)
      expect(result.current.formData.ressource_id).toBe(mockRessource.id)
      expect(result.current.formData.heure_debut).toBe('07:00')
      expect(result.current.formData.heure_fin).toBe('17:00')
    })

    it('utilise les valeurs initiales fournies', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          initialDate: '2024-02-01',
          initialHeureDebut: '09:00',
          initialHeureFin: '15:00',
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      expect(result.current.formData.date_reservation).toBe('2024-02-01')
      expect(result.current.formData.heure_debut).toBe('09:00')
      expect(result.current.formData.heure_fin).toBe('15:00')
    })
  })

  describe('etat initial - mode vue', () => {
    it('isViewMode est true quand reservation existe', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      expect(result.current.isViewMode).toBe(true)
    })
  })

  describe('setFormData', () => {
    it('met a jour les donnees du formulaire', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      act(() => {
        result.current.setFormData({
          ...result.current.formData,
          chantier_id: 5,
          commentaire: 'Mon commentaire',
        })
      })

      expect(result.current.formData.chantier_id).toBe(5)
      expect(result.current.formData.commentaire).toBe('Mon commentaire')
    })
  })

  describe('motif de refus', () => {
    it('permet de definir le motif de refus', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      expect(result.current.motifRefus).toBe('')

      act(() => {
        result.current.setMotifRefus('Vehicule en panne')
      })

      expect(result.current.motifRefus).toBe('Vehicule en panne')
    })

    it('toggle showMotifRefus', () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      expect(result.current.showMotifRefus).toBe(false)

      act(() => {
        result.current.setShowMotifRefus(true)
      })

      expect(result.current.showMotifRefus).toBe(true)
    })
  })

  describe('handleSubmit', () => {
    it('cree une reservation avec succes', async () => {
      vi.mocked(createReservation).mockResolvedValue({ id: 2 } as Reservation)

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      // Mettre un chantier_id valide
      act(() => {
        result.current.setFormData({
          ...result.current.formData,
          chantier_id: 1,
        })
      })

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(mockEvent.preventDefault).toHaveBeenCalled()
      expect(createReservation).toHaveBeenCalled()
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('affiche erreur si pas de chantier', async () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(result.current.error).toBe('Veuillez sélectionner un chantier')
      expect(createReservation).not.toHaveBeenCalled()
    })

    it('gere erreur 409 conflit', async () => {
      vi.mocked(createReservation).mockRejectedValue({
        response: { status: 409 },
      })

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      act(() => {
        result.current.setFormData({
          ...result.current.formData,
          chantier_id: 1,
        })
      })

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(result.current.error).toBe('Conflit: ce créneau est déjà réservé')
      expect(result.current.loading).toBe(false)
    })

    it('gere erreur generique', async () => {
      vi.mocked(createReservation).mockRejectedValue({
        response: { data: { detail: 'Erreur specifique' } },
      })

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      act(() => {
        result.current.setFormData({
          ...result.current.formData,
          chantier_id: 1,
        })
      })

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(result.current.error).toBe('Erreur specifique')
    })
  })

  describe('handleValider', () => {
    it('valide une reservation avec succes', async () => {
      vi.mocked(validerReservation).mockResolvedValue(undefined)

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleValider()
      })

      expect(validerReservation).toHaveBeenCalledWith(mockReservation.id)
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('ne fait rien sans reservation', async () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleValider()
      })

      expect(validerReservation).not.toHaveBeenCalled()
    })

    it('gere les erreurs', async () => {
      vi.mocked(validerReservation).mockRejectedValue({
        response: { data: { detail: 'Erreur validation' } },
      })

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleValider()
      })

      expect(result.current.error).toBe('Erreur validation')
    })
  })

  describe('handleRefuser', () => {
    it('refuse une reservation avec motif', async () => {
      vi.mocked(refuserReservation).mockResolvedValue(undefined)

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      act(() => {
        result.current.setMotifRefus('Vehicule indisponible')
      })

      await act(async () => {
        await result.current.handleRefuser()
      })

      expect(refuserReservation).toHaveBeenCalledWith(mockReservation.id, 'Vehicule indisponible')
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('refuse sans motif', async () => {
      vi.mocked(refuserReservation).mockResolvedValue(undefined)

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleRefuser()
      })

      expect(refuserReservation).toHaveBeenCalledWith(mockReservation.id, undefined)
    })

    it('ne fait rien sans reservation', async () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleRefuser()
      })

      expect(refuserReservation).not.toHaveBeenCalled()
    })
  })

  describe('handleAnnuler', () => {
    it('annule une reservation avec succes', async () => {
      vi.mocked(annulerReservation).mockResolvedValue(undefined)

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleAnnuler()
      })

      expect(annulerReservation).toHaveBeenCalledWith(mockReservation.id)
      expect(mockOnSuccess).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('ne fait rien sans reservation', async () => {
      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: null,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleAnnuler()
      })

      expect(annulerReservation).not.toHaveBeenCalled()
    })

    it('gere les erreurs', async () => {
      vi.mocked(annulerReservation).mockRejectedValue({
        response: { data: { detail: "Erreur annulation" } },
      })

      const { result } = renderHook(() =>
        useReservationModal({
          isOpen: true,
          ressource: mockRessource,
          reservation: mockReservation,
          onSuccess: mockOnSuccess,
          onClose: mockOnClose,
        })
      )

      await act(async () => {
        await result.current.handleAnnuler()
      })

      expect(result.current.error).toBe("Erreur annulation")
    })
  })

  describe('reinitialisation a l\'ouverture', () => {
    it('reinitialise le formulaire quand modal s\'ouvre en mode creation', () => {
      const { result, rerender } = renderHook(
        ({ isOpen }) =>
          useReservationModal({
            isOpen,
            ressource: mockRessource,
            reservation: null,
            onSuccess: mockOnSuccess,
            onClose: mockOnClose,
          }),
        { initialProps: { isOpen: false } }
      )

      // Modifier les donnees
      act(() => {
        result.current.setFormData({
          ...result.current.formData,
          commentaire: 'Test modified',
        })
      })

      // Ouvrir le modal
      rerender({ isOpen: true })

      // Les donnees devraient etre reinitialises
      expect(result.current.formData.commentaire).toBe('')
    })
  })
})
