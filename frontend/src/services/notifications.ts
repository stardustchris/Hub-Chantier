/**
 * Service de gestion des notifications push.
 *
 * Gère :
 * - Demande de permission
 * - Enregistrement du token auprès du backend
 * - Affichage des notifications en foreground
 * - Navigation au clic sur notification
 */

import api from './api'
import { logger } from './logger'
import {
  isFirebaseConfigured,
  requestNotificationPermission,
  onForegroundMessage,
} from './firebase'

export interface NotificationData {
  type: string
  reservation_id?: string
  ressource_id?: string
  signalement_id?: string
  date?: string
  motif?: string
}

export interface NotificationPayload {
  title?: string
  body?: string
  data?: NotificationData
}

// Callbacks pour les notifications
type NotificationCallback = (payload: NotificationPayload) => void
const subscribers: NotificationCallback[] = []

/**
 * Initialise le service de notifications.
 *
 * @returns true si initialisé avec succès
 */
export const initNotifications = async (): Promise<boolean> => {
  if (!isFirebaseConfigured()) {
    logger.info('Firebase non configuré - mode simulation')
    return false
  }

  // Demander la permission et récupérer le token
  const token = await requestNotificationPermission()

  if (token) {
    // Enregistrer le token auprès du backend
    await registerToken(token)

    // Écouter les messages en foreground
    onForegroundMessage((payload) => {
      // Convertir le payload générique en NotificationPayload
      const notificationPayload: NotificationPayload = {
        title: payload.title,
        body: payload.body,
        data: payload.data as NotificationData | undefined,
      }

      // Notifier les subscribers
      subscribers.forEach((callback) => callback(notificationPayload))

      // Afficher une notification native si l'app est en foreground
      showNotification(notificationPayload)
    })

    return true
  }

  return false
}

/**
 * Enregistre le token FCM auprès du backend.
 */
const registerToken = async (token: string): Promise<void> => {
  try {
    await api.post('/users/me/push-token', { token })
    logger.info('Token FCM enregistré auprès du backend')
  } catch (error) {
    logger.error('Erreur enregistrement token', error, { context: 'notifications' })
  }
}

/**
 * Affiche une notification native.
 */
const showNotification = (payload: NotificationPayload): void => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    return
  }

  const { title, body, data } = payload

  const notification = new Notification(title || 'Hub Chantier', {
    body: body || '',
    icon: '/icon-192.png',
    badge: '/icon-72.png',
    tag: data?.type || 'default',
    data,
  })

  notification.onclick = () => {
    window.focus()
    handleNotificationClick(data)
    notification.close()
  }
}

/**
 * Gère le clic sur une notification.
 */
const handleNotificationClick = (data?: NotificationData): void => {
  if (!data) return

  // Navigation selon le type de notification
  switch (data.type) {
    case 'reservation_demande':
      window.location.href = '/logistique?tab=validations'
      break
    case 'reservation_validee':
    case 'reservation_refusee':
    case 'rappel_reservation':
      if (data.reservation_id) {
        window.location.href = `/logistique/reservations/${data.reservation_id}`
      }
      break
    case 'signalement':
      if (data.signalement_id) {
        window.location.href = `/signalements/${data.signalement_id}`
      }
      break
    default:
      logger.info('Type de notification non géré:', data.type)
  }
}

/**
 * S'abonne aux notifications.
 *
 * @param callback Fonction appelée quand une notification arrive
 * @returns Fonction de désabonnement
 */
export const subscribeToNotifications = (
  callback: NotificationCallback
): (() => void) => {
  subscribers.push(callback)
  return () => {
    const index = subscribers.indexOf(callback)
    if (index > -1) {
      subscribers.splice(index, 1)
    }
  }
}

/**
 * Désactive les notifications pour cet utilisateur.
 */
export const disableNotifications = async (): Promise<void> => {
  try {
    await api.delete('/users/me/push-token')
    logger.info('Notifications désactivées')
  } catch (error) {
    logger.error('Erreur désactivation notifications', error, { context: 'notifications' })
  }
}

/**
 * Vérifie si les notifications sont activées.
 */
export const areNotificationsEnabled = (): boolean => {
  return (
    'Notification' in window &&
    Notification.permission === 'granted' &&
    isFirebaseConfigured()
  )
}

/**
 * Vérifie si les notifications sont supportées.
 */
export const areNotificationsSupported = (): boolean => {
  return 'Notification' in window && 'serviceWorker' in navigator
}

export default {
  initNotifications,
  subscribeToNotifications,
  disableNotifications,
  areNotificationsEnabled,
  areNotificationsSupported,
}
