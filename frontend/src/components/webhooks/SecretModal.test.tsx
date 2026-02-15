/**
 * Tests pour SecretModal
 *
 * Couvre:
 * - Affichage du secret
 * - Message de succes
 * - Alerte de copie
 * - Details du webhook (URL, evenements)
 * - Bouton Copier / Copie
 * - Actions onCopy et onClose
 * - Documentation HMAC
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import SecretModal from './SecretModal'
import type { Webhook } from '../../services/webhooks'

describe('SecretModal', () => {
  const mockOnCopy = vi.fn()
  const mockOnClose = vi.fn()

  const mockWebhook: Webhook = {
    id: 'wh-123',
    url: 'https://example.com/webhook',
    events: ['chantier.*', 'heures.*'],
    description: 'Mon webhook de test',
    is_active: true,
    consecutive_failures: 0,
    created_at: '2026-01-20T10:00:00Z',
  }

  const defaultProps = {
    secret: 'whsec_abc123def456',
    webhook: mockWebhook,
    copied: false,
    onCopy: mockOnCopy,
    onClose: mockOnClose,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le secret', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('whsec_abc123def456')).toBeInTheDocument()
  })

  it('affiche le message de succes', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Webhook créé avec succès/)).toBeInTheDocument()
  })

  it('affiche l alerte de copie', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/copiez-le maintenant/i)).toBeInTheDocument()
  })

  it('affiche les details du webhook - URL', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('https://example.com/webhook')).toBeInTheDocument()
  })

  it('affiche les details du webhook - evenements', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('chantier.*, heures.*')).toBeInTheDocument()
  })

  it('affiche le bouton Copier quand non copie', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} copied={false} />)

    // Assert
    expect(screen.getByText('Copier')).toBeInTheDocument()
  })

  it('affiche le bouton Copie quand copie', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} copied={true} />)

    // Assert
    expect(screen.getByText('Copié')).toBeInTheDocument()
  })

  it('appelle onCopy au clic sur Copier', () => {
    // Arrange
    render(<SecretModal {...defaultProps} />)

    // Act
    fireEvent.click(screen.getByText('Copier'))

    // Assert
    expect(mockOnCopy).toHaveBeenCalledTimes(1)
  })

  it('appelle onClose au clic sur Fermer', () => {
    // Arrange
    render(<SecretModal {...defaultProps} />)

    // Act
    fireEvent.click(screen.getByText('Fermer'))

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('affiche la documentation HMAC', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Vérification de signature HMAC-SHA256/)).toBeInTheDocument()
    expect(screen.getByText(/x-webhook-signature/)).toBeInTheDocument()
  })

  it('affiche le label Secret Webhook', () => {
    // Arrange & Act
    render(<SecretModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Secret Webhook')).toBeInTheDocument()
  })
})
