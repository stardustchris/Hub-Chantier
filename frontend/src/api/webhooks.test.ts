/**
 * Tests unitaires pour l'API Webhooks
 * Gestion des webhooks pour les evenements temps reel
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { webhooksApi } from './webhooks'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from '../services/api'

const mockedApi = api as {
  get: ReturnType<typeof vi.fn>
  post: ReturnType<typeof vi.fn>
  delete: ReturnType<typeof vi.fn>
}

describe('webhooksApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('appelle GET /api/v1/webhooks et retourne les webhooks', async () => {
      // Arrange
      const mockWebhooks = [
        { id: 'wh-1', url: 'https://example.com/hook', events: ['chantier.created'], is_active: true },
        { id: 'wh-2', url: 'https://example.com/hook2', events: ['tache.updated'], is_active: false },
      ]
      mockedApi.get.mockResolvedValue({ data: mockWebhooks })

      // Act
      const result = await webhooksApi.list()

      // Assert
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/webhooks')
      expect(result).toEqual(mockWebhooks)
    })
  })

  describe('create', () => {
    it('appelle POST /api/v1/webhooks avec les donnees et retourne le webhook + secret', async () => {
      // Arrange
      const createData = {
        url: 'https://example.com/hook',
        events: ['chantier.created', 'tache.updated'],
        description: 'Mon webhook',
      }
      const mockResponse = {
        webhook: { id: 'wh-new', ...createData, is_active: true, consecutive_failures: 0, created_at: '2024-01-15' },
        secret: 'whsec_abc123secret',
      }
      mockedApi.post.mockResolvedValue({ data: mockResponse })

      // Act
      const result = await webhooksApi.create(createData)

      // Assert
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/webhooks', createData)
      expect(result).toEqual(mockResponse)
      expect(result.secret).toBe('whsec_abc123secret')
    })
  })

  describe('delete', () => {
    it('appelle DELETE /api/v1/webhooks/{id}', async () => {
      // Arrange
      const webhookId = 'wh-123'
      mockedApi.delete.mockResolvedValue({})

      // Act
      await webhooksApi.delete(webhookId)

      // Assert
      expect(mockedApi.delete).toHaveBeenCalledWith('/api/v1/webhooks/wh-123')
    })
  })

  describe('test', () => {
    it('appelle POST /api/v1/webhooks/{id}/test', async () => {
      // Arrange
      const webhookId = 'wh-456'
      mockedApi.post.mockResolvedValue({})

      // Act
      await webhooksApi.test(webhookId)

      // Assert
      expect(mockedApi.post).toHaveBeenCalledWith('/api/v1/webhooks/wh-456/test')
    })
  })

  describe('deliveries', () => {
    it('appelle GET /api/v1/webhooks/{id}/deliveries?limit=50 par defaut', async () => {
      // Arrange
      const webhookId = 'wh-789'
      const mockDeliveries = [
        { id: 'del-1', webhook_id: webhookId, event_type: 'chantier.created', attempt: 1, success: true, delivered_at: '2024-01-15' },
      ]
      mockedApi.get.mockResolvedValue({ data: mockDeliveries })

      // Act
      const result = await webhooksApi.deliveries(webhookId)

      // Assert
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/webhooks/wh-789/deliveries?limit=50')
      expect(result).toEqual(mockDeliveries)
    })

    it('appelle GET /api/v1/webhooks/{id}/deliveries avec un limit personnalise', async () => {
      // Arrange
      const webhookId = 'wh-789'
      mockedApi.get.mockResolvedValue({ data: [] })

      // Act
      await webhooksApi.deliveries(webhookId, 10)

      // Assert
      expect(mockedApi.get).toHaveBeenCalledWith('/api/v1/webhooks/wh-789/deliveries?limit=10')
    })
  })
})
