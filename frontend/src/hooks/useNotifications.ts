/**
 * Hook React pour gerer les notifications in-app.
 */

import { useState, useEffect, useCallback } from 'react'
import {
  notificationsService,
  type Notification,
  type NotificationList,
} from '../services/notificationsApi'

interface UseNotificationsReturn {
  notifications: Notification[]
  unreadCount: number
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  markAsRead: (notificationId: number) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (notificationId: number) => Promise<void>
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data: NotificationList = await notificationsService.getNotifications(false, 0, 20)
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (err) {
      console.error('Erreur chargement notifications:', err)
      setError('Impossible de charger les notifications')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNotifications()

    // Rafraichir toutes les 30 secondes
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [fetchNotifications])

  const markAsRead = useCallback(async (notificationId: number) => {
    try {
      await notificationsService.markAsRead(notificationId)
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
        )
      )
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (err) {
      console.error('Erreur marquage notification:', err)
    }
  }, [])

  const markAllAsRead = useCallback(async () => {
    try {
      await notificationsService.markAllAsRead()
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      )
      setUnreadCount(0)
    } catch (err) {
      console.error('Erreur marquage toutes notifications:', err)
    }
  }, [])

  const deleteNotification = useCallback(async (notificationId: number) => {
    try {
      await notificationsService.deleteNotification(notificationId)
      setNotifications((prev) => prev.filter((n) => n.id !== notificationId))
      // Recalculer le compteur
      setNotifications((prev) => {
        const unread = prev.filter((n) => !n.is_read).length
        setUnreadCount(unread)
        return prev
      })
    } catch (err) {
      console.error('Erreur suppression notification:', err)
    }
  }, [])

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  }
}
