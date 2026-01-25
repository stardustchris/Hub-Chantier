/**
 * Tests pour le hook useNotifications
 * Gestion des notifications in-app
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useNotifications } from './useNotifications'

// Mock du service
vi.mock('../services/notificationsApi', () => ({
  notificationsService: {
    getNotifications: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    deleteNotification: vi.fn(),
  },
}))

import { notificationsService } from '../services/notificationsApi'

const mockNotifications: any[] = [
  {
    id: 1,
    user_id: 1,
    title: 'Nouvelle affectation',
    message: 'Vous avez ete affecte au chantier Villa Lyon',
    notification_type: 'affectation',
    is_read: false,
    read_at: null,
    created_at: '2024-01-15T10:00:00Z',
    data: { chantier_id: 1 },
  },
  {
    id: 2,
    user_id: 1,
    title: 'Pointage valide',
    message: 'Votre pointage du 14/01 a ete valide',
    notification_type: 'pointage',
    is_read: true,
    read_at: '2024-01-15T11:00:00Z',
    created_at: '2024-01-15T09:00:00Z',
    data: {},
  },
  {
    id: 3,
    user_id: 1,
    title: 'Nouveau signalement',
    message: 'Un signalement urgent a ete cree',
    notification_type: 'signalement',
    is_read: false,
    read_at: null,
    created_at: '2024-01-15T08:00:00Z',
    data: { signalement_id: 5 },
  },
]

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(notificationsService.getNotifications).mockResolvedValue({
      notifications: mockNotifications,
      total: 3,
      unread_count: 2,
    })
    vi.mocked(notificationsService.markAsRead).mockResolvedValue(undefined)
    vi.mocked(notificationsService.markAllAsRead).mockResolvedValue(undefined)
    vi.mocked(notificationsService.deleteNotification).mockResolvedValue(undefined)
  })

  describe('etat initial', () => {
    it('initialise avec les valeurs par defaut', () => {
      const { result } = renderHook(() => useNotifications())

      expect(result.current.notifications).toEqual([])
      expect(result.current.unreadCount).toBe(0)
      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('retourne les fonctions requises', () => {
      const { result } = renderHook(() => useNotifications())

      expect(typeof result.current.refresh).toBe('function')
      expect(typeof result.current.markAsRead).toBe('function')
      expect(typeof result.current.markAllAsRead).toBe('function')
      expect(typeof result.current.deleteNotification).toBe('function')
    })
  })

  describe('chargement des notifications', () => {
    it('charge les notifications au montage', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(notificationsService.getNotifications).toHaveBeenCalledWith(false, 0, 20)
      expect(result.current.notifications).toEqual(mockNotifications)
      expect(result.current.unreadCount).toBe(2)
    })

    it('gere les erreurs de chargement', async () => {
      vi.mocked(notificationsService.getNotifications).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe('Impossible de charger les notifications')
      expect(result.current.notifications).toEqual([])
    })
  })

  describe('refresh', () => {
    it('refresh recharge les notifications', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      vi.mocked(notificationsService.getNotifications).mockClear()

      await act(async () => {
        await result.current.refresh()
      })

      expect(notificationsService.getNotifications).toHaveBeenCalledTimes(1)
    })
  })

  describe('markAsRead', () => {
    it('marque une notification comme lue', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const notificationId = 1
      await act(async () => {
        await result.current.markAsRead(notificationId)
      })

      expect(notificationsService.markAsRead).toHaveBeenCalledWith(notificationId)

      // Verifier la mise a jour locale
      const updatedNotification = result.current.notifications.find((n) => n.id === notificationId)
      expect(updatedNotification?.is_read).toBe(true)
      expect(updatedNotification?.read_at).toBeTruthy()
    })

    it('decremente le compteur unread', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.unreadCount).toBe(2)

      await act(async () => {
        await result.current.markAsRead(1)
      })

      expect(result.current.unreadCount).toBe(1)
    })

    it('gere les erreurs silencieusement', async () => {
      vi.mocked(notificationsService.markAsRead).mockRejectedValue(new Error('Error'))

      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne doit pas lever d'exception
      await act(async () => {
        await result.current.markAsRead(1)
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('markAllAsRead', () => {
    it('marque toutes les notifications comme lues', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.markAllAsRead()
      })

      expect(notificationsService.markAllAsRead).toHaveBeenCalled()

      // Verifier que toutes sont marquees comme lues
      result.current.notifications.forEach((n) => {
        expect(n.is_read).toBe(true)
        expect(n.read_at).toBeTruthy()
      })
    })

    it('met le compteur unread a 0', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.unreadCount).toBe(2)

      await act(async () => {
        await result.current.markAllAsRead()
      })

      expect(result.current.unreadCount).toBe(0)
    })

    it('gere les erreurs silencieusement', async () => {
      vi.mocked(notificationsService.markAllAsRead).mockRejectedValue(new Error('Error'))

      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne doit pas lever d'exception
      await act(async () => {
        await result.current.markAllAsRead()
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('deleteNotification', () => {
    it('supprime une notification', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.notifications).toHaveLength(3)

      await act(async () => {
        await result.current.deleteNotification(1)
      })

      expect(notificationsService.deleteNotification).toHaveBeenCalledWith(1)
      expect(result.current.notifications).toHaveLength(2)
      expect(result.current.notifications.find((n) => n.id === 1)).toBeUndefined()
    })

    it('recalcule le compteur unread apres suppression', async () => {
      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Supprimer une notification non lue (id=1)
      await act(async () => {
        await result.current.deleteNotification(1)
      })

      // Recalcul: reste id=2 (lu) et id=3 (non lu) = 1 non lu
      expect(result.current.unreadCount).toBe(1)
    })

    it('gere les erreurs silencieusement', async () => {
      vi.mocked(notificationsService.deleteNotification).mockRejectedValue(new Error('Error'))

      const { result } = renderHook(() => useNotifications())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne doit pas lever d'exception
      await act(async () => {
        await result.current.deleteNotification(1)
      })

      expect(result.current.error).toBeNull()
    })
  })
})
