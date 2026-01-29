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

vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import { useTodayTeam } from './useTodayTeam'
import { useAuth } from '../contexts/AuthContext'
import { planningService } from '../services/planning'

const mockUseAuth = vi.mocked(useAuth)
const mockGetByUtilisateur = vi.mocked(planningService.getByUtilisateur)
const mockGetAffectations = vi.mocked(planningService.getAffectations)

function makeAffectation(overrides: Record<string, any> = {}) {
  return {
    id: '1',
    chantier_id: '10',
    chantier_nom: 'Chantier Alpha',
    utilisateur_id: '2',
    utilisateur_nom: 'Pierre Martin',
    utilisateur_role: 'ouvrier',
    utilisateur_couleur: '#f97316',
    date_affectation: '2026-01-29',
    heure_debut: '08:00',
    heure_fin: '17:00',
    ...overrides,
  }
}

describe('useTodayTeam', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should return empty members when user is null', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.members).toEqual([])
    expect(result.current.teams).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('should load team members from same chantiers as the user', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Dupont', prenom: 'Jean', email: 'j@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    // User is on chantier 10
    mockGetByUtilisateur.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', utilisateur_nom: 'Jean Dupont' }) as any,
    ])

    // All affectations on the same chantiers
    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', utilisateur_nom: 'Jean Dupont' }) as any,
      makeAffectation({ utilisateur_id: '2', utilisateur_nom: 'Pierre Martin', utilisateur_role: 'ouvrier' }) as any,
      makeAffectation({ utilisateur_id: '3', utilisateur_nom: 'Marie Chef', utilisateur_role: 'chef_chantier' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Should exclude the current user (id: '1')
    expect(result.current.members.length).toBe(2)
    expect(result.current.members.some(m => m.id === '1')).toBe(false)
    expect(result.current.members.some(m => m.firstName === 'Pierre')).toBe(true)
    expect(result.current.members.some(m => m.firstName === 'Marie')).toBe(true)
  })

  it('should load all affectations for admin with no personal affectations', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Admin', prenom: 'Greg', email: 'a@t.com', role: 'admin' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])
    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '2', utilisateur_nom: 'Pierre Martin' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(mockGetAffectations).toHaveBeenCalled()
    expect(result.current.members.length).toBe(1)
  })

  it('should group members by chantier in teams', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '1', chantier_id: '20', chantier_nom: 'Chantier Beta' }) as any,
    ])

    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '2', chantier_id: '10', utilisateur_nom: 'Pierre Martin' }) as any,
      makeAffectation({ utilisateur_id: '1', chantier_id: '20', chantier_nom: 'Chantier Beta' }) as any,
      makeAffectation({ utilisateur_id: '3', chantier_id: '20', chantier_nom: 'Chantier Beta', utilisateur_nom: 'Marie Chef' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.teams.length).toBe(2)
    const team10 = result.current.teams.find(t => t.chantierId === '10')
    const team20 = result.current.teams.find(t => t.chantierId === '20')
    expect(team10?.members.length).toBe(1)
    expect(team20?.members.length).toBe(1)
  })

  it('should deduplicate members across chantiers in the members list', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '1', chantier_id: '20', chantier_nom: 'Chantier Beta' }) as any,
    ])

    // Same person on two chantiers
    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '2', chantier_id: '10', utilisateur_nom: 'Pierre Martin' }) as any,
      makeAffectation({ utilisateur_id: '1', chantier_id: '20', chantier_nom: 'Chantier Beta' }) as any,
      makeAffectation({ utilisateur_id: '2', chantier_id: '20', chantier_nom: 'Chantier Beta', utilisateur_nom: 'Pierre Martin' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Pierre appears on both chantiers but uniqueMembers should deduplicate
    expect(result.current.members.length).toBe(1)
    expect(result.current.members[0].firstName).toBe('Pierre')
  })

  it('should provide getTeamForChantier helper', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
    ])

    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '2', chantier_id: '10', utilisateur_nom: 'Pierre Martin' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const teamFor10 = result.current.getTeamForChantier('10')
    expect(teamFor10.length).toBe(1)
    expect(teamFor10[0].firstName).toBe('Pierre')

    const teamFor99 = result.current.getTeamForChantier('99')
    expect(teamFor99.length).toBe(0)
  })

  it('should sort members by role priority', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
    ])

    mockGetAffectations.mockResolvedValue([
      makeAffectation({ utilisateur_id: '1', chantier_id: '10' }) as any,
      makeAffectation({ utilisateur_id: '2', chantier_id: '10', utilisateur_nom: 'Pierre Ouvrier', utilisateur_role: 'ouvrier' }) as any,
      makeAffectation({ utilisateur_id: '3', chantier_id: '10', utilisateur_nom: 'Marie Chef', utilisateur_role: 'chef_chantier' }) as any,
    ])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Chef de chantier should come before Ouvrier
    expect(result.current.members[0].role).toBe('Chef de chantier')
    expect(result.current.members[1].role).toBe('Ouvrier')
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

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.error).toBe("Impossible de charger l'équipe")
    expect(result.current.members).toEqual([])
  })

  it('should expose refresh function', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useTodayTeam())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    mockGetByUtilisateur.mockClear()
    mockGetByUtilisateur.mockResolvedValue([])

    await act(async () => {
      await result.current.refresh()
    })

    expect(mockGetByUtilisateur).toHaveBeenCalled()
  })
})
