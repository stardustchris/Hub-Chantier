/**
 * Tests pour ReservationModal
 *
 * Couvre:
 * - Rendu conditionnel
 * - Mode création vs mode vue
 * - Affichage statut réservation
 * - Actions validation/refus (si canValidate)
 * - Formulaire de création
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReservationModal from './ReservationModal'
import type { Ressource, Reservation } from '../../types/logistique'
import type { Chantier } from '../../types'

// Mock useReservationModal hook
const mockHandleSubmit = vi.fn((e: React.FormEvent) => e.preventDefault())
const mockHandleValider = vi.fn()
const mockHandleRefuser = vi.fn()
const mockHandleAnnuler = vi.fn()
const mockSetFormData = vi.fn()
const mockSetMotifRefus = vi.fn()
const mockSetShowMotifRefus = vi.fn()

vi.mock('../../hooks/useReservationModal', () => ({
  useReservationModal: vi.fn(() => ({
    loading: false,
    error: '',
    formData: {
      chantier_id: '',
      date_reservation: '2024-01-25',
      heure_debut: '09:00',
      heure_fin: '12:00',
      commentaire: '',
    },
    motifRefus: '',
    showMotifRefus: false,
    setFormData: mockSetFormData,
    setMotifRefus: mockSetMotifRefus,
    setShowMotifRefus: mockSetShowMotifRefus,
    handleSubmit: mockHandleSubmit,
    handleValider: mockHandleValider,
    handleRefuser: mockHandleRefuser,
    handleAnnuler: mockHandleAnnuler,
    isViewMode: false,
  })),
}))

// Mock sub-components
vi.mock('./ReservationFormFields', () => ({
  default: ({ isViewMode }: { isViewMode: boolean }) => (
    <div data-testid="reservation-form-fields">
      Form Fields - {isViewMode ? 'View Mode' : 'Edit Mode'}
    </div>
  ),
}))

vi.mock('./ReservationActions', () => ({
  default: ({
    isViewMode,
    canValidate,
    onValider,
    onRefuser,
    onClose,
  }: {
    isViewMode: boolean
    canValidate: boolean
    onValider: () => void
    onRefuser: () => void
    onClose: () => void
  }) => (
    <div data-testid="reservation-actions">
      {!isViewMode && (
        <button type="submit" data-testid="submit-button">Créer</button>
      )}
      {isViewMode && canValidate && (
        <>
          <button onClick={onValider} data-testid="validate-button">Valider</button>
          <button onClick={onRefuser} data-testid="refuse-button">Refuser</button>
        </>
      )}
      <button onClick={onClose} data-testid="close-button">Fermer</button>
    </div>
  ),
}))

import { useReservationModal } from '../../hooks/useReservationModal'
const mockUseReservationModal = useReservationModal as ReturnType<typeof vi.fn>

const createMockRessource = (overrides: Partial<Ressource> = {}): Ressource => ({
  id: 1,
  code: 'CAM01',
  nom: 'Camion benne',
  categorie: 'vehicule',
  categorie_label: 'Véhicule',
  couleur: '#FF5733',
  actif: true,
  validation_requise: true,
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
  ...overrides,
})

const createMockReservation = (overrides: Partial<Reservation> = {}): Reservation => ({
  id: 1,
  ressource_id: 1,
  ressource_nom: 'Camion benne',
  ressource_code: 'CAM01',
  ressource_couleur: '#FF5733',
  demandeur_id: 1,
  demandeur_nom: 'Jean Dupont',
  chantier_id: 1,
  chantier_nom: 'Chantier Test',
  date_reservation: '2024-01-25',
  heure_debut: '09:00',
  heure_fin: '12:00',
  statut: 'en_attente',
  statut_label: 'En attente',
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
  ...overrides,
})

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: '1',
  nom: 'Chantier Test',
  code: 'CH001',
  adresse: '123 rue Test',
  statut: 'en_cours',
  couleur: '#3498db',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01T00:00:00',
  ...overrides,
})

describe('ReservationModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSuccess = vi.fn()

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    ressource: createMockRessource(),
    chantiers: [createMockChantier()],
    onSuccess: mockOnSuccess,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseReservationModal.mockReturnValue({
      loading: false,
      error: '',
      formData: {
        chantier_id: '',
        date_reservation: '2024-01-25',
        heure_debut: '09:00',
        heure_fin: '12:00',
        commentaire: '',
      },
      motifRefus: '',
      showMotifRefus: false,
      setFormData: mockSetFormData,
      setMotifRefus: mockSetMotifRefus,
      setShowMotifRefus: mockSetShowMotifRefus,
      handleSubmit: mockHandleSubmit,
      handleValider: mockHandleValider,
      handleRefuser: mockHandleRefuser,
      handleAnnuler: mockHandleAnnuler,
      isViewMode: false,
    })
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<ReservationModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouvelle réservation')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen est true', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByText('Nouvelle réservation')).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('affiche le code et nom de la ressource', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByText('[CAM01] Camion benne')).toBeInTheDocument()
    })

    it('affiche "Nouvelle réservation" en mode création', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByText('Nouvelle réservation')).toBeInTheDocument()
    })

    it('affiche "Détails réservation" en mode vue', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation()}
        />
      )
      expect(screen.getByText('Détails réservation')).toBeInTheDocument()
    })

    it('affiche la couleur de la ressource', () => {
      render(<ReservationModal {...defaultProps} />)
      const colorDiv = document.querySelector('[style*="background-color: rgb(255, 87, 51)"]')
      expect(colorDiv).toBeInTheDocument()
    })
  })

  describe('Statut réservation (mode vue)', () => {
    it('affiche le statut en attente', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation({ statut: 'en_attente' })}
        />
      )
      expect(screen.getByText('En attente')).toBeInTheDocument()
    })

    it('affiche le statut validée', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation({ statut: 'validee' })}
        />
      )
      expect(screen.getByText('Validée')).toBeInTheDocument()
    })

    it('affiche le motif de refus si présent', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation({
            statut: 'refusee',
            motif_refus: 'Ressource déjà réservée',
          })}
        />
      )
      expect(screen.getByText('- Ressource déjà réservée')).toBeInTheDocument()
    })
  })

  describe('Formulaire', () => {
    it('rend ReservationFormFields', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByTestId('reservation-form-fields')).toBeInTheDocument()
    })

    it('passe isViewMode à ReservationFormFields', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByText('Form Fields - Edit Mode')).toBeInTheDocument()
    })

    it('rend ReservationActions', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByTestId('reservation-actions')).toBeInTheDocument()
    })
  })

  describe('Erreur', () => {
    it('affiche le message d\'erreur', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        error: 'Erreur de validation',
      })

      render(<ReservationModal {...defaultProps} />)
      expect(screen.getByText('Erreur de validation')).toBeInTheDocument()
    })
  })

  describe('Message validation requise', () => {
    it('affiche le message si validation requise en mode création', () => {
      render(<ReservationModal {...defaultProps} />)
      expect(
        screen.getByText('Cette ressource nécessite une validation par un responsable')
      ).toBeInTheDocument()
    })

    it('n\'affiche pas le message si pas de validation requise', () => {
      render(
        <ReservationModal
          {...defaultProps}
          ressource={createMockRessource({ validation_requise: false })}
        />
      )
      expect(
        screen.queryByText('Cette ressource nécessite une validation par un responsable')
      ).not.toBeInTheDocument()
    })

    it('n\'affiche pas le message en mode vue', () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation()}
        />
      )
      expect(
        screen.queryByText('Cette ressource nécessite une validation par un responsable')
      ).not.toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('appelle handleSubmit à la soumission du formulaire', async () => {
      const user = userEvent.setup()
      render(<ReservationModal {...defaultProps} />)

      await user.click(screen.getByTestId('submit-button'))
      expect(mockHandleSubmit).toHaveBeenCalled()
    })

    it('appelle handleValider au clic sur Valider (mode vue + canValidate)', async () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      const user = userEvent.setup()
      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation()}
          canValidate={true}
        />
      )

      await user.click(screen.getByTestId('validate-button'))
      expect(mockHandleValider).toHaveBeenCalled()
    })

    it('appelle handleRefuser au clic sur Refuser', async () => {
      mockUseReservationModal.mockReturnValue({
        ...mockUseReservationModal(),
        isViewMode: true,
      })

      const user = userEvent.setup()
      render(
        <ReservationModal
          {...defaultProps}
          reservation={createMockReservation()}
          canValidate={true}
        />
      )

      await user.click(screen.getByTestId('refuse-button'))
      expect(mockHandleRefuser).toHaveBeenCalled()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur le bouton fermer', async () => {
      const user = userEvent.setup()
      render(<ReservationModal {...defaultProps} />)

      await user.click(screen.getByTestId('close-button'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<ReservationModal {...defaultProps} />)

      const closeButton = screen.getByLabelText('Fermer')
      await user.click(closeButton)
      expect(mockOnClose).toHaveBeenCalled()
    })
  })
})
