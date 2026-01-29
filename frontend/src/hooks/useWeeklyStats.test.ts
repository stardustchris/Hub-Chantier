// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'

// Mock all dependencies before importing the hook
vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../services/pointages', () => ({
  pointagesService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/taches', () => ({
  tachesService: {
    listByChantier: vi.fn(),
  },
}))

vi.mock('../services/planning', () => ({
  planningService: {
    getByUtilisateur: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import { useWeeklyStats } from './useWeeklyStats'
import { useAuth } from '../contexts/AuthContext'
import { pointagesService } from '../services/pointages'
import { tachesService } from '../services/taches'
import { planningService } from '../services/planning'

const mockUseAuth = vi.mocked(useAuth)
const mockPointagesList = vi.mocked(pointagesService.list)
const mockGetByUtilisateur = vi.mocked(planningService.getByUtilisateur)
const mockListByChantier = vi.mocked(tachesService.listByChantier)

describe('useWeeklyStats', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return initial loading state with defaults', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const { result } = renderHook(() => useWeeklyStats())

    expect(result.current.hoursWorked).toBe('0h00')
    expect(result.current.hoursProgress).toBe(0)
    expect(result.current.congesTotal).toBe(25)
    expect(result.current.tasksCompleted).toBe(0)
    expect(result.current.tasksTotal).toBe(0)
  })

  it('should not load stats when user is null', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    renderHook(() => useWeeklyStats())

    // Wait a tick to ensure no calls were made
    await new Promise(r => setTimeout(r, 50))
    expect(mockPointagesList).not.toHaveBeenCalled()
  })

  it('should load hours worked for the week', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 'test@test.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    // Week pointages: 7h (420min) = 7h00
    mockPointagesList
      .mockResolvedValueOnce({
        items: [
          { total_heures_decimal: 7.0, date_pointage: '2026-01-26' } as any,
        ],
        total: 1,
        page: 1,
        size: 50,
        pages: 1,
      })
      // Month pointages
      .mockResolvedValueOnce({
        items: [
          { date_pointage: '2026-01-26', chantier_nom: 'Chantier A' } as any,
          { date_pointage: '2026-01-27', chantier_nom: 'Chantier B' } as any,
        ],
        total: 2,
        page: 1,
        size: 100,
        pages: 1,
      })
      // Year pointages (for conges)
      .mockResolvedValueOnce({
        items: [],
        total: 0,
        page: 1,
        size: 100,
        pages: 0,
      })

    // Planning affectations (for tasks)
    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useWeeklyStats())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.hoursWorked).toBe('7h00')
    // 420 min / (35*60=2100 min) * 100 = 20%
    expect(result.current.hoursProgress).toBe(20)
    expect(result.current.joursTravailesMois).toBe(2)
    expect(result.current.congesPris).toBe(0)
  })

  it('should calculate conges from year pointages on conge chantiers', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '2', nom: 'Test', prenom: 'User', email: 'test@test.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    // Week pointages
    mockPointagesList
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 50, pages: 0 })
      // Month pointages
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 100, pages: 0 })
      // Year pointages - 2 days of conges (7h each = 840 min)
      .mockResolvedValueOnce({
        items: [
          { total_heures_decimal: 7.0, date_pointage: '2026-01-10', chantier_nom: 'Congés payés' } as any,
          { total_heures_decimal: 7.0, date_pointage: '2026-01-11', chantier_nom: 'Congés payés' } as any,
        ],
        total: 2,
        page: 1,
        size: 100,
        pages: 1,
      })

    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useWeeklyStats())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // 840 min / 420 min per day = 2 days
    expect(result.current.congesPris).toBe(2)
    expect(result.current.congesTotal).toBe(25)
  })

  it('should calculate tasks completed from chantier taches', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '3', nom: 'Test', prenom: 'User', email: 'test@test.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockPointagesList
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 50, pages: 0 })
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 100, pages: 0 })
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 100, pages: 0 })

    // User has affectations on chantier 10
    mockGetByUtilisateur.mockResolvedValue([
      { chantier_id: '10', utilisateur_id: '3' } as any,
    ])

    // Chantier 10 has 3 tasks, 1 completed
    mockListByChantier.mockResolvedValue({
      items: [
        { id: 1, statut: 'termine' } as any,
        { id: 2, statut: 'en_cours' } as any,
        { id: 3, statut: 'a_faire' } as any,
      ],
      total: 3,
      page: 1,
      size: 100,
      pages: 1,
    })

    const { result } = renderHook(() => useWeeklyStats())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.tasksCompleted).toBe(1)
    expect(result.current.tasksTotal).toBe(3)
  })

  it('should handle API errors gracefully', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '4', nom: 'Test', prenom: 'User', email: 'test@test.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockPointagesList.mockRejectedValue(new Error('API Error'))

    const { result } = renderHook(() => useWeeklyStats())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should still have default values, not crash
    expect(result.current.hoursWorked).toBe('0h00')
  })

  it('should exclude conge chantiers from joursTravailesMois count', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '5', nom: 'Test', prenom: 'User', email: 'test@test.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockPointagesList
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 50, pages: 0 })
      // Month pointages with a mix of work and conge
      .mockResolvedValueOnce({
        items: [
          { date_pointage: '2026-01-05', chantier_nom: 'Chantier A' } as any,
          { date_pointage: '2026-01-06', chantier_nom: 'RTT' } as any,
          { date_pointage: '2026-01-07', chantier_nom: 'Chantier B' } as any,
        ],
        total: 3,
        page: 1,
        size: 100,
        pages: 1,
      })
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 100, pages: 0 })

    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useWeeklyStats())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Only 2 work days, RTT excluded
    expect(result.current.joursTravailesMois).toBe(2)
  })
})
