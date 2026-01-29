/**
 * Tests pour APIKeySecretModal
 *
 * Couvre:
 * - Alerte secret une seule fois
 * - Affichage du nom de la cle
 * - Affichage du secret
 * - Bouton Copier / Copie
 * - Actions onCopy et onClose
 * - Instructions d'utilisation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import APIKeySecretModal from './APIKeySecretModal'

describe('APIKeySecretModal', () => {
  const mockOnCopy = vi.fn()
  const mockOnClose = vi.fn()

  const defaultProps = {
    secret: 'hc_sk_abc123def456ghi789',
    keyInfo: {
      key_prefix: 'hc_sk_abc',
      nom: 'Cle de production',
      expires_at: '2026-04-20T10:00:00Z',
    },
    copied: false,
    onCopy: mockOnCopy,
    onClose: mockOnClose,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche l alerte secret une seule fois', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Secret affiché une seule fois/)).toBeInTheDocument()
    expect(screen.getByText(/Copiez ce secret maintenant/)).toBeInTheDocument()
  })

  it('affiche le nom de la cle', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Cle de production')).toBeInTheDocument()
  })

  it('affiche le secret', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('hc_sk_abc123def456ghi789')).toBeInTheDocument()
  })

  it('affiche le bouton Copier quand non copie', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} copied={false} />)

    // Assert
    expect(screen.getByText('Copier')).toBeInTheDocument()
  })

  it('affiche Copie quand copied est true', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} copied={true} />)

    // Assert
    expect(screen.getByText('Copié')).toBeInTheDocument()
  })

  it('appelle onCopy au clic sur Copier', () => {
    // Arrange
    render(<APIKeySecretModal {...defaultProps} />)

    // Act
    fireEvent.click(screen.getByText('Copier'))

    // Assert
    expect(mockOnCopy).toHaveBeenCalledTimes(1)
  })

  it('appelle onClose au clic sur Fermer', () => {
    // Arrange
    render(<APIKeySecretModal {...defaultProps} />)

    // Act
    fireEvent.click(screen.getByText('Fermer'))

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('affiche les instructions d utilisation', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Comment utiliser cette clé/)).toBeInTheDocument()
    expect(screen.getByText(/Authorization: Bearer/)).toBeInTheDocument()
  })

  it('affiche le label Cle API Secret', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Clé API Secret')).toBeInTheDocument()
  })

  it('affiche le titre Cle API creee', () => {
    // Arrange & Act
    render(<APIKeySecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Clé API créée')).toBeInTheDocument()
  })
})
