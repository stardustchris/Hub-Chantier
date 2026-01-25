/**
 * Service API pour les notifications in-app.
 *
 * Gere la recuperation, le marquage comme lu et la suppression
 * des notifications depuis le backend.
 */

import api from './api'

export interface Notification {
  id: number
  user_id: number
  type: string
  title: string
  message: string
  is_read: boolean
  read_at: string | null
  related_post_id: number | null
  related_comment_id: number | null
  related_chantier_id: number | null
  related_document_id: number | null
  triggered_by_user_id: number | null
  triggered_by_user_name?: string
  chantier_name?: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface NotificationList {
  notifications: Notification[]
  unread_count: number
  total: number
}

export interface MarkAsReadRequest {
  notification_ids?: number[] | null
}

export const notificationsService = {
  /**
   * Recupere les notifications de l'utilisateur connecte.
   */
  async getNotifications(
    unreadOnly: boolean = false,
    skip: number = 0,
    limit: number = 50
  ): Promise<NotificationList> {
    const params = { unread_only: unreadOnly, skip, limit }
    const response = await api.get<NotificationList>('/api/notifications', { params })
    return response.data
  },

  /**
   * Recupere le nombre de notifications non lues.
   */
  async getUnreadCount(): Promise<number> {
    const response = await api.get<{ unread_count: number }>('/api/notifications/unread-count')
    return response.data.unread_count
  },

  /**
   * Marque une notification comme lue.
   */
  async markAsRead(notificationId: number): Promise<void> {
    await api.patch(`/api/notifications/${notificationId}/read`)
  },

  /**
   * Marque plusieurs notifications comme lues.
   * Si notification_ids est null, marque toutes les notifications.
   */
  async markManyAsRead(notificationIds?: number[] | null): Promise<{ marked_count: number }> {
    const response = await api.patch<{ marked_count: number }>('/api/notifications/read', {
      notification_ids: notificationIds ?? null,
    })
    return response.data
  },

  /**
   * Marque toutes les notifications comme lues.
   */
  async markAllAsRead(): Promise<{ marked_count: number }> {
    return this.markManyAsRead(null)
  },

  /**
   * Supprime une notification.
   */
  async deleteNotification(notificationId: number): Promise<void> {
    await api.delete(`/api/notifications/${notificationId}`)
  },

  /**
   * Supprime toutes les notifications.
   */
  async deleteAllNotifications(): Promise<{ deleted_count: number }> {
    const response = await api.delete<{ deleted_count: number }>('/api/notifications')
    return response.data
  },
}

/**
 * Formate le temps relatif pour l'affichage.
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return "A l'instant"
  if (diffMin < 60) return `Il y a ${diffMin} min`
  if (diffHours < 24) return `Il y a ${diffHours}h`
  if (diffDays < 7) return `Il y a ${diffDays}j`

  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

/**
 * Retourne l'icone appropriee pour un type de notification.
 */
export function getNotificationIcon(type: string): string {
  switch (type) {
    case 'comment_added':
      return 'MessageCircle'
    case 'mention':
      return 'AtSign'
    case 'like_added':
      return 'Heart'
    case 'document_added':
      return 'FileText'
    case 'chantier_assignment':
      return 'Building2'
    case 'signalement_created':
    case 'signalement_resolved':
      return 'AlertTriangle'
    case 'tache_assigned':
    case 'tache_due':
      return 'CheckSquare'
    default:
      return 'Bell'
  }
}

export default notificationsService
