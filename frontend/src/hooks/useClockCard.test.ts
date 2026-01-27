/**
 * Tests pour le hook useClockCard
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useClockCard } from './useClockCard'

// Mock ToastContext
const mockAddToast = vi.fn()
vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    addToast: mockAddToast,
  }),
}))

// Mock AuthContext
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', nom: 'Test', prenom: 'User', role: 'compagnon' },
  }),
}))

// Mock pointagesService
vi.mock('../services/pointages', () => ({
  pointagesService: {
    create: vi.fn().mockResolvedValue({ id: 100 }),
    update: vi.fn().mockResolvedValue({}),
  },
}))

// Mock logger
vi.mock('../services/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}))

describe('useClockCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2024-01-15T09:00:00'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('état initial', () => {
    it('retourne clockState null initialement', () => {
      const { result } = renderHook(() => useClockCard())

      expect(result.current.clockState).toBeNull()
      expect(result.current.isClockedIn).toBe(false)
    })

    it('initialise showEditModal à false', () => {
      const { result } = renderHook(() => useClockCard())

      expect(result.current.showEditModal).toBe(false)
    })
  })

  describe('handleClockIn', () => {
    it('enregistre l\'heure d\'arrivée dans le state', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      expect(result.current.clockState?.clockInTime).toBe('09:00')
      expect(result.current.isClockedIn).toBe(true)
    })

    it('affiche un toast de succès', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      expect(mockAddToast).toHaveBeenCalledWith({
        message: expect.stringContaining('09:00'),
        type: 'success',
      })
    })
  })

  describe('handleClockOut', () => {
    it('enregistre l\'heure de départ', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      vi.setSystemTime(new Date('2024-01-15T17:30:00'))

      act(() => {
        result.current.handleClockOut()
      })

      expect(result.current.clockState?.clockOutTime).toBe('17:30')
      expect(result.current.isClockedIn).toBe(false)
    })

    it('ne fait rien si pas de clockIn', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockOut()
      })

      expect(result.current.clockState).toBeNull()
    })

    it('affiche un toast de succès après clock out', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      mockAddToast.mockClear()

      act(() => {
        result.current.handleClockOut()
      })

      expect(mockAddToast).toHaveBeenCalledWith({
        message: expect.stringContaining('09:00'),
        type: 'success',
      })
    })
  })

  describe('isClockedIn', () => {
    it('retourne true si clockInTime mais pas clockOutTime', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      expect(result.current.isClockedIn).toBe(true)
    })

    it('retourne false si clockInTime ET clockOutTime', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleClockIn()
      })

      act(() => {
        result.current.handleClockOut()
      })

      expect(result.current.isClockedIn).toBe(false)
    })
  })

  describe('modal d\'édition', () => {
    it('ouvre la modal avec handleEditTime', () => {
      const { result } = renderHook(() => useClockCard())

      expect(result.current.showEditModal).toBe(false)

      act(() => {
        result.current.handleEditTime('arrival', '08:00')
      })

      expect(result.current.showEditModal).toBe(true)
      expect(result.current.editTimeType).toBe('arrival')
      expect(result.current.editTimeValue).toBe('08:00')
    })

    it('ferme la modal avec closeEditModal', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleEditTime('arrival')
      })

      expect(result.current.showEditModal).toBe(true)

      act(() => {
        result.current.closeEditModal()
      })

      expect(result.current.showEditModal).toBe(false)
    })

    it('met à jour editTimeValue', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleEditTime('arrival')
      })

      act(() => {
        result.current.setEditTimeValue('07:45')
      })

      expect(result.current.editTimeValue).toBe('07:45')
    })

    it('sauvegarde l\'heure modifiée et ferme la modal', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleEditTime('arrival')
        result.current.setEditTimeValue('07:45')
      })

      act(() => {
        result.current.handleSaveEditedTime()
      })

      expect(result.current.clockState?.clockInTime).toBe('07:45')
      expect(result.current.showEditModal).toBe(false)
    })

    it('ne sauvegarde pas si valeur vide', () => {
      const { result } = renderHook(() => useClockCard())

      act(() => {
        result.current.handleEditTime('arrival')
        result.current.setEditTimeValue('')
      })

      act(() => {
        result.current.handleSaveEditedTime()
      })

      // La modal reste ouverte car pas de sauvegarde
      expect(result.current.showEditModal).toBe(true)
    })
  })
})
