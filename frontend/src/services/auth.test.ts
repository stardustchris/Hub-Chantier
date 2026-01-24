/**
 * Tests unitaires pour le service auth
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { authService } from './auth'

// Mock du service api
vi.mock('./api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import api from './api'

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('envoie les credentials en format form-urlencoded', async () => {
      const mockResponse = {
        data: {
          user: {
            id: '1',
            email: 'test@example.com',
            nom: 'Test',
            prenom: 'User',
            role: 'admin',
            is_active: true,
          },
          access_token: 'token-123',
          token_type: 'bearer',
        },
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await authService.login('test@example.com', 'password123')

      expect(api.post).toHaveBeenCalledWith(
        '/api/auth/login',
        expect.any(URLSearchParams),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      )

      // Verifie les parametres URLSearchParams
      const callArgs = vi.mocked(api.post).mock.calls[0]
      const params = callArgs[1] as URLSearchParams
      expect(params.get('username')).toBe('test@example.com')
      expect(params.get('password')).toBe('password123')
    })

    it('retourne la reponse avec user et token', async () => {
      const mockResponse = {
        data: {
          user: {
            id: '1',
            email: 'test@example.com',
            nom: 'Test',
            prenom: 'User',
            role: 'admin',
            is_active: true,
          },
          access_token: 'token-123',
          token_type: 'bearer',
        },
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await authService.login('test@example.com', 'password123')

      expect(result.user.email).toBe('test@example.com')
      expect(result.access_token).toBe('token-123')
      expect(result.token_type).toBe('bearer')
    })

    it('propage les erreurs du serveur', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Invalid credentials'))

      await expect(
        authService.login('test@example.com', 'wrong-password')
      ).rejects.toThrow('Invalid credentials')
    })

    it('gere les emails avec caracteres speciaux', async () => {
      const mockResponse = {
        data: {
          user: { id: '1', email: 'test+special@example.com', nom: 'Test', prenom: 'User', role: 'admin', is_active: true },
          access_token: 'token-123',
          token_type: 'bearer',
        },
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await authService.login('test+special@example.com', 'password')

      const callArgs = vi.mocked(api.post).mock.calls[0]
      const params = callArgs[1] as URLSearchParams
      expect(params.get('username')).toBe('test+special@example.com')
    })
  })

  describe('register', () => {
    it('envoie les donnees d\'inscription en JSON', async () => {
      const mockResponse = {
        data: {
          user: {
            id: '1',
            email: 'new@example.com',
            nom: 'New',
            prenom: 'User',
            role: 'compagnon',
            is_active: true,
          },
          access_token: 'token-456',
          token_type: 'bearer',
        },
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await authService.register({
        email: 'new@example.com',
        password: 'password123',
        nom: 'New',
        prenom: 'User',
      })

      expect(api.post).toHaveBeenCalledWith('/api/auth/register', {
        email: 'new@example.com',
        password: 'password123',
        nom: 'New',
        prenom: 'User',
      })

      expect(result.user.email).toBe('new@example.com')
      expect(result.access_token).toBe('token-456')
    })

    it('propage les erreurs d\'inscription', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Email already exists'))

      await expect(
        authService.register({
          email: 'existing@example.com',
          password: 'password123',
          nom: 'Test',
          prenom: 'User',
        })
      ).rejects.toThrow('Email already exists')
    })
  })

  describe('getCurrentUser', () => {
    it('appelle l\'endpoint /api/auth/me', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        nom: 'Test',
        prenom: 'User',
        role: 'admin',
        is_active: true,
      }
      vi.mocked(api.get).mockResolvedValue({ data: mockUser })

      const result = await authService.getCurrentUser()

      expect(api.get).toHaveBeenCalledWith('/api/auth/me')
      expect(result).toEqual(mockUser)
    })

    it('propage les erreurs 401', async () => {
      vi.mocked(api.get).mockRejectedValue({ response: { status: 401 } })

      await expect(authService.getCurrentUser()).rejects.toEqual({
        response: { status: 401 },
      })
    })

    it('retourne toutes les proprietes de l\'utilisateur', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        nom: 'Test',
        prenom: 'User',
        role: 'conducteur',
        is_active: true,
        metier: 'Electricien',
        telephone: '+33612345678',
      }
      vi.mocked(api.get).mockResolvedValue({ data: mockUser })

      const result = await authService.getCurrentUser()

      expect(result.role).toBe('conducteur')
      expect(result.metier).toBe('Electricien')
      expect(result.telephone).toBe('+33612345678')
    })
  })
})
