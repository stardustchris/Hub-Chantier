/**
 * Tests unitaires pour TraiterModal
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TraiterModal from './TraiterModal'

describe('TraiterModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn().mockResolvedValue(undefined),
    isLoading: false,
  }

  it('ne rend rien quand isOpen est false', () => {
    // Arrange & Act
    const { container } = render(
      <TraiterModal {...defaultProps} isOpen={false} />
    )

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('affiche le titre "Marquer comme traite"', () => {
    // Arrange & Act
    render(<TraiterModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
  })

  it('affiche le textarea pour le commentaire', () => {
    // Arrange & Act
    render(<TraiterModal {...defaultProps} />)

    // Assert
    const textarea = screen.getByPlaceholderText(/Décrivez comment le problème a été résolu/)
    expect(textarea).toBeInTheDocument()
  })

  it('le bouton Confirmer est desactive quand le commentaire est vide', () => {
    // Arrange & Act
    render(<TraiterModal {...defaultProps} />)

    // Assert
    const button = screen.getByText('Confirmer')
    expect(button).toBeDisabled()
  })

  it('le bouton Confirmer est desactive quand isLoading est true', () => {
    // Arrange & Act
    render(<TraiterModal {...defaultProps} isLoading={true} />)

    // Assert
    const button = screen.getByText('Traitement...')
    expect(button).toBeDisabled()
  })

  it('affiche "Traitement..." quand isLoading est true', () => {
    // Arrange & Act
    render(<TraiterModal {...defaultProps} isLoading={true} />)

    // Assert
    expect(screen.getByText('Traitement...')).toBeInTheDocument()
  })

  it('appelle onConfirm avec le commentaire au clic', async () => {
    // Arrange
    const onConfirm = vi.fn().mockResolvedValue(undefined)
    render(<TraiterModal {...defaultProps} onConfirm={onConfirm} />)
    const user = userEvent.setup()

    // Act
    const textarea = screen.getByPlaceholderText(/Décrivez comment le problème a été résolu/)
    await user.type(textarea, 'Probleme resolu')
    const button = screen.getByText('Confirmer')
    await user.click(button)

    // Assert
    expect(onConfirm).toHaveBeenCalledWith('Probleme resolu')
  })

  it('appelle onClose au clic sur Annuler', async () => {
    // Arrange
    const onClose = vi.fn()
    render(<TraiterModal {...defaultProps} onClose={onClose} />)
    const user = userEvent.setup()

    // Act
    await user.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur l\'overlay', () => {
    // Arrange
    const onClose = vi.fn()
    render(<TraiterModal {...defaultProps} onClose={onClose} />)

    // Act
    const overlayDiv = document.querySelector('[aria-hidden="true"]')!
    fireEvent.click(overlayDiv)

    // Assert
    expect(onClose).toHaveBeenCalled()
  })
})
