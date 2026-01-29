// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

vi.mock('../services/logistiqueMockData', () => ({
  initializeMockData: vi.fn(),
  getTodayReservationsByChantier: vi.fn(),
  getUpcomingReservationsByChantier: vi.fn(),
}))

vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import { useChantierLogistique } from './useChantierLogistique'
import {
  initializeMockData,
  getTodayReservationsByChantier,
  getUpcomingReservationsByChantier,
} from '../services/logistiqueMockData'

const mockInitialize = vi.mocked(initializeMockData)
const mockGetToday = vi.mocked(getTodayReservationsByChantier)
const mockGetUpcoming = vi.mocked(getUpcomingReservationsByChantier)

function makeReservation(overrides: Record<string, any> = {}) {
  return {
    id: 1,
    ressource_id: 10,
    ressource_nom: 'Grue mobile',
    ressource_code: 'GRU-01',
    ressource_couleur: '#E74C3C',
    chantier_id: 1,
    chantier_nom: 'Résidence Les Jardins',
    demandeur_id: 1,
    demandeur_nom: 'Pierre Martin',
    date_reservation: '2026-01-29',
    heure_debut: '08:00',
    heure_fin: '17:00',
    statut: 'validee' as const,
    statut_label: 'Validée',
    statut_couleur: '#4CAF50',
    ...overrides,
  }
}

describe('useChantierLogistique', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockInitialize.mockImplementation(() => {})
    mockGetToday.mockReturnValue([])
    mockGetUpcoming.mockReturnValue([])
  })

  it('should return initial loading state then load data', () => {
    const { result } = renderHook(() => useChantierLogistique(1))

    // After useEffect runs synchronously (mock data is sync)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.todayReservations).toEqual([])
    expect(result.current.upcomingReservations).toEqual([])
  })

  it('should initialize mock data on load', () => {
    renderHook(() => useChantierLogistique(1))

    expect(mockInitialize).toHaveBeenCalled()
  })

  it('should load today and upcoming reservations for the chantier', () => {
    const todayRes = [makeReservation({ id: 1 })]
    const upcomingRes = [makeReservation({ id: 2, date_reservation: '2026-02-01', statut: 'en_attente' })]

    mockGetToday.mockReturnValue(todayRes as any)
    mockGetUpcoming.mockReturnValue(upcomingRes as any)

    const { result } = renderHook(() => useChantierLogistique(1))

    expect(mockGetToday).toHaveBeenCalledWith(1)
    expect(mockGetUpcoming).toHaveBeenCalledWith(1)
    expect(result.current.todayReservations).toEqual(todayRes)
    expect(result.current.upcomingReservations).toEqual(upcomingRes)
  })

  it('should calculate stats correctly', () => {
    mockGetToday.mockReturnValue([
      makeReservation({ id: 1 }),
      makeReservation({ id: 2 }),
    ] as any)

    mockGetUpcoming.mockReturnValue([
      makeReservation({ id: 3, statut: 'en_attente' }),
      makeReservation({ id: 4, statut: 'validee' }),
      makeReservation({ id: 5, statut: 'en_attente' }),
    ] as any)

    const { result } = renderHook(() => useChantierLogistique(1))

    expect(result.current.stats.todayCount).toBe(2)
    expect(result.current.stats.upcomingCount).toBe(3)
    expect(result.current.stats.pendingCount).toBe(2) // 2 en_attente
  })

  it('should accept string chantierId and convert to number', () => {
    renderHook(() => useChantierLogistique('5'))

    expect(mockGetToday).toHaveBeenCalledWith(5)
    expect(mockGetUpcoming).toHaveBeenCalledWith(5)
  })

  it('should not load data for invalid (NaN) chantierId', () => {
    renderHook(() => useChantierLogistique('abc'))

    expect(mockGetToday).not.toHaveBeenCalled()
    expect(mockGetUpcoming).not.toHaveBeenCalled()
  })

  it('should not load data when chantierId is 0', () => {
    renderHook(() => useChantierLogistique(0))

    expect(mockGetToday).not.toHaveBeenCalled()
    expect(mockGetUpcoming).not.toHaveBeenCalled()
  })

  it('should handle errors gracefully', () => {
    mockGetToday.mockImplementation(() => {
      throw new Error('Mock data error')
    })

    const { result } = renderHook(() => useChantierLogistique(1))

    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe('Impossible de charger les données logistique')
    expect(result.current.todayReservations).toEqual([])
  })

  it('should expose refresh function that reloads data', () => {
    const { result } = renderHook(() => useChantierLogistique(1))

    mockGetToday.mockClear()
    mockGetUpcoming.mockClear()
    mockInitialize.mockClear()

    const newRes = [makeReservation({ id: 99 })]
    mockGetToday.mockReturnValue(newRes as any)
    mockGetUpcoming.mockReturnValue([])

    act(() => {
      result.current.refresh()
    })

    expect(mockInitialize).toHaveBeenCalled()
    expect(mockGetToday).toHaveBeenCalledWith(1)
    expect(result.current.todayReservations).toEqual(newRes)
  })

  it('should reload when chantierId changes', () => {
    const { rerender } = renderHook(
      ({ id }: { id: number }) => useChantierLogistique(id),
      { initialProps: { id: 1 } }
    )

    expect(mockGetToday).toHaveBeenCalledWith(1)

    mockGetToday.mockClear()
    mockGetUpcoming.mockClear()

    rerender({ id: 2 })

    expect(mockGetToday).toHaveBeenCalledWith(2)
    expect(mockGetUpcoming).toHaveBeenCalledWith(2)
  })
})
