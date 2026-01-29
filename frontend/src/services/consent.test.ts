/**
 * Tests pour le service de gestion du consentement RGPD
 * Note: Ces tests vérifient principalement l'API du service
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { consentService, type ConsentType } from './consent'
import api from './api'

// Mock logger service
vi.mock('./logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

// Mock de l'API
vi.mock('./api')

describe('consentService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Réinitialise le cache avant chaque test
    consentService.resetCache()
  })

  describe('structure API', () => {
    it('expose les méthodes requises', () => {
      expect(typeof consentService.hasConsent).toBe('function')
      expect(typeof consentService.hasAnyConsent).toBe('function')
      expect(typeof consentService.setConsent).toBe('function')
      expect(typeof consentService.setConsents).toBe('function')
      expect(typeof consentService.revokeAllConsents).toBe('function')
      expect(typeof consentService.getAllConsents).toBe('function')
      expect(typeof consentService.wasBannerShown).toBe('function')
      expect(typeof consentService.markBannerAsShown).toBe('function')
      expect(typeof consentService.resetCache).toBe('function')
    })
  })

  describe('hasConsent', () => {
    it('retourne false par défaut', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { geolocation: false, analytics: false, notifications: false }
      })

      expect(await consentService.hasConsent('geolocation')).toBe(false)
      expect(await consentService.hasConsent('analytics')).toBe(false)
      expect(await consentService.hasConsent('notifications')).toBe(false)
    })

    it('accepte les types de consentement valides', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { geolocation: true, analytics: false, notifications: false }
      })

      const types: ConsentType[] = ['geolocation', 'analytics', 'notifications']
      for (const type of types) {
        await expect(consentService.hasConsent(type)).resolves.toBeDefined()
      }
    })
  })

  describe('hasAnyConsent', () => {
    it('retourne false si aucun consentement', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { geolocation: false, analytics: false, notifications: false }
      })

      expect(await consentService.hasAnyConsent()).toBe(false)
    })

    it('retourne true si au moins un consentement', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { geolocation: true, analytics: false, notifications: false }
      })

      expect(await consentService.hasAnyConsent()).toBe(true)
    })
  })

  describe('setConsent', () => {
    it('envoie une requête à l\'API', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: {} })

      await consentService.setConsent('geolocation', true)

      expect(api.post).toHaveBeenCalledWith('/api/auth/consents', {
        geolocation: true,
      })
    })

    it('met à jour le cache', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { geolocation: false, analytics: false, notifications: false }
      })
      vi.mocked(api.post).mockResolvedValue({ data: {} })

      await consentService.hasConsent('geolocation') // Charge le cache
      await consentService.setConsent('geolocation', true)

      // Le cache devrait être mis à jour, pas d'appel API supplémentaire
      vi.mocked(api.get).mockClear()
      expect(await consentService.hasConsent('geolocation')).toBe(true)
      expect(api.get).not.toHaveBeenCalled()
    })
  })

  describe('revokeAllConsents', () => {
    it('révoque tous les consentements', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: {} })

      await consentService.revokeAllConsents()

      expect(api.post).toHaveBeenCalledWith('/api/auth/consents', {
        geolocation: false,
        analytics: false,
        notifications: false,
      })
    })
  })

  describe('getAllConsents', () => {
    it('retourne tous les consentements', async () => {
      const mockConsents = {
        geolocation: true,
        analytics: false,
        notifications: true
      }
      vi.mocked(api.get).mockResolvedValue({ data: mockConsents })

      const consents = await consentService.getAllConsents()

      expect(consents).toEqual(mockConsents)
    })
  })

  describe('banner management', () => {
    it('wasBannerShown retourne false par défaut', () => {
      expect(consentService.wasBannerShown()).toBe(false)
    })

    it('markBannerAsShown change l\'état', () => {
      consentService.markBannerAsShown()
      expect(consentService.wasBannerShown()).toBe(true)
    })

    it('resetCache réinitialise l\'état du banner', () => {
      consentService.markBannerAsShown()
      consentService.resetCache()
      expect(consentService.wasBannerShown()).toBe(false)
    })
  })

  describe('gestion des erreurs', () => {
    it('gère gracieusement les erreurs API', async () => {
      vi.mocked(api.get).mockRejectedValue(new Error('API error'))

      const consents = await consentService.getAllConsents()

      // Devrait retourner des valeurs par défaut (tous false avec champs metadata)
      expect(consents).toEqual({
        geolocation: false,
        notifications: false,
        analytics: false,
        timestamp: null,
        ip_address: null,
        user_agent: null,
      })
    })
  })
})
