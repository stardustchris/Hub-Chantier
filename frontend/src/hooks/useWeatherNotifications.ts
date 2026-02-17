/**
 * useWeatherNotifications - Hook pour les notifications push météo
 *
 * Encapsule la logique RGPD de consentement + notifications météo:
 * - Demande la permission push si consentement donné
 * - Envoie une notification si alerte météo active
 *
 * Implémente les features météo/notifications du Dashboard (CDC section 2).
 */

import { useEffect } from 'react'
import { weatherNotificationService } from '../services/weatherNotifications'
import { consentService } from '../services/consent'
import type { WeatherAlert } from './useWeather'

interface UseWeatherNotificationsOptions {
  /** Alerte météo courante (depuis useWeather) */
  weatherAlert: WeatherAlert | null
}

/**
 * Gère la demande de permission pour les notifications push météo
 * et l'envoi d'alertes, en respectant le consentement RGPD.
 */
export function useWeatherNotifications({ weatherAlert }: UseWeatherNotificationsOptions): void {
  // Demander la permission push si consentement donné
  useEffect(() => {
    const requestNotifications = async () => {
      const hasConsent = await consentService.hasConsent('notifications')
      if (hasConsent && weatherNotificationService.areNotificationsSupported()) {
        weatherNotificationService.requestNotificationPermission()
      }
    }

    requestNotifications()
  }, [])

  // Envoyer une notification si alerte météo et consentement donné
  useEffect(() => {
    const sendAlert = async () => {
      const hasConsent = await consentService.hasConsent('notifications')
      if (weatherAlert && hasConsent) {
        weatherNotificationService.sendWeatherAlertNotification(weatherAlert)
      }
    }

    sendAlert()
  }, [weatherAlert])
}

export default useWeatherNotifications
