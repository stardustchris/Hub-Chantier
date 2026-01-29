/**
 * Tests unitaires pour le service apiKeys
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { apiKeysService } from './apiKeys'

// Mock du service api
vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from './api'

describe('apiKeysService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('retourne la liste des cles API', async () => {
      const mockKeys = [
        {
          id: 'key-1',
          key_prefix: 'hc_abc',
          nom: 'Test Key',
          description: null,
          scopes: ['read'],
          rate_limit_per_hour: 100,
          is_active: true,
          last_used_at: null,
          expires_at: null,
          created_at: '2026-01-01T00:00:00Z',
        },
      ]
      vi.mocked(api.get).mockResolvedValue({ data: mockKeys })

      const result = await apiKeysService.list()

      expect(api.get).toHaveBeenCalledWith('/api/auth/api-keys', {
        params: { include_revoked: false },
      })
      expect(result).toEqual(mockKeys)
    })

    it('passe include_revoked=true quand demande', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] })

      await apiKeysService.list(true)

      expect(api.get).toHaveBeenCalledWith('/api/auth/api-keys', {
        params: { include_revoked: true },
      })
    })

    it('passe include_revoked=false par defaut', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] })

      await apiKeysService.list()

      expect(api.get).toHaveBeenCalledWith('/api/auth/api-keys', {
        params: { include_revoked: false },
      })
    })
  })

  describe('create', () => {
    it('cree une nouvelle cle API avec les donnees minimales', async () => {
      const createData = { nom: 'Ma cle' }
      const mockResponse = {
        api_key: 'hc_secret_key_123',
        key_id: 'key-uuid',
        key_prefix: 'hc_sec',
        nom: 'Ma cle',
        created_at: '2026-01-01T00:00:00Z',
        expires_at: null,
      }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const result = await apiKeysService.create(createData)

      expect(api.post).toHaveBeenCalledWith('/api/auth/api-keys', createData)
      expect(result).toEqual(mockResponse)
    })

    it('cree une cle API avec toutes les options', async () => {
      const createData = {
        nom: 'Cle complete',
        description: 'Une description',
        scopes: ['read', 'write'],
        expires_days: 90,
      }
      const mockResponse = {
        api_key: 'hc_full_key',
        key_id: 'key-uuid-2',
        key_prefix: 'hc_ful',
        nom: 'Cle complete',
        created_at: '2026-01-01T00:00:00Z',
        expires_at: '2026-04-01T00:00:00Z',
      }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const result = await apiKeysService.create(createData)

      expect(api.post).toHaveBeenCalledWith('/api/auth/api-keys', createData)
      expect(result).toEqual(mockResponse)
    })

    it('propage les erreurs API', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Network error'))

      await expect(apiKeysService.create({ nom: 'test' })).rejects.toThrow('Network error')
    })
  })

  describe('revoke', () => {
    it('revoque une cle API par son ID', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await apiKeysService.revoke('key-uuid-123')

      expect(api.delete).toHaveBeenCalledWith('/api/auth/api-keys/key-uuid-123')
    })

    it('propage les erreurs API', async () => {
      vi.mocked(api.delete).mockRejectedValue(new Error('Not found'))

      await expect(apiKeysService.revoke('invalid-id')).rejects.toThrow('Not found')
    })
  })
})
