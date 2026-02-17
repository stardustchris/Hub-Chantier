/**
 * Tests unitaires pour useChantierDetail hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useChantierDetail } from './useChantierDetail'
import { chantiersService } from '../services/chantiers'
import { usersService } from '../services/users'
import { createMockUser } from '../fixtures'
import type { ReactNode } from 'react'

// Mocks
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const mockAddToast = vi.fn()
const mockShowUndoToast = vi.fn()
vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    addToast: mockAddToast,
    showUndoToast: mockShowUndoToast,
  }),
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    getById: vi.fn(),
    getNavigationIds: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    demarrer: vi.fn(),
    receptionner: vi.fn(),
    fermer: vi.fn(),
    addConducteur: vi.fn(),
    addChef: vi.fn(),
    removeConducteur: vi.fn(),
    removeChef: vi.fn(),
  },
}))

vi.mock('../services/users', () => ({
  usersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

const mockChantier = {
  id: '1',
  nom: 'Chantier Test',
  code: 'CT001',
  statut: 'planifie',
  conducteurs: [{ id: 'u1', nom: 'Dupont', prenom: 'Jean' }],
  chefs: [{ id: 'u2', nom: 'Martin', prenom: 'Pierre' }],
}

const mockNavIds = { prevId: null, nextId: '2' }

const mockUsers = [
  createMockUser({ id: 'u3', nom: 'Bernard', prenom: 'Paul', role: 'conducteur' }),
  createMockUser({ id: 'u4', nom: 'Petit', prenom: 'Marie', role: 'conducteur' }),
]

const wrapper = ({ children }: { children: ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  })
  return (
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </MemoryRouter>
  )
}

describe('useChantierDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(chantiersService.getById).mockResolvedValue(mockChantier as never)
    vi.mocked(chantiersService.getNavigationIds).mockResolvedValue(mockNavIds)
    vi.mocked(usersService.list).mockResolvedValue({ items: mockUsers, total: mockUsers.length, page: 1, size: 20, pages: 1 })
  })

  describe('initial loading', () => {
    it('demarre en mode loading', () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )
      expect(result.current.isLoading).toBe(true)
    })

    it('charge le chantier au demarrage', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.chantier).toEqual(mockChantier)
      expect(chantiersService.getById).toHaveBeenCalledWith('1')
    })

    it('charge la navigation au demarrage', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.navIds).toEqual(mockNavIds)
      expect(chantiersService.getNavigationIds).toHaveBeenCalledWith('1')
    })
  })

  describe('error handling', () => {
    it('redirige vers /chantiers si erreur de chargement', async () => {
      vi.mocked(chantiersService.getById).mockRejectedValue(new Error('Not found'))

      renderHook(() => useChantierDetail({ chantierId: '999' }), { wrapper })

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/chantiers')
      })

      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Erreur lors du chargement du chantier',
        type: 'error',
      })
    })
  })

  describe('modal states', () => {
    it('gere le modal edition', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.showEditModal).toBe(false)

      act(() => {
        result.current.setShowEditModal(true)
      })

      expect(result.current.showEditModal).toBe(true)
    })

    it('ouvre le modal ajout utilisateur', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.openAddUserModal('conducteur')
      })

      expect(result.current.showAddUserModal).toBe('conducteur')
      expect(usersService.list).toHaveBeenCalledWith(
        expect.objectContaining({ role: 'conducteur' })
      )
    })

    it('ferme le modal ajout utilisateur', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.openAddUserModal('chef')
      })

      act(() => {
        result.current.closeAddUserModal()
      })

      expect(result.current.showAddUserModal).toBeNull()
    })
  })

  describe('update chantier', () => {
    it('met a jour le chantier', async () => {
      const updatedChantier = { ...mockChantier, nom: 'Updated Name' }
      vi.mocked(chantiersService.update).mockResolvedValue(updatedChantier as never)
      // After invalidateQueries, getById is called again — return updated data
      vi.mocked(chantiersService.getById).mockResolvedValue(updatedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.handleUpdateChantier({ nom: 'Updated Name' })
      })

      await waitFor(() => {
        expect(result.current.chantier?.nom).toBe('Updated Name')
      })
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Chantier mis a jour',
        type: 'success',
      })
    })

    it('gere les erreurs de mise a jour', async () => {
      vi.mocked(chantiersService.update).mockRejectedValue(new Error('Update failed'))

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.handleUpdateChantier({ nom: 'Failed' })
      })

      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Erreur lors de la mise a jour',
        type: 'error',
      })
    })
  })

  describe('change status', () => {
    it('demarre le chantier', async () => {
      const startedChantier = { ...mockChantier, statut: 'en_cours' }
      vi.mocked(chantiersService.demarrer).mockResolvedValue(startedChantier as never)
      // After invalidateQueries, getById is called again — return started data
      vi.mocked(chantiersService.getById).mockResolvedValue(startedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.handleChangeStatut('demarrer')
      })

      await waitFor(() => {
        expect(result.current.chantier?.statut).toBe('en_cours')
      })
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Statut mis a jour',
        type: 'success',
      })
    })

    it('receptionne le chantier', async () => {
      const receptionedChantier = { ...mockChantier, statut: 'receptionne' }
      vi.mocked(chantiersService.receptionner).mockResolvedValue(receptionedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.handleChangeStatut('receptionner')
      })

      expect(chantiersService.receptionner).toHaveBeenCalledWith('1')
    })

    it('ferme le chantier', async () => {
      const closedChantier = { ...mockChantier, statut: 'ferme' }
      vi.mocked(chantiersService.fermer).mockResolvedValue(closedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.handleChangeStatut('fermer')
      })

      expect(chantiersService.fermer).toHaveBeenCalledWith('1')
    })
  })

  describe('team management', () => {
    it('ajoute un conducteur', async () => {
      const updatedChantier = {
        ...mockChantier,
        conducteurs: [...mockChantier.conducteurs, mockUsers[0]],
      }
      vi.mocked(chantiersService.addConducteur).mockResolvedValue(updatedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.openAddUserModal('conducteur')
      })

      await act(async () => {
        await result.current.handleAddUser('u3')
      })

      expect(chantiersService.addConducteur).toHaveBeenCalledWith('1', 'u3')
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Utilisateur ajoute',
        type: 'success',
      })
    })

    it('ajoute un chef', async () => {
      const updatedChantier = {
        ...mockChantier,
        chefs: [...mockChantier.chefs, mockUsers[1]],
      }
      vi.mocked(chantiersService.addChef).mockResolvedValue(updatedChantier as never)

      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.openAddUserModal('chef')
      })

      await act(async () => {
        await result.current.handleAddUser('u4')
      })

      expect(chantiersService.addChef).toHaveBeenCalledWith('1', 'u4')
    })

    it('retire un utilisateur avec undo', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.handleRemoveUser('u1', 'conducteur')
      })

      // Verifie que l'utilisateur est retire de la liste localement (optimistic update via setQueryData)
      await waitFor(() => {
        expect(result.current.chantier?.conducteurs).not.toContainEqual(
          expect.objectContaining({ id: 'u1' })
        )
      })

      // Verifie que showUndoToast a ete appele
      expect(mockShowUndoToast).toHaveBeenCalled()
    })
  })

  describe('delete chantier', () => {
    it('supprime avec undo et redirige', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      act(() => {
        result.current.handleDeleteChantier()
      })

      expect(mockNavigate).toHaveBeenCalledWith('/chantiers')
      expect(mockShowUndoToast).toHaveBeenCalled()
    })
  })

  describe('reload', () => {
    it('recharge les donnees', async () => {
      const { result } = renderHook(
        () => useChantierDetail({ chantierId: '1' }),
        { wrapper }
      )

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      vi.clearAllMocks()

      await act(async () => {
        await result.current.reload()
      })

      expect(chantiersService.getById).toHaveBeenCalledWith('1')
      expect(chantiersService.getNavigationIds).toHaveBeenCalledWith('1')
    })
  })
})
