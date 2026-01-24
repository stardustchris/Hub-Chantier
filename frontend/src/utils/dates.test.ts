/**
 * Tests unitaires pour les utilitaires de dates
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import {
  formatDateFull,
  formatDateShort,
  formatDateTime,
  formatRelative,
  formatDateSmart,
  formatTime,
  formatMonthYear,
  formatDayName,
  formatDateDayMonth,
  formatDateDayMonthShort,
  formatDateDayMonthYear,
  formatDateTimeShort,
  formatDateDayMonthYearTime,
  formatDuration,
  formatDateWeekdayFull,
  parseTimeToMinutes,
  minutesToTime,
  formatRelativeShort,
} from './dates'

describe('dates utilities', () => {
  // Date fixe pour tests reproductibles: 24 janvier 2026 14:30:00
  const fixedDate = new Date('2026-01-24T14:30:00')
  const fixedDateISO = '2026-01-24T14:30:00'

  describe('formatDateFull', () => {
    it('formate une Date au format complet francais', () => {
      const result = formatDateFull(fixedDate)
      expect(result).toBe('24 janvier 2026')
    })

    it('formate une string ISO au format complet francais', () => {
      const result = formatDateFull(fixedDateISO)
      expect(result).toBe('24 janvier 2026')
    })
  })

  describe('formatDateShort', () => {
    it('formate une Date au format court', () => {
      const result = formatDateShort(fixedDate)
      expect(result).toBe('24/01/2026')
    })

    it('formate une string ISO au format court', () => {
      const result = formatDateShort(fixedDateISO)
      expect(result).toBe('24/01/2026')
    })
  })

  describe('formatDateTime', () => {
    it('formate une Date avec heure', () => {
      const result = formatDateTime(fixedDate)
      expect(result).toBe('24 janvier 2026 a 14:30')
    })
  })

  describe('formatTime', () => {
    it('formate uniquement l\'heure', () => {
      const result = formatTime(fixedDate)
      expect(result).toBe('14:30')
    })

    it('formate les heures avec zero padding', () => {
      const earlyMorning = new Date('2026-01-24T08:05:00')
      expect(formatTime(earlyMorning)).toBe('08:05')
    })
  })

  describe('formatMonthYear', () => {
    it('formate mois et annee', () => {
      const result = formatMonthYear(fixedDate)
      expect(result).toBe('janvier 2026')
    })
  })

  describe('formatDayName', () => {
    it('retourne le nom du jour en francais', () => {
      // 24 janvier 2026 est un samedi
      const result = formatDayName(fixedDate)
      expect(result).toBe('samedi')
    })
  })

  describe('formatDateDayMonth', () => {
    it('formate jour et mois abrege', () => {
      const result = formatDateDayMonth(fixedDate)
      expect(result).toMatch(/24\s*janv\.?/)
    })
  })

  describe('formatDateDayMonthShort', () => {
    it('formate jour/mois numerique', () => {
      const result = formatDateDayMonthShort(fixedDate)
      expect(result).toBe('24/01')
    })
  })

  describe('formatDateDayMonthYear', () => {
    it('formate jour mois abrege annee', () => {
      const result = formatDateDayMonthYear(fixedDate)
      expect(result).toMatch(/24\s*janv\.?\s*2026/)
    })
  })

  describe('formatDateTimeShort', () => {
    it('formate date complete avec heure', () => {
      const result = formatDateTimeShort(fixedDate)
      expect(result).toBe('24/01/2026 14:30')
    })
  })

  describe('formatDateDayMonthYearTime', () => {
    it('formate jour mois abrege annee avec heure', () => {
      const result = formatDateDayMonthYearTime(fixedDate)
      expect(result).toMatch(/24\s*janv\.?\s*2026\s*14:30/)
    })
  })

  describe('formatDateWeekdayFull', () => {
    it('formate jour semaine complet avec date', () => {
      const result = formatDateWeekdayFull(fixedDate)
      expect(result).toBe('samedi 24 janvier 2026')
    })
  })

  describe('formatDuration', () => {
    it('formate heures et minutes avec padding', () => {
      expect(formatDuration(7, 30)).toBe('07:30')
      expect(formatDuration(14, 5)).toBe('14:05')
      expect(formatDuration(0, 0)).toBe('00:00')
    })

    it('gere les minutes par defaut a 0', () => {
      expect(formatDuration(8)).toBe('08:00')
    })
  })

  describe('parseTimeToMinutes', () => {
    it('convertit HH:mm en minutes totales', () => {
      expect(parseTimeToMinutes('07:30')).toBe(450)
      expect(parseTimeToMinutes('14:00')).toBe(840)
      expect(parseTimeToMinutes('00:00')).toBe(0)
      expect(parseTimeToMinutes('23:59')).toBe(1439)
    })
  })

  describe('minutesToTime', () => {
    it('convertit minutes totales en HH:mm', () => {
      expect(minutesToTime(450)).toBe('07:30')
      expect(minutesToTime(840)).toBe('14:00')
      expect(minutesToTime(0)).toBe('00:00')
      expect(minutesToTime(1439)).toBe('23:59')
    })
  })

  describe('formatRelative', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2026-01-24T16:00:00'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('formate une date relative en francais', () => {
      const twoHoursAgo = new Date('2026-01-24T14:00:00')
      const result = formatRelative(twoHoursAgo)
      expect(result).toContain('heure')
    })
  })

  describe('formatDateSmart', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2026-01-24T16:00:00'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('affiche "Aujourd\'hui" pour une date du jour', () => {
      const today = new Date('2026-01-24T14:30:00')
      const result = formatDateSmart(today)
      expect(result).toBe("Aujourd'hui a 14:30")
    })

    it('affiche "Hier" pour une date de la veille', () => {
      const yesterday = new Date('2026-01-23T14:30:00')
      const result = formatDateSmart(yesterday)
      expect(result).toBe('Hier a 14:30')
    })

    it('affiche le jour de la semaine pour les 7 derniers jours', () => {
      // 22 janvier 2026 = jeudi (2 jours avant le 24)
      const twoDaysAgo = new Date('2026-01-22T14:30:00')
      const result = formatDateSmart(twoDaysAgo)
      expect(result).toMatch(/jeudi a 14:30/i)
    })

    it('affiche la date complete pour les dates plus anciennes', () => {
      const oldDate = new Date('2026-01-10T14:30:00')
      const result = formatDateSmart(oldDate)
      expect(result).toBe('10 janvier 2026')
    })
  })

  describe('formatRelativeShort', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2026-01-24T16:00:00'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('affiche "A l\'instant" pour une date tres recente', () => {
      const justNow = new Date('2026-01-24T15:59:30')
      const result = formatRelativeShort(justNow)
      expect(result).toBe("A l'instant")
    })

    it('affiche "Il y a X min" pour moins d\'une heure', () => {
      const thirtyMinsAgo = new Date('2026-01-24T15:30:00')
      const result = formatRelativeShort(thirtyMinsAgo)
      expect(result).toBe('Il y a 30 min')
    })

    it('affiche "Il y a Xh" pour moins de 24 heures', () => {
      const fiveHoursAgo = new Date('2026-01-24T11:00:00')
      const result = formatRelativeShort(fiveHoursAgo)
      expect(result).toBe('Il y a 5h')
    })

    it('affiche "Il y a Xj" pour moins de 7 jours', () => {
      const threeDaysAgo = new Date('2026-01-21T16:00:00')
      const result = formatRelativeShort(threeDaysAgo)
      expect(result).toBe('Il y a 3j')
    })

    it('affiche la date courte pour plus de 7 jours', () => {
      const twoWeeksAgo = new Date('2026-01-10T16:00:00')
      const result = formatRelativeShort(twoWeeksAgo)
      expect(result).toBe('10/01/2026')
    })
  })
})
