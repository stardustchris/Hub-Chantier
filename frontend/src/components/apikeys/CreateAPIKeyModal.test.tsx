/**
 * Tests pour CreateAPIKeyModal
 *
 * Couvre:
 * - Affichage du formulaire (titre, champs, scopes)
 * - Scope read selectionne par defaut
 * - Toggle des scopes
 * - Champ expiration avec 90 jours par defaut
 * - Action Annuler
 * - Soumission du formulaire
 * - Etat de soumission (loading)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CreateAPIKeyModal from './CreateAPIKeyModal'
import type { CreateAPIKeyResponse } from '../../services/apiKeys'

vi.mock('../../services/apiKeys', () => ({
  apiKeysService: {
    create: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: { info: vi.fn(), error: vi.fn(), warn: vi.fn() },
}))

import { apiKeysService } from '../../services/apiKeys'

const mockedCreate = vi.mocked(apiKeysService.create)

describe('CreateAPIKeyModal', () => {
  const mockOnClose = vi.fn()
  const mockOnCreated = vi.fn()

  const defaultProps = {
    onClose: mockOnClose,
    onCreated: mockOnCreated,
  }

  const mockCreateResponse: CreateAPIKeyResponse = {
    api_key: 'hc_sk_newsecret123',
    key_id: 'key-123',
    key_prefix: 'hc_sk_new',
    nom: 'Ma cle API',
    created_at: '2026-01-25T10:00:00Z',
    expires_at: '2026-04-25T10:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('affiche le titre Creer une cle API', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Créer une clé API')).toBeInTheDocument()
  })

  it('affiche le champ nom', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText('Clé de production')).toBeInTheDocument()
  })

  it('affiche les scopes disponibles', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('read')).toBeInTheDocument()
    expect(screen.getByText('write')).toBeInTheDocument()
    expect(screen.getByText('chantiers:read')).toBeInTheDocument()
    expect(screen.getByText('chantiers:write')).toBeInTheDocument()
    expect(screen.getByText('planning:read')).toBeInTheDocument()
    expect(screen.getByText('planning:write')).toBeInTheDocument()
    expect(screen.getByText('documents:read')).toBeInTheDocument()
    expect(screen.getByText('documents:write')).toBeInTheDocument()
  })

  it('read est selectionne par defaut', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    const readCheckbox = screen.getByText('read').closest('label')?.querySelector('input')
    expect(readCheckbox).toBeChecked()
  })

  it('permet de toggler les scopes', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Act - Activer write
    const writeCheckbox = screen.getByText('write').closest('label')?.querySelector('input')
    if (writeCheckbox) {
      await user.click(writeCheckbox)
    }

    // Assert
    expect(writeCheckbox).toBeChecked()

    // Act - Desactiver read
    const readCheckbox = screen.getByText('read').closest('label')?.querySelector('input')
    if (readCheckbox) {
      await user.click(readCheckbox)
    }

    // Assert
    expect(readCheckbox).not.toBeChecked()
  })

  it('affiche le champ expiration avec 90 jours par defaut', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    const expirationInput = screen.getByDisplayValue('90')
    expect(expirationInput).toBeInTheDocument()
    expect(screen.getByText(/expirera automatiquement après 90 jours/)).toBeInTheDocument()
  })

  it('appelle onClose au clic sur Annuler', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Act
    await user.click(screen.getByText('Annuler'))

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('soumet le formulaire avec succes', async () => {
    // Arrange
    const user = userEvent.setup()
    mockedCreate.mockResolvedValue(mockCreateResponse)
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Act
    await user.type(screen.getByPlaceholderText('Clé de production'), 'Ma cle API')
    await user.click(screen.getByText('Créer'))

    // Assert
    await waitFor(() => {
      expect(mockedCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          nom: 'Ma cle API',
          scopes: ['read'],
          expires_days: 90,
        })
      )
      expect(mockOnCreated).toHaveBeenCalledWith('hc_sk_newsecret123', {
        key_prefix: 'hc_sk_new',
        nom: 'Ma cle API',
        expires_at: '2026-04-25T10:00:00Z',
      })
    })
  })

  it('affiche Creation... pendant la soumission', async () => {
    // Arrange
    const user = userEvent.setup()
    mockedCreate.mockReturnValue(new Promise(() => {}))
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Act
    await user.type(screen.getByPlaceholderText('Clé de production'), 'Ma cle API')
    await user.click(screen.getByText('Créer'))

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Création...')).toBeInTheDocument()
    })
  })

  it('affiche le champ description', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText(/Utilisée pour le système de synchronisation/)).toBeInTheDocument()
  })

  it('affiche le label Permissions (Scopes)', () => {
    // Arrange & Act
    render(<CreateAPIKeyModal {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Permissions \(Scopes\)/)).toBeInTheDocument()
  })
})
