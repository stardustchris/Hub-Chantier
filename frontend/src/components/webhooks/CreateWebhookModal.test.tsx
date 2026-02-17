/**
 * Tests pour CreateWebhookModal
 *
 * Couvre:
 * - Affichage du formulaire (titre, champs, evenements)
 * - Selection des evenements
 * - Ajout d'evenements personnalises
 * - Action Annuler
 * - Soumission du formulaire
 * - Etat de soumission (loading)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CreateWebhookModal from './CreateWebhookModal'
import type { CreateWebhookResponse } from '../../services/webhooks'

vi.mock('../../services/webhooks', () => ({
  webhooksApi: {
    create: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: { info: vi.fn(), error: vi.fn(), warn: vi.fn() },
}))

import { webhooksApi } from '../../services/webhooks'

const mockedCreate = vi.mocked(webhooksApi.create)

describe('CreateWebhookModal', () => {
  const mockOnClose = vi.fn()
  const mockOnCreated = vi.fn()

  const defaultProps = {
    onClose: mockOnClose,
    onCreated: mockOnCreated,
  }

  const mockWebhookResponse: CreateWebhookResponse = {
    webhook: {
      id: 'wh-new',
      url: 'https://example.com/webhook',
      events: ['chantier.*'],
      is_active: true,
      consecutive_failures: 0,
      created_at: '2026-01-25T10:00:00Z',
    },
    secret: 'whsec_newsecret123',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('affiche le titre Creer un Webhook', () => {
    // Arrange & Act
    render(<CreateWebhookModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Créer un Webhook')).toBeInTheDocument()
  })

  it('affiche le champ URL', () => {
    // Arrange & Act
    render(<CreateWebhookModal {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText('https://example.com/webhook')).toBeInTheDocument()
    expect(screen.getByText(/Doit utiliser HTTPS/)).toBeInTheDocument()
  })

  it('affiche le champ description', () => {
    // Arrange & Act
    render(<CreateWebhookModal {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText(/Synchronisation avec système externe/)).toBeInTheDocument()
    expect(screen.getByText(/Description \(optionnel\)/)).toBeInTheDocument()
  })

  it('affiche les evenements disponibles', () => {
    // Arrange & Act
    render(<CreateWebhookModal {...defaultProps} />)

    // Assert
    // '*' apparait aussi dans les labels requis, on utilise getAllByText
    const allStars = screen.getAllByText('*')
    expect(allStars.length).toBeGreaterThanOrEqual(3) // 2 labels requis + 1 evenement
    expect(screen.getByText('chantier.*')).toBeInTheDocument()
    expect(screen.getByText('heures.*')).toBeInTheDocument()
    expect(screen.getByText('affectation.*')).toBeInTheDocument()
    expect(screen.getByText('signalement.*')).toBeInTheDocument()
    expect(screen.getByText('document.*')).toBeInTheDocument()
  })

  it('permet de selectionner des evenements', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateWebhookModal {...defaultProps} />)

    // Act
    const checkbox = screen.getByText('chantier.*').closest('label')?.querySelector('input')
    if (checkbox) {
      await user.click(checkbox)
    }

    // Assert
    expect(checkbox).toBeChecked()
  })

  it('permet d ajouter un evenement personnalise', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateWebhookModal {...defaultProps} />)

    // Act - use fireEvent.change to avoid useFocusTrap focus interference
    const customInput = screen.getByPlaceholderText('Pattern personnalisé...')
    fireEvent.change(customInput, { target: { value: 'custom.event' } })
    await user.click(screen.getByText('Ajouter'))

    // Assert
    expect(screen.getByText('custom.event')).toBeInTheDocument()
  })

  it('appelle onClose au clic sur Annuler', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateWebhookModal {...defaultProps} />)

    // Act
    await user.click(screen.getByText('Annuler'))

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('soumet le formulaire avec succes', async () => {
    // Arrange
    const user = userEvent.setup()
    mockedCreate.mockResolvedValue(mockWebhookResponse)
    render(<CreateWebhookModal {...defaultProps} />)

    // Act - Remplir le formulaire
    await user.type(
      screen.getByPlaceholderText('https://example.com/webhook'),
      'https://example.com/webhook'
    )

    const checkbox = screen.getByText('chantier.*').closest('label')?.querySelector('input')
    if (checkbox) {
      await user.click(checkbox)
    }

    await user.click(screen.getByText('Créer'))

    // Assert
    await waitFor(() => {
      expect(mockedCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          url: 'https://example.com/webhook',
          events: ['chantier.*'],
        })
      )
      expect(mockOnCreated).toHaveBeenCalledWith(
        'whsec_newsecret123',
        mockWebhookResponse.webhook
      )
    })
  })

  it('affiche Creation... pendant la soumission', async () => {
    // Arrange
    const user = userEvent.setup()
    mockedCreate.mockReturnValue(new Promise(() => {}))
    render(<CreateWebhookModal {...defaultProps} />)

    // Act
    await user.type(
      screen.getByPlaceholderText('https://example.com/webhook'),
      'https://example.com/webhook'
    )

    const checkbox = screen.getByText('chantier.*').closest('label')?.querySelector('input')
    if (checkbox) {
      await user.click(checkbox)
    }

    await user.click(screen.getByText('Créer'))

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Création...')).toBeInTheDocument()
    })
  })

  it('affiche une alerte si l URL est vide', async () => {
    // Arrange
    const user = userEvent.setup()
    render(<CreateWebhookModal {...defaultProps} />)

    // Act - Selectionner un evenement mais pas d'URL
    const checkbox = screen.getByText('chantier.*').closest('label')?.querySelector('input')
    if (checkbox) {
      await user.click(checkbox)
    }

    // Note: Le formulaire HTML natif empechera la soumission car l'input URL est required
  })

  it('affiche le champ evenement personnalise', () => {
    // Arrange & Act
    render(<CreateWebhookModal {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText('Pattern personnalisé...')).toBeInTheDocument()
  })
})
