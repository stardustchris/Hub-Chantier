/**
 * Tests unitaires pour FormulaireList
 * Liste des formulaires remplis
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FormulaireList from './FormulaireList'

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYear: vi.fn().mockReturnValue('15 janv. 2024'),
  formatDateTimeShort: vi.fn().mockReturnValue('15/01/2024 14:30'),
}))

const mockFormulaire: any = {
  id: 1,
  template_nom: 'Rapport journalier',
  template_categorie: 'rapport_journalier',
  statut: 'brouillon',
  chantier_nom: 'Chantier A',
  user_nom: 'Jean Dupont',
  created_at: '2024-01-15',
  est_signe: false,
  photos: [],
  soumis_at: null,
}

describe('FormulaireList', () => {
  const defaultProps = {
    formulaires: [mockFormulaire],
    onView: vi.fn(),
    onEdit: vi.fn(),
    onExportPDF: vi.fn(),
    onValidate: vi.fn(),
    onReject: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le skeleton quand loading est true', () => {
    // Act
    const { container } = render(
      <FormulaireList {...defaultProps} loading={true} />
    )

    // Assert
    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('affiche "Aucun formulaire" quand la liste est vide', () => {
    // Act
    render(<FormulaireList {...defaultProps} formulaires={[]} />)

    // Assert
    expect(screen.getByText('Aucun formulaire')).toBeInTheDocument()
  })

  it('affiche la liste des formulaires', () => {
    // Act
    render(<FormulaireList {...defaultProps} />)

    // Assert
    expect(screen.getByText('Rapport journalier')).toBeInTheDocument()
  })

  it('affiche le nom du template', () => {
    // Act
    render(<FormulaireList {...defaultProps} />)

    // Assert
    expect(screen.getByText('Rapport journalier')).toBeInTheDocument()
  })

  it('affiche le statut du formulaire', () => {
    // Act
    render(<FormulaireList {...defaultProps} />)

    // Assert
    // Le statut est affiche via STATUTS_FORMULAIRE[formulaire.statut].label ou le statut brut
    const statusElement = screen.getByText((content) =>
      content.toLowerCase().includes('brouillon')
    )
    expect(statusElement).toBeInTheDocument()
  })

  it('affiche le chantier et l\'utilisateur', () => {
    // Act
    render(<FormulaireList {...defaultProps} />)

    // Assert
    expect(screen.getByText('Chantier A')).toBeInTheDocument()
    expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
  })

  it('affiche le bouton Modifier pour les brouillons', () => {
    // Act
    render(<FormulaireList {...defaultProps} />)

    // Assert
    expect(screen.getByTitle('Modifier')).toBeInTheDocument()
  })

  it('affiche les boutons Valider/Refuser pour les formulaires soumis', () => {
    // Arrange
    const formulaireSoumis: any = { ...mockFormulaire, statut: 'soumis' }

    // Act
    render(<FormulaireList {...defaultProps} formulaires={[formulaireSoumis]} />)

    // Assert
    expect(screen.getByTitle('Valider')).toBeInTheDocument()
    expect(screen.getByTitle('Refuser')).toBeInTheDocument()
  })

  it('appelle onView au clic sur un formulaire', () => {
    // Arrange
    const onView = vi.fn()

    // Act
    render(<FormulaireList {...defaultProps} onView={onView} />)
    fireEvent.click(screen.getByText('Rapport journalier'))

    // Assert
    expect(onView).toHaveBeenCalledWith(mockFormulaire)
  })

  it('appelle onEdit au clic sur Modifier', () => {
    // Arrange
    const onEdit = vi.fn()

    // Act
    render(<FormulaireList {...defaultProps} onEdit={onEdit} />)
    fireEvent.click(screen.getByTitle('Modifier'))

    // Assert
    expect(onEdit).toHaveBeenCalledWith(mockFormulaire)
  })

  it('appelle onExportPDF au clic sur Telecharger PDF', () => {
    // Arrange
    const onExportPDF = vi.fn()

    // Act
    render(<FormulaireList {...defaultProps} onExportPDF={onExportPDF} />)
    fireEvent.click(screen.getByTitle('Telecharger PDF'))

    // Assert
    expect(onExportPDF).toHaveBeenCalledWith(mockFormulaire)
  })

  it('affiche le badge Signe pour les formulaires signes', () => {
    // Arrange
    const formulaireSigne: any = { ...mockFormulaire, est_signe: true }

    // Act
    render(<FormulaireList {...defaultProps} formulaires={[formulaireSigne]} />)

    // Assert
    expect(screen.getByText('Signe')).toBeInTheDocument()
  })

  it('affiche le nombre de photos', () => {
    // Arrange
    const formulaireAvecPhotos: any = {
      ...mockFormulaire,
      photos: [{ id: 1 }, { id: 2 }, { id: 3 }],
    }

    // Act
    render(<FormulaireList {...defaultProps} formulaires={[formulaireAvecPhotos]} />)

    // Assert
    expect(screen.getByText('3 photos')).toBeInTheDocument()
  })
})
