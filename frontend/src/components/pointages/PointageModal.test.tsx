/**
 * Tests pour PointageModal
 *
 * Couvre:
 * - Rendu conditionnel
 * - Mode création vs édition
 * - Affichage statut et motif rejet
 * - Formulaire avec PointageFormFields
 * - Section signature
 * - Actions validateur
 * - Actions footer (supprimer, soumettre, enregistrer)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PointageModal from './PointageModal'
import type { Pointage, Chantier } from '../../types'

// Mock usePointageForm hook
const mockHandleSubmit = vi.fn((e: React.FormEvent) => e.preventDefault())
const mockHandleDelete = vi.fn()
const mockHandleSign = vi.fn()
const mockHandleSubmitForValidation = vi.fn()
const mockHandleValidate = vi.fn()
const mockHandleReject = vi.fn()
const mockSetChantierId = vi.fn()
const mockSetHeuresNormales = vi.fn()
const mockSetHeuresSupplementaires = vi.fn()
const mockSetCommentaire = vi.fn()
const mockSetSignature = vi.fn()
const mockSetShowRejectForm = vi.fn()
const mockSetMotifRejet = vi.fn()

vi.mock('./usePointageForm', () => ({
  usePointageForm: vi.fn(() => ({
    isEditing: false,
    isEditable: true,
    saving: false,
    error: '',
    chantierId: 1,
    heuresNormales: '08:00',
    heuresSupplementaires: '00:00',
    commentaire: '',
    signature: '',
    showRejectForm: false,
    motifRejet: '',
    setChantierId: mockSetChantierId,
    setHeuresNormales: mockSetHeuresNormales,
    setHeuresSupplementaires: mockSetHeuresSupplementaires,
    setCommentaire: mockSetCommentaire,
    setSignature: mockSetSignature,
    setShowRejectForm: mockSetShowRejectForm,
    setMotifRejet: mockSetMotifRejet,
    handleSubmit: mockHandleSubmit,
    handleDelete: mockHandleDelete,
    handleSign: mockHandleSign,
    handleSubmitForValidation: mockHandleSubmitForValidation,
    handleValidate: mockHandleValidate,
    handleReject: mockHandleReject,
  })),
}))

// Mock sub-components
vi.mock('./PointageFormFields', () => ({
  PointageFormFields: ({ isEditable }: { isEditable: boolean }) => (
    <div data-testid="pointage-form-fields">
      Form Fields - {isEditable ? 'Editable' : 'Read-only'}
    </div>
  ),
}))

vi.mock('./SignatureSection', () => ({
  SignatureSection: ({ onSign }: { onSign: () => void }) => (
    <div data-testid="signature-section">
      <button onClick={onSign} data-testid="sign-button">Sign</button>
    </div>
  ),
}))

vi.mock('./ValidatorActions', () => ({
  ValidatorActions: ({
    onValidate,
    onReject,
  }: {
    onValidate: () => void
    onReject: () => void
  }) => (
    <div data-testid="validator-actions">
      <button onClick={onValidate} data-testid="validate-btn">Valider</button>
      <button onClick={onReject} data-testid="reject-btn">Rejeter</button>
    </div>
  ),
}))

import { usePointageForm } from './usePointageForm'
const mockUsePointageForm = usePointageForm as ReturnType<typeof vi.fn>

const createMockPointage = (overrides: Partial<Pointage> = {}): Pointage => ({
  id: 1,
  utilisateur_id: 1,
  chantier_id: 1,
  date_pointage: '2024-01-22',
  heures_normales: '08:00',
  heures_supplementaires: '00:00',
  total_heures: '08:00',
  total_heures_decimal: 8,
  commentaire: '',
  statut: 'brouillon',
  created_at: '2024-01-22T08:00:00',
  updated_at: '2024-01-22T17:00:00',
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

describe('PointageModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSave = vi.fn()

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSave: mockOnSave,
    pointage: null,
    chantiers: [createMockChantier()],
    selectedDate: new Date('2024-01-22'),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUsePointageForm.mockReturnValue({
      isEditing: false,
      isEditable: true,
      saving: false,
      error: '',
      chantierId: 1,
      heuresNormales: '08:00',
      heuresSupplementaires: '00:00',
      commentaire: '',
      signature: '',
      showRejectForm: false,
      motifRejet: '',
      setChantierId: mockSetChantierId,
      setHeuresNormales: mockSetHeuresNormales,
      setHeuresSupplementaires: mockSetHeuresSupplementaires,
      setCommentaire: mockSetCommentaire,
      setSignature: mockSetSignature,
      setShowRejectForm: mockSetShowRejectForm,
      setMotifRejet: mockSetMotifRejet,
      handleSubmit: mockHandleSubmit,
      handleDelete: mockHandleDelete,
      handleSign: mockHandleSign,
      handleSubmitForValidation: mockHandleSubmitForValidation,
      handleValidate: mockHandleValidate,
      handleReject: mockHandleReject,
    })
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<PointageModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouveau pointage')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen est true', () => {
      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Nouveau pointage')).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('affiche "Nouveau pointage" en mode création', () => {
      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Nouveau pointage')).toBeInTheDocument()
    })

    it('affiche "Modifier le pointage" en mode édition', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(<PointageModal {...defaultProps} pointage={createMockPointage()} />)
      expect(screen.getByText('Modifier le pointage')).toBeInTheDocument()
    })

    it('affiche la date sélectionnée', () => {
      render(<PointageModal {...defaultProps} />)
      // Date is formatted with French locale
      expect(screen.getByText(/lundi 22 janvier 2024/i)).toBeInTheDocument()
    })

    it('affiche le badge de statut si pointage existant', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(<PointageModal {...defaultProps} pointage={createMockPointage()} />)
      expect(screen.getByText('Brouillon')).toBeInTheDocument()
    })
  })

  describe('Motif de rejet', () => {
    it('affiche le motif de rejet si présent', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({
            statut: 'rejete',
            motif_rejet: 'Heures incorrectes',
          })}
        />
      )
      expect(screen.getByText('Motif de rejet :')).toBeInTheDocument()
      expect(screen.getByText('Heures incorrectes')).toBeInTheDocument()
    })
  })

  describe('Erreur', () => {
    it('affiche le message d\'erreur', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        error: 'Erreur de validation',
      })

      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Erreur de validation')).toBeInTheDocument()
    })
  })

  describe('Formulaire', () => {
    it('rend PointageFormFields', () => {
      render(<PointageModal {...defaultProps} />)
      expect(screen.getByTestId('pointage-form-fields')).toBeInTheDocument()
    })

    it('passe isEditable à PointageFormFields', () => {
      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Form Fields - Editable')).toBeInTheDocument()
    })
  })

  describe('Section signature', () => {
    it('affiche la section signature pour un brouillon avec onSign', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({ statut: 'brouillon' })}
          onSign={mockOnSign}
        />
      )
      expect(screen.getByTestId('signature-section')).toBeInTheDocument()
    })

    it('n\'affiche pas la section signature si statut != brouillon', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({ statut: 'soumis' })}
          onSign={mockOnSign}
        />
      )
      expect(screen.queryByTestId('signature-section')).not.toBeInTheDocument()
    })
  })

  describe('Actions validateur', () => {
    it('affiche les actions validateur si isValidateur et statut soumis', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({ statut: 'soumis' })}
          isValidateur={true}
        />
      )
      expect(screen.getByTestId('validator-actions')).toBeInTheDocument()
    })

    it('n\'affiche pas les actions si pas validateur', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({ statut: 'soumis' })}
          isValidateur={false}
        />
      )
      expect(screen.queryByTestId('validator-actions')).not.toBeInTheDocument()
    })
  })

  describe('Footer actions', () => {
    it('affiche le bouton Supprimer si pointage existant et éditable', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
        isEditable: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage()}
          onDelete={mockOnDelete}
        />
      )
      expect(screen.getByText('Supprimer')).toBeInTheDocument()
    })

    it('appelle handleDelete au clic sur Supprimer', async () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
        isEditable: true,
      })

      const user = userEvent.setup()
      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage()}
          onDelete={mockOnDelete}
        />
      )

      await user.click(screen.getByText('Supprimer'))
      expect(mockHandleDelete).toHaveBeenCalled()
    })

    it('affiche le bouton Soumettre pour un brouillon', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        isEditing: true,
      })

      render(
        <PointageModal
          {...defaultProps}
          pointage={createMockPointage({ statut: 'brouillon' })}
          onSubmit={mockOnSubmit}
        />
      )
      expect(screen.getByText('Soumettre')).toBeInTheDocument()
    })

    it('affiche le bouton Enregistrer si éditable', () => {
      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Enregistrer')).toBeInTheDocument()
    })

    it('appelle handleSubmit au clic sur Enregistrer', async () => {
      const user = userEvent.setup()
      render(<PointageModal {...defaultProps} />)

      await user.click(screen.getByText('Enregistrer'))
      expect(mockHandleSubmit).toHaveBeenCalled()
    })

    it('désactive les boutons pendant la sauvegarde', () => {
      mockUsePointageForm.mockReturnValue({
        ...mockUsePointageForm(),
        saving: true,
      })

      render(<PointageModal {...defaultProps} />)
      expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<PointageModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<PointageModal {...defaultProps} />)

      const closeButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-x')
      )
      if (closeButton) {
        await user.click(closeButton)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })

    it('appelle onClose au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      render(<PointageModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })
})
