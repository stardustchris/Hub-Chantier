/**
 * Service de notifications météo
 * Gère les alertes push pour les conditions météo dangereuses
 */

import type { WeatherAlert } from './weather'
import { logger } from './logger'

/** Clé localStorage pour le dernier alerte notifiée */
const LAST_ALERT_KEY = 'hubchantier_last_weather_alert'

/**
 * Vérifie si les notifications sont supportées et autorisées
 */
export function areNotificationsSupported(): boolean {
  return 'Notification' in window
}

/**
 * Demande la permission pour les notifications
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!areNotificationsSupported()) {
    logger.warn('Les notifications ne sont pas supportées')
    return 'denied'
  }

  try {
    const permission = await Notification.requestPermission()
    logger.info('Permission notifications', { permission })
    return permission
  } catch (err) {
    logger.error('Erreur demande permission', err)
    return 'denied'
  }
}

/**
 * Vérifie si les notifications sont autorisées
 */
export function areNotificationsAllowed(): boolean {
  return areNotificationsSupported() && Notification.permission === 'granted'
}

/**
 * Envoie une notification d'alerte météo
 */
export function sendWeatherAlertNotification(alert: WeatherAlert): void {
  if (!areNotificationsAllowed()) {
    logger.debug('Notifications non autorisées')
    return
  }

  // Vérifier si on a déjà notifié cette alerte récemment
  const lastAlertKey = localStorage.getItem(LAST_ALERT_KEY)
  const alertKey = `${alert.type}_${alert.title}_${alert.startTime}`

  if (lastAlertKey === alertKey) {
    logger.debug('Alerte déjà notifiée')
    return
  }

  // Icônes selon le type d'alerte
  const icons: Record<WeatherAlert['type'], string> = {
    vigilance_jaune: '/icons/weather-yellow.png',
    vigilance_orange: '/icons/weather-orange.png',
    vigilance_rouge: '/icons/weather-red.png',
  }

  // Créer la notification
  try {
    const notification = new Notification(alert.title, {
      body: alert.description,
      icon: icons[alert.type] || '/icons/weather.png',
      badge: '/icons/badge-weather.png',
      tag: 'weather-alert', // Une seule notification à la fois
      requireInteraction: alert.type === 'vigilance_rouge', // Rouge reste affichée
      data: { alert },
    })

    // Enregistrer qu'on a notifié cette alerte
    localStorage.setItem(LAST_ALERT_KEY, alertKey)

    // Gérer le clic sur la notification
    notification.onclick = () => {
      window.focus()
      notification.close()
      // Ouvrir la page météo ou le dashboard
      window.location.href = '/dashboard'
    }

    // Log
    logger.info('Notification alerte météo envoyée', { type: alert.type })
  } catch (err) {
    logger.error('Erreur envoi notification', err)
  }
}

/**
 * Envoie une notification du bulletin météo matinal
 */
export function sendMorningBulletinNotification(
  location: string,
  temperature: number,
  _condition: string,
  bulletin: string
): void {
  if (!areNotificationsAllowed()) {
    return
  }

  // Vérifier si on a déjà envoyé le bulletin aujourd'hui
  const today = new Date().toISOString().split('T')[0]
  const lastBulletinKey = localStorage.getItem('hubchantier_last_bulletin')

  if (lastBulletinKey === today) {
    return
  }

  try {
    const notification = new Notification(`Météo ${location} - ${temperature}°C`, {
      body: bulletin,
      icon: '/icons/weather.png',
      tag: 'weather-bulletin',
    })

    localStorage.setItem('hubchantier_last_bulletin', today)

    notification.onclick = () => {
      window.focus()
      notification.close()
    }

    logger.info('Bulletin météo matinal envoyé')
  } catch (err) {
    logger.error('Erreur envoi bulletin', err)
  }
}

/**
 * Enregistre le service worker pour les notifications push en arrière-plan
 * (pour les alertes même quand l'app est fermée)
 */
export async function registerPushNotifications(): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    logger.warn('Push notifications non supportées')
    return false
  }

  try {
    const registration = await navigator.serviceWorker.ready

    // Vérifier si déjà abonné
    const existingSubscription = await registration.pushManager.getSubscription()
    if (existingSubscription) {
      logger.info('Déjà abonné aux push notifications')
      return true
    }

    // En production, il faudrait une clé VAPID du serveur
    // Pour l'instant, on utilise les notifications locales uniquement
    logger.info('Push notifications configurées (mode local)')
    return true
  } catch (err) {
    logger.error('Erreur registration push', err)
    return false
  }
}

/**
 * Planifie une vérification périodique des alertes météo
 * Appelé au démarrage de l'app
 */
export function scheduleWeatherAlertCheck(checkFunction: () => Promise<WeatherAlert | null>): void {
  // Vérifier toutes les 30 minutes
  const INTERVAL = 30 * 60 * 1000

  const check = async () => {
    try {
      const alert = await checkFunction()
      if (alert) {
        sendWeatherAlertNotification(alert)
      }
    } catch (err) {
      logger.error('Erreur vérification alerte', err)
    }
  }

  // Première vérification après 1 minute
  setTimeout(check, 60 * 1000)

  // Puis toutes les 30 minutes
  setInterval(check, INTERVAL)
}

export const weatherNotificationService = {
  areNotificationsSupported,
  requestNotificationPermission,
  areNotificationsAllowed,
  sendWeatherAlertNotification,
  sendMorningBulletinNotification,
  registerPushNotifications,
  scheduleWeatherAlertCheck,
}
