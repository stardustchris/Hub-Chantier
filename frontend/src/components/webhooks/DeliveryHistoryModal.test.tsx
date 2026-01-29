/**
 * Tests pour DeliveryHistoryModal
 *
 * Couvre:
 * - Affichage du titre et URL
 * - Loader pendant le chargement
 * - Message vide quand pas de deliveries
 * - Affichage des deliveries avec succes
 * - Affichage des deliveries en echec
 * - Badge tentative pour les retries
 * - Action onClose
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DeliveryHistoryModal from './DeliveryHistoryModal'
import type { Webhook, WebhookDelivery } from '../../api/webhooks'

vi.mock('../../api/webhooks', () => ({
  webhooksApi: {
    deliveries: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: { info: vi.fn(), error: vi.fn(), warn: vi.fn() },
}))

import { webhooksApi } from '../../api/webhooks'

const mockedDeliveries = vi.mocked(webhooksApi.deliveries)

describe('DeliveryHistoryModal', () => {
  const mockOnClose = vi.fn()

  const mockWebhook: Webhook = {
    id: 'wh-123',
    url: 'https://example.com/webhook',
    events: ['chantier.*'],
    is_active: true,
    consecutive_failures: 0,
    created_at: '2026-01-20T10:00:00Z',
  }

  const defaultProps = {
    webhook: mockWebhook,
    onClose: mockOnClose,
  }

  const mockDeliverySuccess: WebhookDelivery = {
    id: 'del-1',
    webhook_id: 'wh-123',
    event_type: 'chantier.created',
    attempt: 1,
    success: true,
    status_code: 200,
    response_time_ms: 150,
    delivered_at: '2026-01-25T14:30:00Z',
  }

  const mockDeliveryFailure: WebhookDelivery = {
    id: 'del-2',
    webhook_id: 'wh-123',
    event_type: 'chantier.updated',
    attempt: 3,
    success: false,
    status_code: 500,
    response_time_ms: 5000,
    error_message: 'Internal Server Error',
    delivered_at: '2026-01-25T15:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le titre et l URL du webhook', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Historique des Deliveries')).toBeInTheDocument()
    expect(screen.getByText('https://example.com/webhook')).toBeInTheDocument()
  })

  it('affiche le loader pendant le chargement', () => {
    // Arrange
    mockedDeliveries.mockReturnValue(new Promise(() => {}))

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('affiche le message vide quand pas de deliveries', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Aucune delivery pour ce webhook')).toBeInTheDocument()
    })
  })

  it('affiche les deliveries avec succes', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([mockDeliverySuccess])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('chantier.created')).toBeInTheDocument()
      expect(screen.getByText('200')).toBeInTheDocument()
      expect(screen.getByText('150 ms')).toBeInTheDocument()
      expect(screen.getByText('Succès')).toBeInTheDocument()
    })
  })

  it('affiche les deliveries en echec avec message d erreur', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([mockDeliveryFailure])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('chantier.updated')).toBeInTheDocument()
      expect(screen.getByText('Internal Server Error')).toBeInTheDocument()
      expect(screen.getByText('500')).toBeInTheDocument()
    })
  })

  it('affiche le badge tentative pour les retries', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([mockDeliveryFailure])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Tentative 3')).toBeInTheDocument()
    })
  })

  it('ne affiche pas le badge tentative pour attempt 1', async () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([mockDeliverySuccess])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('chantier.created')).toBeInTheDocument()
    })
    expect(screen.queryByText(/Tentative/)).not.toBeInTheDocument()
  })

  it('appelle onClose au clic sur Fermer', async () => {
    // Arrange
    const user = userEvent.setup()
    mockedDeliveries.mockResolvedValue([])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)
    await waitFor(() => {
      expect(screen.getByText('Aucune delivery pour ce webhook')).toBeInTheDocument()
    })
    await user.click(screen.getByText('Fermer'))

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('appelle webhooksApi.deliveries avec le bon ID', () => {
    // Arrange
    mockedDeliveries.mockResolvedValue([])

    // Act
    render(<DeliveryHistoryModal {...defaultProps} />)

    // Assert
    expect(mockedDeliveries).toHaveBeenCalledWith('wh-123')
  })
})
