/**
 * Tests unitaires pour chantiersService
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { chantiersService } from './chantiers'
import api from './api'

// Mock the api module
vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockApi = api as unknown as {
  get: ReturnType<typeof vi.fn>
  post: ReturnType<typeof vi.fn>
  put: ReturnType<typeof vi.fn>
  delete: ReturnType<typeof vi.fn>
}

describe('chantiersService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('charge la liste des chantiers sans parametres', async () => {
      const mockResponse = {
        data: {
          items: [{ id: '1', nom: 'Chantier 1' }],
          total: 1,
          page: 1,
          size: 12,
          pages: 1,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await chantiersService.list()

      expect(mockApi.get).toHaveBeenCalledWith('/api/chantiers', { params: {} })
      expect(result.items).toHaveLength(1)
      expect(result.items[0].nom).toBe('Chantier 1')
    })

    it('charge la liste avec parametres de pagination', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 2,
          size: 10,
          pages: 0,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      await chantiersService.list({ page: 2, size: 10 })

      expect(mockApi.get).toHaveBeenCalledWith('/api/chantiers', {
        params: { page: 2, size: 10 },
      })
    })

    it('charge la liste avec filtre de statut', async () => {
      const mockResponse = {
        data: {
          items: [{ id: '1', statut: 'en_cours' }],
          total: 1,
          page: 1,
          size: 12,
          pages: 1,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      await chantiersService.list({ statut: 'en_cours' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/chantiers', {
        params: { statut: 'en_cours' },
      })
    })

    it('charge la liste avec recherche', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 12,
          pages: 0,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      await chantiersService.list({ search: 'test' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/chantiers', {
        params: { search: 'test' },
      })
    })
  })

  describe('getById', () => {
    it('charge un chantier par son ID', async () => {
      const mockChantier = { id: '123', nom: 'Test Chantier' }
      mockApi.get.mockResolvedValue({ data: mockChantier })

      const result = await chantiersService.getById('123')

      expect(mockApi.get).toHaveBeenCalledWith('/api/chantiers/123')
      expect(result.id).toBe('123')
      expect(result.nom).toBe('Test Chantier')
    })
  })

  describe('create', () => {
    it('cree un nouveau chantier', async () => {
      const newChantier = {
        nom: 'Nouveau Chantier',
        client_nom: 'Client Test',
        adresse: '123 Rue Test',
      }
      const mockResponse = { id: '456', ...newChantier }
      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await chantiersService.create(newChantier)

      expect(mockApi.post).toHaveBeenCalledWith('/api/chantiers', newChantier)
      expect(result.id).toBe('456')
      expect(result.nom).toBe('Nouveau Chantier')
    })
  })

  describe('update', () => {
    it('met a jour un chantier existant', async () => {
      const updateData = { nom: 'Chantier Modifie' }
      const mockResponse = { id: '123', nom: 'Chantier Modifie' }
      mockApi.put.mockResolvedValue({ data: mockResponse })

      const result = await chantiersService.update('123', updateData)

      expect(mockApi.put).toHaveBeenCalledWith('/api/chantiers/123', updateData)
      expect(result.nom).toBe('Chantier Modifie')
    })
  })

  describe('delete', () => {
    it('supprime un chantier', async () => {
      mockApi.delete.mockResolvedValue({})

      await chantiersService.delete('123')

      expect(mockApi.delete).toHaveBeenCalledWith('/api/chantiers/123')
    })
  })

  describe('changeStatut', () => {
    it('change le statut d\'un chantier', async () => {
      const mockResponse = { id: '123', statut: 'en_cours' }
      mockApi.post.mockResolvedValue({ data: mockResponse })

      const result = await chantiersService.changeStatut('123', 'en_cours')

      expect(mockApi.post).toHaveBeenCalledWith('/api/chantiers/123/statut', {
        statut: 'en_cours',
      })
      expect(result.statut).toBe('en_cours')
    })
  })

  describe('getNavigationIds', () => {
    it('retourne les IDs precedent et suivant', async () => {
      const mockResponse = {
        data: {
          items: [
            { id: 'a' },
            { id: 'b' },
            { id: 'c' },
          ],
          total: 3,
          page: 1,
          size: 500,
          pages: 1,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await chantiersService.getNavigationIds('b')

      expect(result.prevId).toBe('a')
      expect(result.nextId).toBe('c')
    })

    it('retourne null pour prevId si premier element', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 'a' }, { id: 'b' }],
          total: 2,
          page: 1,
          size: 500,
          pages: 1,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await chantiersService.getNavigationIds('a')

      expect(result.prevId).toBeNull()
      expect(result.nextId).toBe('b')
    })

    it('retourne null pour nextId si dernier element', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 'a' }, { id: 'b' }],
          total: 2,
          page: 1,
          size: 500,
          pages: 1,
        },
      }
      mockApi.get.mockResolvedValue(mockResponse)

      const result = await chantiersService.getNavigationIds('b')

      expect(result.prevId).toBe('a')
      expect(result.nextId).toBeNull()
    })

    it('retourne null pour les deux si erreur', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      const result = await chantiersService.getNavigationIds('123')

      expect(result.prevId).toBeNull()
      expect(result.nextId).toBeNull()
    })
  })

  describe('getWazeUrl', () => {
    it('genere l\'URL Waze correctement', () => {
      const url = chantiersService.getWazeUrl(48.8566, 2.3522)

      expect(url).toBe('https://waze.com/ul?ll=48.8566,2.3522&navigate=yes')
    })
  })

  describe('getGoogleMapsUrl', () => {
    it('genere l\'URL Google Maps correctement', () => {
      const url = chantiersService.getGoogleMapsUrl(48.8566, 2.3522)

      expect(url).toBe(
        'https://www.google.com/maps/dir/?api=1&destination=48.8566,2.3522'
      )
    })
  })
})
