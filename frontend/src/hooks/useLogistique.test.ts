/**
 * Tests unitaires pour useLogistique hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useLogistique } from './useLogistique'
import { chantiersService } from '../services/chantiers'
import { listReservationsEnAttente, listRessources } from '../services/logistique'
import { createMockChantier, createMockReservation, createMockRessource } from '../fixtures'

// Mocks
vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(() => ({
    user: { id: '1', role: 'admin', email: 'admin@test.com' },
  })),
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/logistique', () => ({
  listReservationsEnAttente: vi.fn(),
  listRessources: vi.fn(),
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

const mockChantiers = [
  createMockChantier({ id: '1', nom: 'Chantier 1', code: 'CH1' }),
  createMockChantier({ id: '2', nom: 'Chantier 2', code: 'CH2' }),
]

const mockReservationsEnAttente = [
  createMockReservation({ id: 1, ressource_id: 1, statut: 'en_attente', date_reservation: '2026-01-25' }),
  createMockReservation({ id: 2, ressource_id: 2, statut: 'en_attente', date_reservation: '2026-01-26' }),
]

const mockRessources = [
  createMockRessource({ id: 1, nom: 'Grue 1', categorie: 'engin_levage' }),
  createMockRessource({ id: 2, nom: 'Camion 1', categorie: 'vehicule' }),
]

describe('useLogistique', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(chantiersService.list).mockResolvedValue({ items: mockChantiers, total: mockChantiers.length, page: 1, size: 20, pages: 1 })
    vi.mocked(listReservationsEnAttente).mockResolvedValue({ items: mockReservationsEnAttente, total: mockReservationsEnAttente.length, limit: 20, offset: 0, has_more: false })
    vi.mocked(listRessources).mockResolvedValue({ items: mockRessources, total: mockRessources.length, limit: 20, offset: 0, has_more: false })
  })

  describe('permissions', () => {
    it('admin a toutes les permissions', () => {
      const { result } = renderHook(() => useLogistique())

      expect(result.current.isAdmin).toBe(true)
      expect(result.current.canValidate).toBe(true)
    })

    it('affiche le tab en-attente si canValidate', async () => {
      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.chantiers).toHaveLength(2)
      })

      const tabIds = result.current.tabs.map((t) => t.id)
      expect(tabIds).toContain('en-attente')
    })
  })

  describe('initial state', () => {
    it('demarre avec onglet ressources', () => {
      const { result } = renderHook(() => useLogistique())
      expect(result.current.activeTab).toBe('ressources')
    })

    it('charge les chantiers au demarrage', async () => {
      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.chantiers).toHaveLength(2)
      })

      expect(chantiersService.list).toHaveBeenCalled()
    })

    it('charge les reservations en attente si canValidate', async () => {
      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.reservationsEnAttente).toHaveLength(2)
      })

      expect(listReservationsEnAttente).toHaveBeenCalled()
    })
  })

  describe('tab management', () => {
    it('change onglet avec setActiveTab', () => {
      const { result } = renderHook(() => useLogistique())

      act(() => {
        result.current.setActiveTab('planning')
      })

      expect(result.current.activeTab).toBe('planning')
    })
  })

  describe('resource selection', () => {
    it('selectionne une ressource et passe au planning', () => {
      const { result } = renderHook(() => useLogistique())

      act(() => {
        result.current.handleSelectRessource(mockRessources[0] as never)
      })

      expect(result.current.selectedRessource).toEqual(mockRessources[0])
      expect(result.current.activeTab).toBe('planning')
    })
  })

  describe('reservation creation', () => {
    it('ouvre le modal avec les donnees initiales', () => {
      const { result } = renderHook(() => useLogistique())

      act(() => {
        result.current.handleCreateReservation('2026-01-25', '08:00', '17:00')
      })

      expect(result.current.showModal).toBe(true)
      expect(result.current.modalInitialData).toEqual({
        date: '2026-01-25',
        heureDebut: '08:00',
        heureFin: '17:00',
      })
      expect(result.current.selectedReservation).toBeNull()
    })
  })

  describe('reservation selection', () => {
    it('selectionne une reservation existante', () => {
      const { result } = renderHook(() => useLogistique())

      act(() => {
        result.current.handleSelectReservation(mockReservationsEnAttente[0] as never)
      })

      expect(result.current.selectedReservation).toEqual(mockReservationsEnAttente[0])
      expect(result.current.showModal).toBe(true)
    })

    it('selectionne une reservation en attente', async () => {
      const { result } = renderHook(() => useLogistique())

      await act(async () => {
        await result.current.handleSelectPendingReservation(mockReservationsEnAttente[0] as never)
      })

      expect(listRessources).toHaveBeenCalled()
      expect(result.current.selectedRessource).toEqual(mockRessources[0])
      expect(result.current.selectedReservation).toEqual(mockReservationsEnAttente[0])
      expect(result.current.showModal).toBe(true)
    })
  })

  describe('modal management', () => {
    it('ferme le modal et reset les donnees', () => {
      const { result } = renderHook(() => useLogistique())

      act(() => {
        result.current.handleCreateReservation('2026-01-25', '08:00', '17:00')
      })

      act(() => {
        result.current.handleModalClose()
      })

      expect(result.current.showModal).toBe(false)
      expect(result.current.selectedReservation).toBeNull()
      expect(result.current.modalInitialData).toEqual({})
    })

    it('handleModalSuccess recharge les reservations en attente', async () => {
      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.reservationsEnAttente).toHaveLength(2)
      })

      vi.clearAllMocks()

      act(() => {
        result.current.handleModalSuccess()
      })

      expect(listReservationsEnAttente).toHaveBeenCalled()
    })
  })

  describe('tabs configuration', () => {
    it('inclut badge sur tab en-attente', async () => {
      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.reservationsEnAttente).toHaveLength(2)
      })

      const enAttenteTab = result.current.tabs.find((t) => t.id === 'en-attente')
      expect(enAttenteTab?.badge).toBe(2)
    })
  })

  describe('error handling', () => {
    it('gere les erreurs de chargement chantiers', async () => {
      vi.mocked(chantiersService.list).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.chantiers).toEqual([])
      })
    })

    it('gere les erreurs de chargement reservations', async () => {
      vi.mocked(listReservationsEnAttente).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useLogistique())

      await waitFor(() => {
        expect(result.current.reservationsEnAttente).toEqual([])
      })
    })
  })
})
