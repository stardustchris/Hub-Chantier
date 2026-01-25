/**
 * Dropdown des notifications avec support du detail et actions.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bell,
  MessageCircle,
  AtSign,
  Heart,
  FileText,
  Building2,
  AlertTriangle,
  CheckSquare,
  X,
  Loader2,
  ExternalLink,
} from 'lucide-react'
import { useNotifications } from '../../hooks/useNotifications'
import { formatRelativeTime, type Notification } from '../../services/notificationsApi'

interface NotificationDropdownProps {
  isOpen: boolean
  onClose: () => void
}

function getNotificationIcon(type: string) {
  const iconClass = 'w-5 h-5'
  switch (type) {
    case 'comment_added':
      return <MessageCircle className={`${iconClass} text-blue-500`} />
    case 'mention':
      return <AtSign className={`${iconClass} text-purple-500`} />
    case 'like_added':
      return <Heart className={`${iconClass} text-red-500`} />
    case 'document_added':
      return <FileText className={`${iconClass} text-green-500`} />
    case 'chantier_assignment':
      return <Building2 className={`${iconClass} text-orange-500`} />
    case 'signalement_created':
    case 'signalement_resolved':
      return <AlertTriangle className={`${iconClass} text-yellow-500`} />
    case 'tache_assigned':
    case 'tache_due':
      return <CheckSquare className={`${iconClass} text-indigo-500`} />
    default:
      return <Bell className={`${iconClass} text-gray-500`} />
  }
}

export default function NotificationDropdown({ isOpen, onClose }: NotificationDropdownProps) {
  const navigate = useNavigate()
  const {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead,
  } = useNotifications()

  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)

  const handleNotificationClick = async (notification: Notification) => {
    // Marquer comme lue
    if (!notification.is_read) {
      await markAsRead(notification.id)
    }

    // Afficher le detail ou naviguer selon le type
    if (notification.related_document_id || notification.type === 'document_added') {
      // Ouvrir le popup de detail pour les documents
      setSelectedNotification(notification)
    } else if (notification.related_post_id) {
      // Naviguer vers le dashboard (le post)
      onClose()
      navigate('/')
    } else if (notification.related_chantier_id) {
      // Naviguer vers le chantier
      onClose()
      navigate(`/chantiers/${notification.related_chantier_id}`)
    } else {
      // Afficher le popup de detail
      setSelectedNotification(notification)
    }
  }

  const handleViewDocument = () => {
    if (selectedNotification?.related_document_id) {
      onClose()
      navigate(`/documents?id=${selectedNotification.related_document_id}`)
    }
    setSelectedNotification(null)
  }

  const handleViewChantier = () => {
    if (selectedNotification?.related_chantier_id) {
      onClose()
      navigate(`/chantiers/${selectedNotification.related_chantier_id}`)
    }
    setSelectedNotification(null)
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay pour fermer */}
      <div className="fixed inset-0 z-10" onClick={onClose} />

      {/* Dropdown */}
      <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border z-20 max-w-[calc(100vw-2rem)]">
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">
            Notifications
            {unreadCount > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({unreadCount} non lues)
              </span>
            )}
          </h3>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Tout marquer lu
            </button>
          )}
        </div>

        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
              Chargement...
            </div>
          ) : notifications.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              Aucune notification
            </div>
          ) : (
            notifications.map((notif) => (
              <div
                key={notif.id}
                onClick={() => handleNotificationClick(notif)}
                className={`px-4 py-3 border-b last:border-b-0 hover:bg-gray-50 cursor-pointer flex gap-3 ${
                  !notif.is_read ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getNotificationIcon(notif.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {notif.title}
                  </p>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {notif.message}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatRelativeTime(notif.created_at)}
                  </p>
                </div>
                {!notif.is_read && (
                  <div className="flex-shrink-0">
                    <span className="w-2 h-2 bg-primary-500 rounded-full inline-block" />
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {notifications.length > 0 && (
          <div className="px-4 py-2 border-t bg-gray-50">
            <button
              onClick={() => {
                onClose()
                navigate('/notifications')
              }}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium w-full text-center"
            >
              Voir toutes les notifications
            </button>
          </div>
        )}
      </div>

      {/* Modal de detail notification */}
      {selectedNotification && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={() => setSelectedNotification(null)}
          />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="px-4 py-3 border-b flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getNotificationIcon(selectedNotification.type)}
                  <h3 className="font-semibold text-gray-900">
                    {selectedNotification.title}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedNotification(null)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-4">
                <p className="text-gray-700 mb-4">{selectedNotification.message}</p>

                {selectedNotification.chantier_name && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Chantier</p>
                    <p className="font-medium text-gray-900">
                      {selectedNotification.chantier_name}
                    </p>
                  </div>
                )}

                <p className="text-xs text-gray-400 mb-4">
                  {formatRelativeTime(selectedNotification.created_at)}
                </p>

                <div className="flex gap-2">
                  {selectedNotification.related_document_id && (
                    <button
                      onClick={handleViewDocument}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <FileText className="w-4 h-4" />
                      Voir le document
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  )}

                  {selectedNotification.related_chantier_id && !selectedNotification.related_document_id && (
                    <button
                      onClick={handleViewChantier}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <Building2 className="w-4 h-4" />
                      Voir le chantier
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  )}

                  <button
                    onClick={() => setSelectedNotification(null)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Fermer
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  )
}
