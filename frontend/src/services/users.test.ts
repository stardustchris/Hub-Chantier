import { describe, it, expect, vi, beforeEach } from 'vitest'
import { usersService } from './users'
import api from './api'

vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('usersService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should fetch users with default params', async () => {
      const mockResponse = {
        data: {
          items: [{ id: '1', nom: 'Dupont', prenom: 'Jean' }],
          total: 1,
          page: 1,
          pages: 1,
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await usersService.list()

      expect(api.get).toHaveBeenCalledWith('/api/users', { params: {} })
      expect(result.items).toHaveLength(1)
      expect(result.total).toBe(1)
    })

    it('should fetch users with search params', async () => {
      const mockResponse = {
        data: { items: [], total: 0, page: 1, pages: 0 },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await usersService.list({ search: 'Jean', page: 2, size: 20 })

      expect(api.get).toHaveBeenCalledWith('/api/users', {
        params: { search: 'Jean', page: 2, size: 20 },
      })
    })

    it('should filter by role', async () => {
      const mockResponse = {
        data: { items: [], total: 0, page: 1, pages: 0 },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await usersService.list({ role: 'admin' })

      expect(api.get).toHaveBeenCalledWith('/api/users', {
        params: { role: 'admin' },
      })
    })

    it('should filter by is_active', async () => {
      const mockResponse = {
        data: { items: [], total: 0, page: 1, pages: 0 },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await usersService.list({ is_active: true })

      expect(api.get).toHaveBeenCalledWith('/api/users', {
        params: { is_active: true },
      })
    })
  })

  describe('getById', () => {
    it('should fetch a single user by id', async () => {
      const mockUser = { id: '123', nom: 'Dupont', prenom: 'Jean' }
      vi.mocked(api.get).mockResolvedValue({ data: mockUser })

      const result = await usersService.getById('123')

      expect(api.get).toHaveBeenCalledWith('/api/users/123')
      expect(result).toEqual(mockUser)
    })
  })

  describe('create', () => {
    it('should create a new user via auth/register', async () => {
      const newUser = {
        email: 'jean@test.com',
        password: 'password123',
        nom: 'Dupont',
        prenom: 'Jean',
        role: 'compagnon' as const,
        type_utilisateur: 'employe' as const,
      }
      const mockCreatedUser = { id: '456', ...newUser }
      vi.mocked(api.post).mockResolvedValue({ data: mockCreatedUser })

      const result = await usersService.create(newUser)

      expect(api.post).toHaveBeenCalledWith('/api/auth/register', newUser)
      expect(result.id).toBe('456')
    })
  })

  describe('update', () => {
    it('should update user data', async () => {
      const updateData = { nom: 'Martin' }
      const mockUpdatedUser = { id: '123', nom: 'Martin', prenom: 'Jean' }
      vi.mocked(api.put).mockResolvedValue({ data: mockUpdatedUser })

      const result = await usersService.update('123', updateData)

      expect(api.put).toHaveBeenCalledWith('/api/users/123', updateData)
      expect(result.nom).toBe('Martin')
    })
  })

  describe('activate/deactivate', () => {
    it('should activate a user', async () => {
      const mockUser = { id: '123', is_active: true }
      vi.mocked(api.post).mockResolvedValue({ data: mockUser })

      const result = await usersService.activate('123')

      expect(api.post).toHaveBeenCalledWith('/api/users/123/activate')
      expect(result.is_active).toBe(true)
    })

    it('should deactivate a user', async () => {
      const mockUser = { id: '123', is_active: false }
      vi.mocked(api.post).mockResolvedValue({ data: mockUser })

      const result = await usersService.deactivate('123')

      expect(api.post).toHaveBeenCalledWith('/api/users/123/deactivate')
      expect(result.is_active).toBe(false)
    })
  })

  describe('getNavigationIds', () => {
    it('should return navigation ids from fetched user list', async () => {
      const mockUsers = {
        data: {
          items: [
            { id: '121' },
            { id: '122' },
            { id: '123' },
            { id: '124' },
            { id: '125' },
          ],
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockUsers)

      const result = await usersService.getNavigationIds('123')

      expect(api.get).toHaveBeenCalledWith('/api/users', { params: { size: 500 } })
      expect(result).toEqual({ prevId: '122', nextId: '124' })
    })

    it('should return null prevId for first user', async () => {
      const mockUsers = {
        data: { items: [{ id: '121' }, { id: '122' }, { id: '123' }] },
      }
      vi.mocked(api.get).mockResolvedValue(mockUsers)

      const result = await usersService.getNavigationIds('121')

      expect(result.prevId).toBeNull()
      expect(result.nextId).toBe('122')
    })

    it('should return null nextId for last user', async () => {
      const mockUsers = {
        data: { items: [{ id: '121' }, { id: '122' }, { id: '123' }] },
      }
      vi.mocked(api.get).mockResolvedValue(mockUsers)

      const result = await usersService.getNavigationIds('123')

      expect(result.prevId).toBe('122')
      expect(result.nextId).toBeNull()
    })

    it('should return nulls on error', async () => {
      vi.mocked(api.get).mockRejectedValue(new Error('Network error'))

      const result = await usersService.getNavigationIds('123')

      expect(result).toEqual({ prevId: null, nextId: null })
    })
  })
})
