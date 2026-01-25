/**
 * Tests pour le service de gestion du consentement RGPD
 * Note: Ces tests vérifient principalement l'API du service
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { consentService, type ConsentType } from './consent'

describe('consentService', () => {
  beforeEach(() => {
    // Révoque tout avant chaque test pour un état propre
    consentService.revokeAllConsents()
  })

  describe('structure API', () => {
    it('expose les méthodes requises', () => {
      expect(typeof consentService.hasConsent).toBe('function')
      expect(typeof consentService.wasAsked).toBe('function')
      expect(typeof consentService.setConsent).toBe('function')
      expect(typeof consentService.revokeAllConsents).toBe('function')
      expect(typeof consentService.getAllConsents).toBe('function')
      expect(typeof consentService.getConsentTimestamp).toBe('function')
    })
  })

  describe('hasConsent', () => {
    it('retourne false par défaut', () => {
      expect(consentService.hasConsent('geolocation')).toBe(false)
      expect(consentService.hasConsent('analytics')).toBe(false)
      expect(consentService.hasConsent('notifications')).toBe(false)
    })

    it('accepte les types de consentement valides', () => {
      const types: ConsentType[] = ['geolocation', 'analytics', 'notifications']
      types.forEach(type => {
        expect(() => consentService.hasConsent(type)).not.toThrow()
      })
    })
  })

  describe('wasAsked', () => {
    it('retourne false par défaut', () => {
      expect(consentService.wasAsked('geolocation')).toBe(false)
    })
  })

  describe('setConsent', () => {
    it('ne lève pas d\'erreur', () => {
      expect(() => consentService.setConsent('geolocation', true)).not.toThrow()
      expect(() => consentService.setConsent('analytics', false)).not.toThrow()
    })
  })

  describe('revokeAllConsents', () => {
    it('ne lève pas d\'erreur', () => {
      expect(() => consentService.revokeAllConsents()).not.toThrow()
    })

    it('réinitialise l\'état', () => {
      consentService.revokeAllConsents()
      expect(consentService.hasConsent('geolocation')).toBe(false)
      expect(consentService.wasAsked('geolocation')).toBe(false)
    })
  })

  describe('getAllConsents', () => {
    it('retourne un tableau', () => {
      const consents = consentService.getAllConsents()
      expect(Array.isArray(consents)).toBe(true)
    })

    it('retourne un tableau vide après révocation', () => {
      consentService.revokeAllConsents()
      const consents = consentService.getAllConsents()
      expect(consents).toHaveLength(0)
    })
  })

  describe('getConsentTimestamp', () => {
    it('retourne null par défaut', () => {
      expect(consentService.getConsentTimestamp('geolocation')).toBeNull()
    })
  })
})
