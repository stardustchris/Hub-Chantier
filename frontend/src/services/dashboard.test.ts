import { describe, it, expect, vi, beforeEach } from 'vitest'
import { dashboardService } from './dashboard'
import api from './api'

vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('dashboardService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getFeed', () => {
    it('should fetch feed with default params', async () => {
      const mockFeed = {
        items: [{ id: '1', contenu: 'Test post' }],
        total: 1,
        page: 1,
        pages: 1,
      }
      vi.mocked(api.get).mockResolvedValue({ data: mockFeed })

      const result = await dashboardService.getFeed()

      expect(api.get).toHaveBeenCalledWith('/api/dashboard/feed', { params: {} })
      expect(result.items).toHaveLength(1)
    })

    it('should fetch feed with pagination params', async () => {
      const mockFeed = { items: [], total: 0, page: 2, pages: 5 }
      vi.mocked(api.get).mockResolvedValue({ data: mockFeed })

      await dashboardService.getFeed({ page: 2, size: 10 })

      expect(api.get).toHaveBeenCalledWith('/api/dashboard/feed', {
        params: { page: 2, size: 10 },
      })
    })
  })

  describe('createPost', () => {
    it('should create a new post', async () => {
      const newPost = { contenu: 'New post content' }
      const mockCreatedPost = { id: '123', ...newPost }
      vi.mocked(api.post).mockResolvedValue({ data: mockCreatedPost })

      const result = await dashboardService.createPost(newPost)

      expect(api.post).toHaveBeenCalledWith('/api/dashboard/posts', newPost)
      expect(result.id).toBe('123')
    })
  })

  describe('getPost', () => {
    it('should fetch a single post', async () => {
      const mockPost = { id: '123', contenu: 'Test' }
      vi.mocked(api.get).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.getPost('123')

      expect(api.get).toHaveBeenCalledWith('/api/dashboard/posts/123')
      expect(result).toEqual(mockPost)
    })
  })

  describe('deletePost', () => {
    it('should delete a post', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: null })

      await dashboardService.deletePost('123')

      expect(api.delete).toHaveBeenCalledWith('/api/dashboard/posts/123')
    })
  })

  describe('pinPost', () => {
    it('should pin a post', async () => {
      const mockPost = { id: '123', is_pinned: true }
      vi.mocked(api.post).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.pinPost('123')

      expect(api.post).toHaveBeenCalledWith('/api/dashboard/posts/123/pin')
      expect(result.is_pinned).toBe(true)
    })
  })

  describe('unpinPost', () => {
    it('should unpin a post', async () => {
      const mockPost = { id: '123', is_pinned: false }
      vi.mocked(api.delete).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.unpinPost('123')

      expect(api.delete).toHaveBeenCalledWith('/api/dashboard/posts/123/pin')
      expect(result.is_pinned).toBe(false)
    })
  })

  describe('addComment', () => {
    it('should add a comment to a post', async () => {
      const comment = { contenu: 'Great post!' }
      const mockPost = {
        id: '123',
        comments: [{ id: 'c1', contenu: 'Great post!' }],
      }
      vi.mocked(api.post).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.addComment('123', comment)

      expect(api.post).toHaveBeenCalledWith(
        '/api/dashboard/posts/123/comments',
        comment
      )
      expect((result as any).comments).toHaveLength(1)
    })
  })

  describe('likePost', () => {
    it('should like a post', async () => {
      const mockPost = { id: '123', likes_count: 1, is_liked: true }
      vi.mocked(api.post).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.likePost('123')

      expect(api.post).toHaveBeenCalledWith('/api/dashboard/posts/123/like')
      expect((result as any).is_liked).toBe(true)
    })
  })

  describe('unlikePost', () => {
    it('should unlike a post', async () => {
      const mockPost = { id: '123', likes_count: 0, is_liked: false }
      vi.mocked(api.delete).mockResolvedValue({ data: mockPost })

      const result = await dashboardService.unlikePost('123')

      expect(api.delete).toHaveBeenCalledWith('/api/dashboard/posts/123/like')
      expect((result as any).is_liked).toBe(false)
    })
  })
})
