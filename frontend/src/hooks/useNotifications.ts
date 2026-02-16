/**
 * Hook React pour gerer les notifications in-app.
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  notificationsService,
  type Notification,
  type NotificationList,
} from '../services/notificationsApi'
import { logger } from '../services/logger'

export interface GroupedNotification {
  id: string // ID unique pour le groupe
  type: string
  isGroup: true
  count: number
  notifications: Notification[]
  latestNotification: Notification
  isExpanded?: boolean
}

export interface NotificationOrGroup {
  notification?: Notification
  group?: GroupedNotification
}

interface UseNotificationsReturn {
  notifications: Notification[]
  groupedNotifications: NotificationOrGroup[]
  unreadCount: number
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  markAsRead: (notificationId: number) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (notificationId: number) => Promise<void>
  toggleGroupExpanded: (groupId: string) => void
}

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data: NotificationList = await notificationsService.getNotifications(false, 0, 20)
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (err) {
      logger.error('Erreur chargement notifications', err, { context: 'useNotifications' })
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
      logger.error('Erreur marquage notification', err, { context: 'useNotifications' })
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
      logger.error('Erreur marquage toutes notifications', err, { context: 'useNotifications' })
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
      logger.error('Erreur suppression notification', err, { context: 'useNotifications' })
    }
  }, [])

  const toggleGroupExpanded = useCallback((groupId: string) => {
    setExpandedGroups((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(groupId)) {
        newSet.delete(groupId)
      } else {
        newSet.add(groupId)
      }
      return newSet
    })
  }, [])

  // Regroupement intelligent des notifications (5.1.2)
  // Si 3+ notifications du même type dans une fenêtre de 5 minutes, on les groupe
  const groupedNotifications = useMemo((): NotificationOrGroup[] => {
    const GROUPING_THRESHOLD = 3
    const TIME_WINDOW_MS = 5 * 60 * 1000 // 5 minutes

    // Types qui doivent être groupés
    const GROUPABLE_TYPES = ['mention', 'signalement_created', 'signalement_resolved', 'tache_assigned']

    // Grouper par type
    const byType = new Map<string, Notification[]>()
    notifications.forEach((notif) => {
      if (GROUPABLE_TYPES.includes(notif.type)) {
        if (!byType.has(notif.type)) {
          byType.set(notif.type, [])
        }
        byType.get(notif.type)!.push(notif)
      }
    })

    // Identifier les groupes (même type + fenêtre temporelle)
    const groups: GroupedNotification[] = []
    const groupedNotifIds = new Set<number>()

    byType.forEach((notifs, type) => {
      if (notifs.length < GROUPING_THRESHOLD) return

      // Trier par date décroissante
      const sorted = [...notifs].sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )

      // Créer des groupes temporels
      let currentGroup: Notification[] = []
      let groupStartTime: number | null = null

      sorted.forEach((notif) => {
        const notifTime = new Date(notif.created_at).getTime()

        if (!groupStartTime) {
          // Première notification du groupe
          currentGroup = [notif]
          groupStartTime = notifTime
        } else if (groupStartTime - notifTime <= TIME_WINDOW_MS) {
          // Dans la fenêtre temporelle
          currentGroup.push(notif)
        } else {
          // Fenêtre dépassée - finaliser le groupe si >= threshold
          if (currentGroup.length >= GROUPING_THRESHOLD) {
            const groupId = `${type}-${currentGroup[0].id}`
            groups.push({
              id: groupId,
              type,
              isGroup: true,
              count: currentGroup.length,
              notifications: currentGroup,
              latestNotification: currentGroup[0],
              isExpanded: expandedGroups.has(groupId),
            })
            currentGroup.forEach((n) => groupedNotifIds.add(n.id))
          }

          // Commencer un nouveau groupe
          currentGroup = [notif]
          groupStartTime = notifTime
        }
      })

      // Finaliser le dernier groupe si >= threshold
      if (currentGroup.length >= GROUPING_THRESHOLD) {
        const groupId = `${type}-${currentGroup[0].id}`
        groups.push({
          id: groupId,
          type,
          isGroup: true,
          count: currentGroup.length,
          notifications: currentGroup,
          latestNotification: currentGroup[0],
          isExpanded: expandedGroups.has(groupId),
        })
        currentGroup.forEach((n) => groupedNotifIds.add(n.id))
      }
    })

    // Construire la liste finale : groupes + notifications individuelles
    const result: NotificationOrGroup[] = []
    const processedGroupIds = new Set<string>()

    notifications.forEach((notif) => {
      if (groupedNotifIds.has(notif.id)) {
        // Cette notification fait partie d'un groupe
        const group = groups.find((g) =>
          g.notifications.some((n) => n.id === notif.id)
        )
        if (group && !processedGroupIds.has(group.id)) {
          result.push({ group })
          processedGroupIds.add(group.id)
        }
      } else {
        // Notification individuelle
        result.push({ notification: notif })
      }
    })

    return result
  }, [notifications, expandedGroups])

  return {
    notifications,
    groupedNotifications,
    unreadCount,
    loading,
    error,
    refresh: fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    toggleGroupExpanded,
  }
}
