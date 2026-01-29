// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../services/planning', () => ({
  planningService: {
    getByUtilisateur: vi.fn(),
    getAffectations: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    getById: vi.fn(),
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

import { useTodayPlanning } from './useTodayPlanning'
import { useAuth } from '../contexts/AuthContext'
import { planningService } from '../services/planning'
import { chantiersService } from '../services/chantiers'

const mockUseAuth = vi.mocked(useAuth)
const mockGetByUtilisateur = vi.mocked(planningService.getByUtilisateur)
const mockGetAffectations = vi.mocked(planningService.getAffectations)
const mockGetById = vi.mocked(chantiersService.getById)

function makeAffectation(overrides: Record<string, any> = {}) {
  return {
    id: '1',
    chantier_id: '10',
    chantier_nom: 'Chantier Alpha',
    utilisateur_id: '1',
    utilisateur_nom: 'Jean Dupont',
    date_affectation: '2026-01-29',
    heure_debut: '08:00',
    heure_fin: '12:00',
    note: null,
    ...overrides,
  }
}

function makeChantier(overrides: Record<string, any> = {}) {
  return {
    id: '10',
    nom: 'Chantier Alpha',
    adresse: '123 rue test',
    statut: 'en_cours',
    latitude: 45.0,
    longitude: 5.0,
    ...overrides,
  }
}

describe('useTodayPlanning', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return empty slots and stop loading when user is null', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.slots).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should load personal affectations for a regular user', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Dupont', prenom: 'Jean', email: 'j@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const affectation = makeAffectation()
    mockGetByUtilisateur.mockResolvedValue([affectation as any])

    const chantier = makeChantier()
    mockGetById.mockResolvedValue(chantier as any)

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.slots.length).toBeGreaterThan(0)
    const slot = result.current.slots[0]
    expect(slot.siteName).toBe('Chantier Alpha')
    expect(slot.siteAddress).toBe('123 rue test')
    expect(slot.startTime).toBe('08:00')
    expect(slot.endTime).toBe('12:00')
    expect(slot.period).toBe('morning')
    expect(slot.isPersonalAffectation).toBe(true)
  })

  it('should load all affectations for admin with no personal affectations', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Admin', prenom: 'Greg', email: 'a@t.com', role: 'admin' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    // No personal affectations
    mockGetByUtilisateur.mockResolvedValue([])

    // All affectations for the day
    const allAffectation = makeAffectation({ id: '5', chantier_id: '20', chantier_nom: 'Chantier Beta', utilisateur_id: '2' })
    mockGetAffectations.mockResolvedValue([allAffectation as any])

    const chantier = makeChantier({ id: '20', nom: 'Chantier Beta' })
    mockGetById.mockResolvedValue(chantier as any)

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(mockGetAffectations).toHaveBeenCalled()
    expect(result.current.slots.length).toBeGreaterThan(0)
    // Admin with no personal affectation sees team affectations
    expect(result.current.slots[0].isPersonalAffectation).toBe(false)
  })

  it('should add a lunch break between morning and afternoon slots', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const morningAff = makeAffectation({ id: '1', heure_debut: '08:00', heure_fin: '12:00' })
    const afternoonAff = makeAffectation({ id: '2', heure_debut: '13:30', heure_fin: '17:00' })
    mockGetByUtilisateur.mockResolvedValue([morningAff as any, afternoonAff as any])
    mockGetById.mockResolvedValue(makeChantier() as any)

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should have morning + break + afternoon = 3 slots
    expect(result.current.slots.length).toBe(3)
    const breakSlot = result.current.slots.find(s => s.period === 'break')
    expect(breakSlot).toBeDefined()
    expect(breakSlot?.startTime).toBe('12:00')
    expect(breakSlot?.endTime).toBe('13:30')
  })

  it('should handle API errors gracefully', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.error).toBe('Impossible de charger votre planning')
    expect(result.current.slots).toEqual([])
  })

  it('should expose a refresh function', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(typeof result.current.refresh).toBe('function')

    mockGetByUtilisateur.mockClear()
    mockGetByUtilisateur.mockResolvedValue([])

    await act(async () => {
      await result.current.refresh()
    })

    expect(mockGetByUtilisateur).toHaveBeenCalled()
  })

  it('should handle chantier fetch failure gracefully', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const affectation = makeAffectation()
    mockGetByUtilisateur.mockResolvedValue([affectation as any])
    // Chantier fetch fails
    mockGetById.mockRejectedValue(new Error('Not found'))

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should still produce a slot, but without chantier details
    expect(result.current.slots.length).toBe(1)
    expect(result.current.error).toBeNull()
  })

  it('should use default times when affectation has no heure_debut/fin', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const affectation = makeAffectation({ heure_debut: undefined, heure_fin: undefined })
    mockGetByUtilisateur.mockResolvedValue([affectation as any])
    mockGetById.mockResolvedValue(makeChantier() as any)

    const { result } = renderHook(() => useTodayPlanning())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.slots[0].startTime).toBe('08:00')
    expect(result.current.slots[0].endTime).toBe('17:00')
  })
})
