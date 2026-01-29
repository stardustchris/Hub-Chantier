/**
 * Tests unitaires pour TemplateModal
 * Modal de creation/edition de template
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TemplateModal from './TemplateModal'
import { useTemplateForm } from './useTemplateForm'

vi.mock('./useTemplateForm', () => ({
  useTemplateForm: vi.fn(),
}))

vi.mock('./ChampEditor', () => ({
  ChampEditor: ({ champ, index }: any) => <div data-testid={`champ-editor-${index}`}>{champ.label}</div>,
}))

const mockUseTemplateForm = useTemplateForm as ReturnType<typeof vi.fn>

const defaultFormReturn = {
  formData: {
    nom: '',
    categorie: 'autre',
    description: '',
    champs: [],
  },
  isEditing: false,
  isSubmitting: false,
  error: '',
  expandedChamp: null,
  handleSubmit: vi.fn(),
  addChamp: vi.fn(),
  updateChamp: vi.fn(),
  removeChamp: vi.fn(),
  moveChamp: vi.fn(),
  setExpandedChamp: vi.fn(),
  updateFormField: vi.fn(),
}

describe('TemplateModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onSave: vi.fn(),
    template: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockUseTemplateForm.mockReturnValue(defaultFormReturn)
  })

  it('ne rend rien quand isOpen est false', () => {
    // Arrange & Act
    const { container } = render(
      <TemplateModal {...defaultProps} isOpen={false} />
    )

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('affiche "Nouveau template" en mode creation', () => {
    // Arrange
    mockUseTemplateForm.mockReturnValue({ ...defaultFormReturn, isEditing: false })

    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Nouveau template')).toBeInTheDocument()
  })

  it('affiche "Modifier le template" en mode edition', () => {
    // Arrange
    mockUseTemplateForm.mockReturnValue({ ...defaultFormReturn, isEditing: true })

    // Act
    render(<TemplateModal {...defaultProps} template={{ id: 1 } as any} />)

    // Assert
    expect(screen.getByText('Modifier le template')).toBeInTheDocument()
  })

  it('affiche le champ nom', () => {
    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Nom du template')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ex: Rapport journalier')).toBeInTheDocument()
  })

  it('affiche le select categorie', () => {
    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Categorie')).toBeInTheDocument()
  })

  it('affiche le textarea description', () => {
    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Description du template...')).toBeInTheDocument()
  })

  it('affiche "Aucun champ defini" quand pas de champs', () => {
    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Aucun champ defini')).toBeInTheDocument()
  })

  it('affiche les champs existants via ChampEditor', () => {
    // Arrange
    mockUseTemplateForm.mockReturnValue({
      ...defaultFormReturn,
      formData: {
        ...defaultFormReturn.formData,
        champs: [
          { nom: 'c1', label: 'Champ 1', type_champ: 'texte', obligatoire: false, ordre: 0, placeholder: '', options: [] },
          { nom: 'c2', label: 'Champ 2', type_champ: 'texte', obligatoire: false, ordre: 1, placeholder: '', options: [] },
        ],
      },
    })

    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByTestId('champ-editor-0')).toBeInTheDocument()
    expect(screen.getByTestId('champ-editor-1')).toBeInTheDocument()
    expect(screen.getByText('Champ 1')).toBeInTheDocument()
    expect(screen.getByText('Champ 2')).toBeInTheDocument()
  })

  it('affiche le bouton "Ajouter un champ"', () => {
    // Act
    render(<TemplateModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Ajouter un champ')).toBeInTheDocument()
  })

  it('appelle onClose au clic sur Annuler', () => {
    // Arrange
    const onClose = vi.fn()

    // Act
    render(<TemplateModal {...defaultProps} onClose={onClose} />)
    fireEvent.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('appelle handleSubmit au clic sur Creer', () => {
    // Arrange
    const handleSubmit = vi.fn()
    mockUseTemplateForm.mockReturnValue({ ...defaultFormReturn, handleSubmit })

    // Act
    render(<TemplateModal {...defaultProps} />)
    fireEvent.click(screen.getByText('Creer'))

    // Assert
    expect(handleSubmit).toHaveBeenCalled()
  })
})
