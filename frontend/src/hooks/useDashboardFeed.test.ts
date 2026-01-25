/**
 * Tests pour le hook useDashboardFeed
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useDashboardFeed } from './useDashboardFeed'

// Mock des dépendances
vi.mock('../services/dashboard', () => ({
  dashboardService: {
    getFeed: vi.fn(),
    createPost: vi.fn(),
    getPost: vi.fn(),
    likePost: vi.fn(),
    unlikePost: vi.fn(),
    deletePost: vi.fn(),
    pinPost: vi.fn(),
    unpinPost: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', prenom: 'Jean', nom: 'Dupont' },
  }),
}))

import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'

// Mock data with any type to avoid TS errors
const mockPosts: any[] = [
  {
    id: '1',
    contenu: 'Post 1',
    is_pinned: false,
    created_at: '2024-01-15T10:00:00Z',
    likes: [],
    likes_count: 0,
  },
  {
    id: '2',
    contenu: 'Post 2',
    is_pinned: true,
    created_at: '2024-01-14T10:00:00Z',
    likes: [],
    likes_count: 0,
  },
]

const mockChantiers: any[] = [
  { id: '1', code: 'CH001', nom: 'Chantier A' },
  { id: '2', code: 'CH002', nom: 'Chantier B' },
]

describe('useDashboardFeed', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(dashboardService.getFeed).mockResolvedValue({
      items: mockPosts,
      total: 2,
      page: 1,
      size: 20,
      pages: 1,
    })
    vi.mocked(chantiersService.list).mockResolvedValue({
      items: mockChantiers,
      total: 2,
      page: 1,
      size: 100,
      pages: 1,
    })
  })

  describe('chargement initial', () => {
    it('charge le feed au montage', async () => {
      renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(dashboardService.getFeed).toHaveBeenCalledWith({ page: 1, size: 20 })
      })
    })

    it('charge les chantiers au montage', async () => {
      renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(chantiersService.list).toHaveBeenCalledWith({ size: 100, statut: 'en_cours' })
      })
    })

    it('met à jour les posts après chargement', async () => {
      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.posts).toEqual(mockPosts)
      })
    })
  })

  describe('sortedPosts', () => {
    it('trie les posts épinglés en premier', async () => {
      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.sortedPosts[0].id).toBe('2') // pinned
        expect(result.current.sortedPosts[1].id).toBe('1')
      })
    })
  })

  describe('état du composeur de post', () => {
    it('a les valeurs initiales correctes', () => {
      const { result } = renderHook(() => useDashboardFeed())

      expect(result.current.newPostContent).toBe('')
      expect(result.current.targetType).toBe('tous')
      expect(result.current.selectedChantiers).toEqual([])
      expect(result.current.isUrgent).toBe(false)
      expect(result.current.isPosting).toBe(false)
    })

    it('permet de modifier le contenu du post', () => {
      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setNewPostContent('Mon nouveau post')
      })

      expect(result.current.newPostContent).toBe('Mon nouveau post')
    })

    it('permet de modifier le type de cible', () => {
      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setTargetType('chantiers')
      })

      expect(result.current.targetType).toBe('chantiers')
    })

    it('permet de modifier les chantiers sélectionnés', () => {
      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setSelectedChantiers(['1', '2'])
      })

      expect(result.current.selectedChantiers).toEqual(['1', '2'])
    })

    it('permet de modifier le flag urgent', () => {
      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setIsUrgent(true)
      })

      expect(result.current.isUrgent).toBe(true)
    })
  })

  describe('handleCreatePost', () => {
    it('ne fait rien si contenu vide', async () => {
      const { result } = renderHook(() => useDashboardFeed())

      await act(async () => {
        await result.current.handleCreatePost()
      })

      expect(dashboardService.createPost).not.toHaveBeenCalled()
    })

    it('crée un post avec les bonnes données', async () => {
      vi.mocked(dashboardService.createPost).mockResolvedValue({ id: '3' } as any)

      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setNewPostContent('Mon post')
        result.current.setIsUrgent(true)
      })

      await act(async () => {
        await result.current.handleCreatePost()
      })

      expect(dashboardService.createPost).toHaveBeenCalledWith({
        contenu: 'Mon post',
        target_type: 'tous',
        target_chantier_ids: undefined,
        is_urgent: true,
      })
    })

    it('réinitialise le formulaire après création', async () => {
      vi.mocked(dashboardService.createPost).mockResolvedValue({ id: '3' } as any)

      const { result } = renderHook(() => useDashboardFeed())

      act(() => {
        result.current.setNewPostContent('Mon post')
        result.current.setIsUrgent(true)
        result.current.setTargetType('chantiers')
        result.current.setSelectedChantiers(['1'])
      })

      await act(async () => {
        await result.current.handleCreatePost()
      })

      expect(result.current.newPostContent).toBe('')
      expect(result.current.isUrgent).toBe(false)
      expect(result.current.targetType).toBe('tous')
      expect(result.current.selectedChantiers).toEqual([])
    })
  })

  describe('handleLike', () => {
    it('appelle likePost si non liké', async () => {
      vi.mocked(dashboardService.likePost).mockResolvedValue(undefined as any)
      vi.mocked(dashboardService.getPost).mockResolvedValue({
        ...mockPosts[0],
        likes_count: 1,
      } as any)

      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.posts.length).toBeGreaterThan(0)
      })

      await act(async () => {
        await result.current.handleLike('1', false)
      })

      expect(dashboardService.likePost).toHaveBeenCalledWith('1')
    })

    it('appelle unlikePost si déjà liké', async () => {
      vi.mocked(dashboardService.unlikePost).mockResolvedValue(undefined as any)
      vi.mocked(dashboardService.getPost).mockResolvedValue({
        ...mockPosts[0],
        likes_count: 0,
      } as any)

      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.posts.length).toBeGreaterThan(0)
      })

      await act(async () => {
        await result.current.handleLike('1', true)
      })

      expect(dashboardService.unlikePost).toHaveBeenCalledWith('1')
    })
  })

  describe('handleDelete', () => {
    beforeEach(() => {
      vi.spyOn(window, 'confirm').mockReturnValue(true)
    })

    it('supprime le post après confirmation', async () => {
      vi.mocked(dashboardService.deletePost).mockResolvedValue(undefined)

      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.posts.length).toBeGreaterThan(0)
      })

      await act(async () => {
        await result.current.handleDelete('1')
      })

      expect(dashboardService.deletePost).toHaveBeenCalledWith('1')
    })

    it('ne supprime pas si annulation', async () => {
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      const { result } = renderHook(() => useDashboardFeed())

      await act(async () => {
        await result.current.handleDelete('1')
      })

      expect(dashboardService.deletePost).not.toHaveBeenCalled()
    })
  })

  describe('pagination', () => {
    it('indique hasMore si plus de pages', async () => {
      vi.mocked(dashboardService.getFeed).mockResolvedValue({
        items: mockPosts as any,
        total: 40,
        page: 1,
        size: 20,
        pages: 2,
      })

      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.hasMore).toBe(true)
      })
    })

    it('charge la page suivante', async () => {
      vi.mocked(dashboardService.getFeed)
        .mockResolvedValueOnce({
          items: mockPosts as any,
          total: 40,
          page: 1,
          size: 20,
          pages: 2,
        })
        .mockResolvedValueOnce({
          items: [{ id: '3', contenu: 'Post 3' }] as any,
          total: 40,
          page: 2,
          size: 20,
          pages: 2,
        })

      const { result } = renderHook(() => useDashboardFeed())

      await waitFor(() => {
        expect(result.current.hasMore).toBe(true)
      })

      await act(async () => {
        await result.current.loadFeed(2)
      })

      expect(dashboardService.getFeed).toHaveBeenCalledWith({ page: 2, size: 20 })
    })
  })
})
