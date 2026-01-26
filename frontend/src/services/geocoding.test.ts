/**
 * Tests pour geocoding.ts
 *
 * Couvre:
 * - Geocoding d'une adresse valide
 * - Adresse non trouvée
 * - Adresse vide
 * - Erreur réseau
 * - Erreur de parsing JSON
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { geocodeAddress } from './geocoding'

describe('geocodeAddress', () => {
  const mockFetch = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch)
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  describe('Adresse valide', () => {
    it('retourne les coordonnées pour une adresse valide', async () => {
      const mockResponse = [
        {
          lat: '45.764043',
          lon: '4.835659',
          display_name: '12 Rue de la République, Lyon, France',
        },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      })

      const result = await geocodeAddress('12 Rue de la République, Lyon')

      expect(result).toEqual({
        latitude: 45.764043,
        longitude: 4.835659,
        displayName: '12 Rue de la République, Lyon, France',
      })
    })

    it('encode correctement l\'adresse dans l\'URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([{ lat: '48.8566', lon: '2.3522', display_name: 'Paris' }]),
      })

      await geocodeAddress('12 Rue de la Paix, Paris')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('12%20Rue%20de%20la%20Paix%2C%20Paris'),
        expect.any(Object)
      )
    })

    it('inclut le User-Agent dans les headers', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([{ lat: '48.8566', lon: '2.3522', display_name: 'Paris' }]),
      })

      await geocodeAddress('Paris')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: {
            'User-Agent': 'HubChantier/1.0',
          },
        })
      )
    })
  })

  describe('Adresse non trouvée', () => {
    it('retourne null si aucun résultat', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      })

      const result = await geocodeAddress('adresse inexistante xyz123')

      expect(result).toBeNull()
    })
  })

  describe('Adresse vide', () => {
    it('retourne null pour une adresse vide', async () => {
      const result = await geocodeAddress('')

      expect(result).toBeNull()
      expect(mockFetch).not.toHaveBeenCalled()
    })

    it('retourne null pour une adresse avec seulement des espaces', async () => {
      const result = await geocodeAddress('   ')

      expect(result).toBeNull()
      expect(mockFetch).not.toHaveBeenCalled()
    })
  })

  describe('Erreurs', () => {
    it('retourne null en cas d\'erreur HTTP', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      const result = await geocodeAddress('Paris')

      expect(result).toBeNull()
      expect(console.error).toHaveBeenCalledWith('Erreur geocoding:', 500)
    })

    it('retourne null en cas d\'erreur réseau', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await geocodeAddress('Paris')

      expect(result).toBeNull()
      expect(console.error).toHaveBeenCalledWith('Erreur geocoding:', expect.any(Error))
    })

    it('retourne null en cas d\'erreur de parsing JSON', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject(new Error('Invalid JSON')),
      })

      const result = await geocodeAddress('Paris')

      expect(result).toBeNull()
    })
  })

  describe('Parsing des coordonnées', () => {
    it('parse correctement les coordonnées en nombre', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([{
          lat: '-33.8688',
          lon: '151.2093',
          display_name: 'Sydney, Australia',
        }]),
      })

      const result = await geocodeAddress('Sydney')

      expect(result).toEqual({
        latitude: -33.8688,
        longitude: 151.2093,
        displayName: 'Sydney, Australia',
      })
    })

    it('prend uniquement le premier résultat', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([
          { lat: '48.8566', lon: '2.3522', display_name: 'Paris, France' },
          { lat: '33.6896', lon: '-84.0245', display_name: 'Paris, Texas, USA' },
        ]),
      })

      const result = await geocodeAddress('Paris')

      expect(result?.displayName).toBe('Paris, France')
    })
  })
})
