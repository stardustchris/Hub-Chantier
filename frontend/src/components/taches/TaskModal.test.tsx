/**
 * Tests unitaires pour TaskModal
 * Modal de creation/edition de tache
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TaskModal from './TaskModal'

vi.mock('../../types', async () => {
  const actual = await vi.importActual('../../types')
  return actual
})

const mockTache: any = {
  id: 1,
  titre: 'Coffrage voiles',
  description: 'Details',
  date_echeance: '2024-03-15',
  unite_mesure: 'm2',
  quantite_estimee: 100,
  heures_estimees: 40,
}

describe('TaskModal', () => {
  const defaultProps = {
    onClose: vi.fn(),
    onSave: vi.fn().mockResolvedValue(undefined),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche "Nouvelle tache" en mode creation', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Nouvelle tache')).toBeInTheDocument()
  })

  it('affiche "Modifier la tache" en mode edition', () => {
    // Act
    render(<TaskModal {...defaultProps} tache={mockTache} />)

    // Assert
    expect(screen.getByText('Modifier la tache')).toBeInTheDocument()
  })

  it('affiche "Ajouter une sous-tache" avec parentId', () => {
    // Act
    render(<TaskModal {...defaultProps} parentId={5} />)

    // Assert
    expect(screen.getByText('Ajouter une sous-tache')).toBeInTheDocument()
  })

  it('affiche le champ titre', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Titre *')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ex: Coffrage voiles R+1')).toBeInTheDocument()
  })

  it('affiche le champ description', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Details supplementaires...')).toBeInTheDocument()
  })

  it('affiche le champ date echeance', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText("Date d'echeance")).toBeInTheDocument()
  })

  it('affiche le select unite de mesure', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Unite de mesure')).toBeInTheDocument()
    expect(screen.getByText('-- Aucune --')).toBeInTheDocument()
  })

  it('affiche le champ quantite estimee (desactive sans unite)', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Quantite estimee')).toBeInTheDocument()
    // Il y a plusieurs inputs avec placeholder "0" - quantite_estimee est le disabled one
    const allPlaceholder0 = screen.getAllByPlaceholderText('0')
    const disabledInput = allPlaceholder0.find((el) => el.hasAttribute('disabled'))
    expect(disabledInput).toBeTruthy()
  })

  it('affiche le champ heures estimees', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Heures estimees')).toBeInTheDocument()
    expect(screen.getByText('Temps prevu pour realiser cette tache')).toBeInTheDocument()
  })

  it('appelle onSave avec les donnees au submit', async () => {
    // Arrange
    const onSave = vi.fn().mockResolvedValue(undefined)
    render(<TaskModal {...defaultProps} onSave={onSave} />)

    // Act
    const titreInput = screen.getByPlaceholderText('Ex: Coffrage voiles R+1')
    fireEvent.change(titreInput, { target: { value: 'Nouvelle tache test' } })
    fireEvent.submit(titreInput.closest('form')!)

    // Assert
    await waitFor(() => {
      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({ titre: 'Nouvelle tache test' })
      )
    })
  })

  it('appelle onSave avec parent_id pour sous-tache', async () => {
    // Arrange
    const onSave = vi.fn().mockResolvedValue(undefined)
    render(<TaskModal {...defaultProps} onSave={onSave} parentId={10} />)

    // Act
    const titreInput = screen.getByPlaceholderText('Ex: Coffrage voiles R+1')
    fireEvent.change(titreInput, { target: { value: 'Sous-tache' } })
    fireEvent.submit(titreInput.closest('form')!)

    // Assert
    await waitFor(() => {
      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({ titre: 'Sous-tache', parent_id: 10 })
      )
    })
  })

  it('appelle onClose au clic sur Annuler', () => {
    // Arrange
    const onClose = vi.fn()
    render(<TaskModal {...defaultProps} onClose={onClose} />)

    // Act
    fireEvent.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur l\'overlay', () => {
    // Arrange
    const onClose = vi.fn()
    render(<TaskModal {...defaultProps} onClose={onClose} />)

    // Act
    const overlay = document.querySelector('.bg-black\\/50')
    if (overlay) fireEvent.click(overlay)

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('le bouton Creer est desactive quand titre est vide', () => {
    // Act
    render(<TaskModal {...defaultProps} />)

    // Assert
    const creerButton = screen.getByText('Creer')
    expect(creerButton).toBeDisabled()
  })
})
