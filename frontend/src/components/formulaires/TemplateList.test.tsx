/**
 * Tests unitaires pour TemplateList
 * Liste des templates de formulaires
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TemplateList from './TemplateList'

const mockTemplate: any = {
  id: 1,
  nom: 'Rapport journalier',
  categorie: 'rapport_journalier',
  description: 'Description du template',
  is_active: true,
  nombre_champs: 5,
  a_photo: false,
  a_signature: false,
  champs: [],
}

const mockTemplateInactif: any = {
  ...mockTemplate,
  id: 2,
  nom: 'Template inactif',
  is_active: false,
}

describe('TemplateList', () => {
  const defaultProps = {
    templates: [mockTemplate],
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    onDuplicate: vi.fn(),
    onToggleActive: vi.fn(),
    onPreview: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche "Aucun template" quand la liste est vide', () => {
    // Act
    render(<TemplateList {...defaultProps} templates={[]} />)

    // Assert
    expect(screen.getByText('Aucun template')).toBeInTheDocument()
  })

  it('affiche les templates avec nom et categorie', () => {
    // Act
    render(<TemplateList {...defaultProps} />)

    // Assert
    expect(screen.getByText('Rapport journalier')).toBeInTheDocument()
  })

  it('affiche le badge Actif/Inactif', () => {
    // Arrange - template actif a le toggle "Desactiver", inactif a "Activer"
    render(<TemplateList {...defaultProps} templates={[mockTemplate]} />)

    // Assert
    expect(screen.getByTitle('Desactiver')).toBeInTheDocument()
  })

  it('affiche le title Activer pour template inactif', () => {
    // Act
    render(<TemplateList {...defaultProps} templates={[mockTemplateInactif]} />)

    // Assert
    expect(screen.getByTitle('Activer')).toBeInTheDocument()
  })

  it('appelle onEdit au clic sur Modifier', () => {
    // Arrange
    const onEdit = vi.fn()

    // Act
    render(<TemplateList {...defaultProps} onEdit={onEdit} />)
    fireEvent.click(screen.getByText('Modifier'))

    // Assert
    expect(onEdit).toHaveBeenCalledWith(mockTemplate)
  })

  it('appelle onDelete au clic sur Supprimer', () => {
    // Arrange
    const onDelete = vi.fn()

    // Act
    render(<TemplateList {...defaultProps} onDelete={onDelete} />)
    fireEvent.click(screen.getByTitle('Supprimer'))

    // Assert
    expect(onDelete).toHaveBeenCalledWith(mockTemplate)
  })

  it('appelle onDuplicate au clic sur Dupliquer', () => {
    // Arrange
    const onDuplicate = vi.fn()

    // Act
    render(<TemplateList {...defaultProps} onDuplicate={onDuplicate} />)
    fireEvent.click(screen.getByTitle('Dupliquer'))

    // Assert
    expect(onDuplicate).toHaveBeenCalledWith(mockTemplate)
  })

  it('appelle onToggleActive au clic sur Activer/Desactiver', () => {
    // Arrange
    const onToggleActive = vi.fn()

    // Act
    render(<TemplateList {...defaultProps} onToggleActive={onToggleActive} />)
    fireEvent.click(screen.getByTitle('Desactiver'))

    // Assert
    expect(onToggleActive).toHaveBeenCalledWith(mockTemplate)
  })

  it('affiche le nombre de champs du template', () => {
    // Act
    render(<TemplateList {...defaultProps} />)

    // Assert
    expect(screen.getByText('5 champs')).toBeInTheDocument()
  })
})
