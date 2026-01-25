/**
 * Tests pour le service notificationsApi
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { notificationsService, formatRelativeTime, getNotificationIcon } from './notificationsApi'
import api from './api'

vi.mock('./api')

describe('notificationsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getNotifications', () => {
    it('fetches notifications with default params', async () => {
      const mockResponse = {
        data: {
          notifications: [{ id: 1, title: 'Test' }],
          unread_count: 1,
          total: 1,
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await notificationsService.getNotifications()

      expect(api.get).toHaveBeenCalledWith('/api/notifications', {
        params: { unread_only: false, skip: 0, limit: 50 },
      })
      expect(result.notifications).toHaveLength(1)
    })

    it('fetches only unread notifications', async () => {
      const mockResponse = {
        data: { notifications: [], unread_count: 0, total: 0 },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await notificationsService.getNotifications(true)

      expect(api.get).toHaveBeenCalledWith('/api/notifications', {
        params: { unread_only: true, skip: 0, limit: 50 },
      })
    })

    it('supports pagination', async () => {
      const mockResponse = {
        data: { notifications: [], unread_count: 0, total: 100 },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await notificationsService.getNotifications(false, 20, 10)

      expect(api.get).toHaveBeenCalledWith('/api/notifications', {
        params: { unread_only: false, skip: 20, limit: 10 },
      })
    })
  })

  describe('getUnreadCount', () => {
    it('fetches unread count', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { unread_count: 5 },
      })

      const count = await notificationsService.getUnreadCount()

      expect(api.get).toHaveBeenCalledWith('/api/notifications/unread-count')
      expect(count).toBe(5)
    })
  })

  describe('markAsRead', () => {
    it('marks a single notification as read', async () => {
      vi.mocked(api.patch).mockResolvedValue({})

      await notificationsService.markAsRead(1)

      expect(api.patch).toHaveBeenCalledWith('/api/notifications/1/read')
    })
  })

  describe('markManyAsRead', () => {
    it('marks multiple notifications as read', async () => {
      vi.mocked(api.patch).mockResolvedValue({
        data: { marked_count: 3 },
      })

      const result = await notificationsService.markManyAsRead([1, 2, 3])

      expect(api.patch).toHaveBeenCalledWith('/api/notifications/read', {
        notification_ids: [1, 2, 3],
      })
      expect(result.marked_count).toBe(3)
    })

    it('marks all notifications when no IDs provided', async () => {
      vi.mocked(api.patch).mockResolvedValue({
        data: { marked_count: 10 },
      })

      const result = await notificationsService.markManyAsRead(null)

      expect(api.patch).toHaveBeenCalledWith('/api/notifications/read', {
        notification_ids: null,
      })
      expect(result.marked_count).toBe(10)
    })

    it('marks all notifications when undefined', async () => {
      vi.mocked(api.patch).mockResolvedValue({
        data: { marked_count: 5 },
      })

      const result = await notificationsService.markManyAsRead()

      expect(api.patch).toHaveBeenCalledWith('/api/notifications/read', {
        notification_ids: null,
      })
      expect(result.marked_count).toBe(5)
    })
  })

  describe('markAllAsRead', () => {
    it('marks all notifications as read', async () => {
      vi.mocked(api.patch).mockResolvedValue({
        data: { marked_count: 15 },
      })

      const result = await notificationsService.markAllAsRead()

      expect(api.patch).toHaveBeenCalledWith('/api/notifications/read', {
        notification_ids: null,
      })
      expect(result.marked_count).toBe(15)
    })
  })

  describe('deleteNotification', () => {
    it('deletes a single notification', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await notificationsService.deleteNotification(1)

      expect(api.delete).toHaveBeenCalledWith('/api/notifications/1')
    })
  })

  describe('deleteAllNotifications', () => {
    it('deletes all notifications', async () => {
      vi.mocked(api.delete).mockResolvedValue({
        data: { deleted_count: 20 },
      })

      const result = await notificationsService.deleteAllNotifications()

      expect(api.delete).toHaveBeenCalledWith('/api/notifications')
      expect(result.deleted_count).toBe(20)
    })
  })
})

describe('formatRelativeTime', () => {
  it('formats instant time', () => {
    const now = new Date()
    const result = formatRelativeTime(now.toISOString())
    expect(result).toBe("A l'instant")
  })

  it('formats minutes ago', () => {
    const date = new Date(Date.now() - 5 * 60 * 1000)
    const result = formatRelativeTime(date.toISOString())
    expect(result).toBe('Il y a 5 min')
  })

  it('formats hours ago', () => {
    const date = new Date(Date.now() - 3 * 60 * 60 * 1000)
    const result = formatRelativeTime(date.toISOString())
    expect(result).toBe('Il y a 3h')
  })

  it('formats days ago', () => {
    const date = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
    const result = formatRelativeTime(date.toISOString())
    expect(result).toBe('Il y a 2j')
  })

  it('formats older dates as date string', () => {
    const date = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
    const result = formatRelativeTime(date.toISOString())
    // Should be formatted as "15 janv." or similar
    expect(result).toMatch(/^\d{1,2}\s\w+\.?$/)
  })
})

describe('getNotificationIcon', () => {
  it('returns MessageCircle for comment_added', () => {
    expect(getNotificationIcon('comment_added')).toBe('MessageCircle')
  })

  it('returns AtSign for mention', () => {
    expect(getNotificationIcon('mention')).toBe('AtSign')
  })

  it('returns Heart for like_added', () => {
    expect(getNotificationIcon('like_added')).toBe('Heart')
  })

  it('returns FileText for document_added', () => {
    expect(getNotificationIcon('document_added')).toBe('FileText')
  })

  it('returns Building2 for chantier_assignment', () => {
    expect(getNotificationIcon('chantier_assignment')).toBe('Building2')
  })

  it('returns AlertTriangle for signalement_created', () => {
    expect(getNotificationIcon('signalement_created')).toBe('AlertTriangle')
  })

  it('returns AlertTriangle for signalement_resolved', () => {
    expect(getNotificationIcon('signalement_resolved')).toBe('AlertTriangle')
  })

  it('returns CheckSquare for tache_assigned', () => {
    expect(getNotificationIcon('tache_assigned')).toBe('CheckSquare')
  })

  it('returns CheckSquare for tache_due', () => {
    expect(getNotificationIcon('tache_due')).toBe('CheckSquare')
  })

  it('returns Bell for unknown type', () => {
    expect(getNotificationIcon('unknown_type')).toBe('Bell')
  })

  it('returns Bell for empty string', () => {
    expect(getNotificationIcon('')).toBe('Bell')
  })
})
