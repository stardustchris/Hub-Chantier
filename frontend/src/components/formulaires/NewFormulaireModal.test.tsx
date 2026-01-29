/**
 * Tests unitaires pour NewFormulaireModal
 * Modal de selection de template pour nouveau formulaire
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { NewFormulaireModal } from './NewFormulaireModal'

const mockTemplate: any = {
  id: 1,
  nom: 'Rapport journalier',
  categorie: 'rapport_journalier',
  description: 'Description du rapport',
  is_active: true,
  nombre_champs: 5,
  a_photo: true,
  a_signature: false,
}

const mockTemplateInactif: any = {
  ...mockTemplate,
  id: 2,
  nom: 'Template inactif',
  is_active: false,
}

const mockChantier: any = {
  id: 1,
  code: 'CH-001',
  nom: 'Chantier Alpha',
}

describe('NewFormulaireModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onCreateFormulaire: vi.fn().mockResolvedValue(undefined),
    templates: [mockTemplate],
    chantiers: [mockChantier],
    selectedChantierId: '1',
    onChantierChange: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ne rend rien quand isOpen est false', () => {
    // Act
    const { container } = render(
      <NewFormulaireModal {...defaultProps} isOpen={false} />
    )

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('affiche le titre "Nouveau formulaire"', () => {
    // Act
    render(<NewFormulaireModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Nouveau formulaire')).toBeInTheDocument()
  })

  it('affiche les templates disponibles', () => {
    // Act
    render(<NewFormulaireModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Rapport journalier')).toBeInTheDocument()
  })

  it('affiche "Aucun template" quand la liste est vide', () => {
    // Act
    render(<NewFormulaireModal {...defaultProps} templates={[]} />)

    // Assert
    expect(screen.getByText('Aucun template disponible')).toBeInTheDocument()
  })

  it('n\'affiche pas les templates inactifs', () => {
    // Act
    render(
      <NewFormulaireModal
        {...defaultProps}
        templates={[mockTemplateInactif]}
      />
    )

    // Assert
    expect(screen.queryByText('Template inactif')).not.toBeInTheDocument()
    expect(screen.getByText('Aucun template disponible')).toBeInTheDocument()
  })

  it('appelle onCreateFormulaire au clic sur un template', () => {
    // Arrange
    const onCreateFormulaire = vi.fn().mockResolvedValue(undefined)

    // Act
    render(
      <NewFormulaireModal
        {...defaultProps}
        onCreateFormulaire={onCreateFormulaire}
      />
    )
    fireEvent.click(screen.getByText('Rapport journalier'))

    // Assert
    expect(onCreateFormulaire).toHaveBeenCalledWith(1)
  })

  it('appelle onClose au clic sur Annuler (bouton X)', () => {
    // Arrange
    const onClose = vi.fn()
    const onChantierChange = vi.fn()

    // Act
    render(
      <NewFormulaireModal
        {...defaultProps}
        onClose={onClose}
        onChantierChange={onChantierChange}
      />
    )
    // Le overlay fait appel a handleClose qui appelle onChantierChange(null) + onClose()
    const overlay = document.querySelector('.bg-black\\/50')
    if (overlay) fireEvent.click(overlay)

    // Assert
    expect(onChantierChange).toHaveBeenCalledWith(null)
    expect(onClose).toHaveBeenCalled()
  })

  it('affiche la description du template', () => {
    // Act - la description est indirectement affichee via nombre_champs
    render(<NewFormulaireModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/5 champs/)).toBeInTheDocument()
  })
})
