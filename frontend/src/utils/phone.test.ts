/**
 * Tests pour les utilitaires phone.ts
 */

import { describe, it, expect } from 'vitest'
import {
  isValidPhone,
  normalizePhone,
  formatPhone,
  detectCountry,
  getPhoneValidationError,
  COUNTRY_CODES,
} from './phone'

describe('phone utilities', () => {
  describe('COUNTRY_CODES', () => {
    it('contient les pays attendus', () => {
      expect(COUNTRY_CODES.length).toBeGreaterThanOrEqual(10)
      expect(COUNTRY_CODES.find((c) => c.country === 'France')).toBeDefined()
      expect(COUNTRY_CODES.find((c) => c.country === 'Belgique')).toBeDefined()
      expect(COUNTRY_CODES.find((c) => c.country === 'Suisse')).toBeDefined()
    })

    it('France a le code +33', () => {
      const france = COUNTRY_CODES.find((c) => c.country === 'France')
      expect(france?.code).toBe('+33')
      expect(france?.flag).toBe('🇫🇷')
    })
  })

  describe('isValidPhone', () => {
    it('retourne true pour une chaîne vide (optionnel)', () => {
      expect(isValidPhone('')).toBe(true)
      expect(isValidPhone('   ')).toBe(true)
    })

    it('valide les numéros français compacts', () => {
      expect(isValidPhone('0612345678')).toBe(true)
      expect(isValidPhone('+33612345678')).toBe(true)
    })

    it('valide les numéros internationaux compacts', () => {
      expect(isValidPhone('+32123456789')).toBe(true)
      expect(isValidPhone('+15551234567')).toBe(true)
      expect(isValidPhone('+442012345678')).toBe(true)
    })

    it('valide les numéros avec quelques espaces', () => {
      // La regex accepte des espaces à certains endroits
      expect(isValidPhone('06 12345678')).toBe(true)
      expect(isValidPhone('+33 612345678')).toBe(true)
    })

    it('rejette les numéros trop courts', () => {
      expect(isValidPhone('12345')).toBe(false)
      expect(isValidPhone('123456')).toBe(false)
    })

    it('rejette les numéros trop longs', () => {
      expect(isValidPhone('1234567890123456')).toBe(false)
    })
  })

  describe('normalizePhone', () => {
    it('retire les espaces', () => {
      expect(normalizePhone('06 12 34 56 78')).toBe('0612345678')
    })

    it('retire les tirets', () => {
      expect(normalizePhone('06-12-34-56-78')).toBe('0612345678')
    })

    it('retire les points', () => {
      expect(normalizePhone('06.12.34.56.78')).toBe('0612345678')
    })

    it('retire les parenthèses', () => {
      expect(normalizePhone('(555) 123-4567')).toBe('5551234567')
    })

    it('gère les combinaisons mixtes', () => {
      expect(normalizePhone('+33 (6) 12-34.56 78')).toBe('+33612345678')
    })
  })

  describe('formatPhone', () => {
    it('formate un numéro français avec indicatif +33', () => {
      expect(formatPhone('+33612345678')).toBe('+33 6 12 34 56 78')
    })

    it('formate un numéro français avec indicatif 33 sans +', () => {
      expect(formatPhone('33612345678')).toBe('+33 6 12 34 56 78')
    })

    it('formate un numéro français sans indicatif', () => {
      expect(formatPhone('0612345678')).toBe('06 12 34 56 78')
    })

    it('retourne tel quel les autres formats', () => {
      const belgique = '+32456789012'
      expect(formatPhone(belgique)).toBe(belgique)
    })

    it('gère les numéros déjà formatés', () => {
      const formatted = '+33 6 12 34 56 78'
      expect(formatPhone(formatted)).toBe('+33 6 12 34 56 78')
    })
  })

  describe('detectCountry', () => {
    it('détecte la France avec +33', () => {
      const result = detectCountry('+33612345678')
      expect(result?.country).toBe('France')
      expect(result?.code).toBe('+33')
    })

    it('détecte la France avec 33 sans +', () => {
      const result = detectCountry('33612345678')
      expect(result?.country).toBe('France')
    })

    it('détecte la Belgique avec +32', () => {
      const result = detectCountry('+32123456789')
      expect(result?.country).toBe('Belgique')
    })

    it('détecte la Suisse avec +41', () => {
      const result = detectCountry('+41123456789')
      expect(result?.country).toBe('Suisse')
    })

    it('détecte le Luxembourg avec +352', () => {
      const result = detectCountry('+352123456')
      expect(result?.country).toBe('Luxembourg')
    })

    it('détecte Monaco avec +377', () => {
      const result = detectCountry('+377123456')
      expect(result?.country).toBe('Monaco')
    })

    it('détecte USA/Canada avec +1', () => {
      const result = detectCountry('+15551234567')
      expect(result?.country).toBe('USA/Canada')
    })

    it('retourne France par défaut pour 0x', () => {
      const result = detectCountry('0612345678')
      expect(result?.country).toBe('France')
    })

    it('retourne null pour un format inconnu sans indicatif reconnu', () => {
      // Note: +1 match les numéros commençant par 1, donc testons avec autre chose
      const result = detectCountry('9876543210')
      expect(result).toBeNull()
    })

    it('gère les espaces et tirets dans les numéros', () => {
      const result = detectCountry('+33-612-345-678')
      expect(result?.country).toBe('France')
    })
  })

  describe('getPhoneValidationError', () => {
    it('retourne null pour une chaîne vide', () => {
      expect(getPhoneValidationError('')).toBeNull()
      expect(getPhoneValidationError('   ')).toBeNull()
    })

    it('retourne null pour un numéro valide', () => {
      expect(getPhoneValidationError('0612345678')).toBeNull()
      expect(getPhoneValidationError('+33612345678')).toBeNull()
    })

    it('retourne une erreur pour numéro trop court', () => {
      const error = getPhoneValidationError('12345')
      expect(error).toContain('trop court')
      expect(error).toContain('8 chiffres')
    })

    it('retourne une erreur pour numéro trop long', () => {
      const error = getPhoneValidationError('1234567890123456')
      expect(error).toContain('trop long')
      expect(error).toContain('15 chiffres')
    })

    it('retourne une erreur pour format invalide', () => {
      const error = getPhoneValidationError('abcdefghij')
      expect(error).toContain('invalide')
    })
  })
})
