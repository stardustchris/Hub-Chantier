/**
 * Dropdown des notifications avec support du detail et actions.
 *
 * - Le dropdown reste ouvert jusqu'a clic externe
 * - Chaque notification ouvre un popup de detail
 * - Les documents sont previsualises/telechargeables
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logger } from '../../services/logger'
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
  Download,
  Eye,
  Settings,
  ChevronDown,
  ChevronUp,
  Users,
} from 'lucide-react'
import { useNotifications } from '../../hooks/useNotifications'
import { formatRelativeTime, type Notification } from '../../services/notificationsApi'
import { getDocument, downloadDocument, getDocumentPreviewUrl, formatFileSize } from '../../services/documents'
import type { Document } from '../../types/documents'
import NotificationPreferences from '../common/NotificationPreferences'

interface NotificationDropdownProps {
  isOpen: boolean
  onClose: () => void
}

interface DocumentInfo {
  loading: boolean
  error: string | null
  document: Document | null
  downloadUrl: string | null
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

function getGroupedNotificationTitle(type: string, count: number): string {
  switch (type) {
    case 'mention':
      return count === 2 ? '2 personnes vous ont mentionné' : `${count} personnes vous ont mentionné`
    case 'signalement_created':
      return count === 2 ? '2 nouveaux signalements' : `${count} nouveaux signalements`
    case 'signalement_resolved':
      return count === 2 ? '2 signalements résolus' : `${count} signalements résolus`
    case 'tache_assigned':
      return count === 2 ? '2 nouvelles tâches assignées' : `${count} nouvelles tâches assignées`
    default:
      return `${count} notifications`
  }
}

export default function NotificationDropdown({ isOpen, onClose }: NotificationDropdownProps) {
  const navigate = useNavigate()
  const {
    groupedNotifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead,
    toggleGroupExpanded,
  } = useNotifications()

  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)
  const [showPreferences, setShowPreferences] = useState(false)
  const [documentInfo, setDocumentInfo] = useState<DocumentInfo>({
    loading: false,
    error: null,
    document: null,
    downloadUrl: null,
  })

  // Charger les infos document quand on selectionne une notification document
  useEffect(() => {
    if (selectedNotification?.related_document_id) {
      setDocumentInfo({ loading: true, error: null, document: null, downloadUrl: null })

      Promise.all([
        getDocument(selectedNotification.related_document_id),
        downloadDocument(selectedNotification.related_document_id),
      ])
        .then(([doc, blob]) => {
          const url = window.URL.createObjectURL(blob)
          setDocumentInfo({
            loading: false,
            error: null,
            document: doc,
            downloadUrl: url,
          })
        })
        .catch((err) => {
          logger.error('Erreur chargement document', err, { context: 'NotificationDropdown' })
          setDocumentInfo({
            loading: false,
            error: 'Impossible de charger le document',
            document: null,
            downloadUrl: null,
          })
        })
    } else {
      setDocumentInfo({ loading: false, error: null, document: null, downloadUrl: null })
    }
  }, [selectedNotification?.related_document_id])

  // Toujours afficher le popup de detail au clic
  const handleNotificationClick = async (notification: Notification) => {
    // Marquer comme lue
    if (!notification.is_read) {
      await markAsRead(notification.id)
    }

    // Toujours ouvrir le popup de detail
    setSelectedNotification(notification)
  }

  const handleViewDocument = () => {
    if (selectedNotification?.related_document_id) {
      setSelectedNotification(null)
      onClose()
      navigate(`/documents?id=${selectedNotification.related_document_id}`)
    }
  }

  const handleDownloadDocument = () => {
    if (documentInfo.downloadUrl) {
      window.open(documentInfo.downloadUrl, '_blank')
    }
  }

  const handlePreviewDocument = () => {
    if (selectedNotification?.related_document_id) {
      const previewUrl = getDocumentPreviewUrl(selectedNotification.related_document_id)
      window.open(previewUrl, '_blank')
    }
  }

  const handleViewChantier = () => {
    if (selectedNotification?.related_chantier_id) {
      setSelectedNotification(null)
      onClose()
      navigate(`/chantiers/${selectedNotification.related_chantier_id}`)
    }
  }

  const handleViewPost = () => {
    if (selectedNotification?.related_post_id) {
      setSelectedNotification(null)
      onClose()
      navigate('/')
    }
  }

  const handleCloseDetail = () => {
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
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                Tout marquer lu
              </button>
            )}
            <button
              onClick={() => setShowPreferences(true)}
              className="p-1.5 hover:bg-gray-100 rounded"
              title="Préférences de notifications"
            >
              <Settings className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>

        <div className="max-h-96 overflow-y-auto">
          {loading ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
              Chargement...
            </div>
          ) : groupedNotifications.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <Bell className="w-8 h-8 mx-auto mb-2 text-gray-500" />
              Aucune notification
            </div>
          ) : (
            groupedNotifications.map((item) => {
              if (item.group) {
                // Afficher un groupe de notifications
                const group = item.group
                const hasUnread = group.notifications.some((n) => !n.is_read)

                return (
                  <div key={group.id}>
                    {/* En-tête du groupe */}
                    <div
                      onClick={() => toggleGroupExpanded(group.id)}
                      className={`px-4 py-3 border-b hover:bg-gray-50 cursor-pointer flex gap-3 ${
                        hasUnread ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="relative">
                          {getNotificationIcon(group.type)}
                          <div className="absolute -bottom-1 -right-1 bg-white rounded-full">
                            <Users className="w-3 h-3 text-gray-600" />
                          </div>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {getGroupedNotificationTitle(group.type, group.count)}
                        </p>
                        <p className="text-sm text-gray-600">
                          {group.latestNotification.message}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          {formatRelativeTime(group.latestNotification.created_at)}
                        </p>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        {hasUnread && (
                          <span className="w-2 h-2 bg-primary-500 rounded-full" />
                        )}
                        {group.isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </div>

                    {/* Notifications du groupe (si déplié) */}
                    {group.isExpanded && (
                      <div className="bg-gray-50">
                        {group.notifications.map((notif) => (
                          <div
                            key={notif.id}
                            onClick={() => handleNotificationClick(notif)}
                            className={`px-4 py-3 pl-12 border-b last:border-b-0 hover:bg-gray-100 cursor-pointer flex gap-3 ${
                              !notif.is_read ? 'bg-blue-100' : ''
                            }`}
                          >
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {notif.title}
                              </p>
                              <p className="text-sm text-gray-600 line-clamp-2">
                                {notif.message}
                              </p>
                              <p className="text-xs text-gray-600 mt-1">
                                {formatRelativeTime(notif.created_at)}
                              </p>
                            </div>
                            {!notif.is_read && (
                              <div className="flex-shrink-0">
                                <span className="w-2 h-2 bg-primary-500 rounded-full inline-block" />
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              } else if (item.notification) {
                // Notification individuelle
                const notif = item.notification
                return (
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
                      <p className="text-xs text-gray-600 mt-1">
                        {formatRelativeTime(notif.created_at)}
                      </p>
                    </div>
                    {!notif.is_read && (
                      <div className="flex-shrink-0">
                        <span className="w-2 h-2 bg-primary-500 rounded-full inline-block" />
                      </div>
                    )}
                  </div>
                )
              }
              return null
            })
          )}
        </div>

        {groupedNotifications.length > 0 && (
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

      {/* Modal préférences */}
      <NotificationPreferences
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
      />

      {/* Modal de detail notification */}
      {selectedNotification && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={handleCloseDetail}
          />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto"
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
                  onClick={handleCloseDetail}
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

                {/* Section Document avec preview/download */}
                {selectedNotification.related_document_id && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-700 font-medium mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Document joint
                    </p>

                    {documentInfo.loading ? (
                      <div className="flex items-center gap-2 text-gray-500">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Chargement du document...
                      </div>
                    ) : documentInfo.error ? (
                      <p className="text-red-600 text-sm">{documentInfo.error}</p>
                    ) : documentInfo.document ? (
                      <div>
                        <p className="font-medium text-gray-900 mb-1">
                          {documentInfo.document.nom_original || documentInfo.document.nom}
                        </p>
                        <p className="text-sm text-gray-500 mb-3">
                          {documentInfo.document.type_document.toUpperCase()} - {formatFileSize(documentInfo.document.taille)}
                        </p>

                        <div className="flex gap-2">
                          {/* Preview pour PDF/images */}
                          {['pdf', 'image'].includes(documentInfo.document.type_document) && (
                            <button
                              onClick={handlePreviewDocument}
                              className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                            >
                              <Eye className="w-4 h-4" />
                              Visualiser
                            </button>
                          )}

                          {/* Download */}
                          <button
                            onClick={handleDownloadDocument}
                            className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                          >
                            <Download className="w-4 h-4" />
                            Telecharger
                          </button>

                          {/* Voir dans GED */}
                          <button
                            onClick={handleViewDocument}
                            className="flex items-center gap-2 px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Ouvrir dans la GED
                          </button>
                        </div>
                      </div>
                    ) : null}
                  </div>
                )}

                <p className="text-xs text-gray-600 mb-4">
                  {formatRelativeTime(selectedNotification.created_at)}
                </p>

                {/* Actions selon le type de notification */}
                <div className="flex flex-wrap gap-2">
                  {/* Voir le post (pour commentaires, likes, mentions) */}
                  {selectedNotification.related_post_id && (
                    <button
                      onClick={handleViewPost}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <MessageCircle className="w-4 h-4" />
                      Voir le post
                    </button>
                  )}

                  {/* Voir le chantier (si pas de document) */}
                  {selectedNotification.related_chantier_id && !selectedNotification.related_document_id && !selectedNotification.related_post_id && (
                    <button
                      onClick={handleViewChantier}
                      className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <Building2 className="w-4 h-4" />
                      Voir le chantier
                    </button>
                  )}

                  <button
                    onClick={handleCloseDetail}
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
