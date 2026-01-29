/**
 * Tests pour le service CSRF
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  requiresCsrf,
  getCsrfToken,
  clearCsrfToken,
  CSRF_HEADER,
  CSRF_METHODS,
} from './csrf'

// Mock api module
vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
  },
}))

describe('csrf service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    clearCsrfToken()
  })

  describe('CSRF_HEADER', () => {
    it('a la bonne valeur', () => {
      expect(CSRF_HEADER).toBe('X-CSRF-Token')
    })
  })

  describe('CSRF_METHODS', () => {
    it('inclut toutes les méthodes mutables', () => {
      expect(CSRF_METHODS).toContain('POST')
      expect(CSRF_METHODS).toContain('PUT')
      expect(CSRF_METHODS).toContain('DELETE')
      expect(CSRF_METHODS).toContain('PATCH')
    })

    it('ne contient pas GET', () => {
      expect(CSRF_METHODS).not.toContain('GET')
    })
  })

  describe('requiresCsrf', () => {
    it('retourne true pour POST', () => {
      expect(requiresCsrf('POST')).toBe(true)
      expect(requiresCsrf('post')).toBe(true)
    })

    it('retourne true pour PUT', () => {
      expect(requiresCsrf('PUT')).toBe(true)
      expect(requiresCsrf('put')).toBe(true)
    })

    it('retourne true pour DELETE', () => {
      expect(requiresCsrf('DELETE')).toBe(true)
      expect(requiresCsrf('delete')).toBe(true)
    })

    it('retourne true pour PATCH', () => {
      expect(requiresCsrf('PATCH')).toBe(true)
      expect(requiresCsrf('patch')).toBe(true)
    })

    it('retourne false pour GET', () => {
      expect(requiresCsrf('GET')).toBe(false)
      expect(requiresCsrf('get')).toBe(false)
    })

    it('retourne false pour HEAD', () => {
      expect(requiresCsrf('HEAD')).toBe(false)
    })

    it('retourne false pour OPTIONS', () => {
      expect(requiresCsrf('OPTIONS')).toBe(false)
    })
  })

  describe('getCsrfToken', () => {
    it('retourne null si aucun token n\'a été récupéré', () => {
      expect(getCsrfToken()).toBeNull()
    })
  })

  describe('clearCsrfToken', () => {
    it('efface le token', () => {
      // Note: We can't easily test fetchCsrfToken without more complex mocking
      // This test just ensures clearCsrfToken doesn't throw
      clearCsrfToken()
      expect(getCsrfToken()).toBeNull()
    })
  })

  describe('fetchCsrfToken', () => {
    it('récupère le token depuis le backend', async () => {
      const { fetchCsrfToken } = await import('./csrf')
      const api = await import('./api')

      vi.mocked(api.default.get).mockResolvedValue({
        data: { csrf_token: 'test-csrf-token-123' },
      })

      clearCsrfToken()
      const token = await fetchCsrfToken()

      expect(token).toBe('test-csrf-token-123')
      expect(api.default.get).toHaveBeenCalledWith('/api/csrf-token')
    })

    it('retourne le token en cache si déjà récupéré', async () => {
      const { fetchCsrfToken } = await import('./csrf')
      const api = await import('./api')

      vi.mocked(api.default.get).mockResolvedValue({
        data: { csrf_token: 'cached-token' },
      })

      clearCsrfToken()
      const token1 = await fetchCsrfToken()
      const token2 = await fetchCsrfToken()

      expect(token1).toBe('cached-token')
      expect(token2).toBe('cached-token')
      // API should only be called once due to caching
      expect(api.default.get).toHaveBeenCalledTimes(1)
    })

    it('lance une erreur si l\'endpoint échoue', async () => {
      const { fetchCsrfToken } = await import('./csrf')
      const api = await import('./api')

      vi.mocked(api.default.get).mockRejectedValue(new Error('Network error'))

      clearCsrfToken()
      await expect(fetchCsrfToken()).rejects.toThrow('Network error')
    })
  })

  describe('csrfService', () => {
    it('exporte les bonnes fonctions', async () => {
      const { csrfService } = await import('./csrf')

      expect(csrfService.fetchToken).toBeDefined()
      expect(csrfService.getToken).toBeDefined()
      expect(csrfService.clear).toBeDefined()
      expect(csrfService.requiresCsrf).toBeDefined()
      expect(csrfService.CSRF_HEADER).toBe('X-CSRF-Token')
    })
  })
})
