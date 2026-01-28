/**
 * Service de gestion des consentements RGPD
 *
 * Gère les consentements utilisateur pour :
 * - Géolocalisation (navigator.geolocation)
 * - Notifications push (weatherNotificationService)
 * - Analytics (futur)
 *
 * Conformité RGPD :
 * - Consentement explicite requis avant toute collecte de données
 * - Consentements stockés côté serveur (pas en localStorage pour éviter XSS)
 * - Possibilité de retirer le consentement à tout moment
 * - Cache en mémoire pour éviter appels API répétés
 */

import api from './api'
import { logger } from './logger'

export type ConsentType = 'geolocation' | 'notifications' | 'analytics'

export interface ConsentPreferences {
  geolocation: boolean
  notifications: boolean
  analytics: boolean
}

/**
 * État des consentements en mémoire (cache session)
 * Évite les appels API répétés pendant la session
 */
let consentCache: ConsentPreferences | null = null
let hasBannerBeenShown = false

/**
 * Réinitialise le cache (utile pour les tests)
 */
export function resetConsentCache(): void {
  consentCache = null
  hasBannerBeenShown = false
}

/**
 * Récupère les consentements depuis le serveur
 */
async function getConsents(): Promise<ConsentPreferences> {
  // Utiliser le cache si disponible
  if (consentCache !== null) {
    return consentCache
  }

  try {
    const response = await api.get<ConsentPreferences>('/api/auth/consents')
    consentCache = response.data
    return response.data
  } catch (error) {
    logger.error('Error fetching consents', error)
    // Valeurs par défaut : aucun consentement
    return {
      geolocation: false,
      notifications: false,
      analytics: false,
    }
  }
}

/**
 * Enregistre un consentement côté serveur
 */
async function setConsent(type: ConsentType, value: boolean): Promise<void> {
  try {
    await api.post('/api/auth/consents', {
      [type]: value,
    })

    // Mettre à jour le cache
    if (consentCache) {
      consentCache[type] = value
    } else {
      consentCache = {
        geolocation: type === 'geolocation' ? value : false,
        notifications: type === 'notifications' ? value : false,
        analytics: type === 'analytics' ? value : false,
      }
    }

    logger.info('Consent updated', { type, value })
  } catch (error) {
    logger.error('Error setting consent', error)
    throw error
  }
}

/**
 * Enregistre plusieurs consentements en une seule fois
 */
async function setConsents(consents: Partial<ConsentPreferences>): Promise<void> {
  try {
    await api.post('/api/auth/consents', consents)

    // Mettre à jour le cache
    if (consentCache) {
      consentCache = { ...consentCache, ...consents }
    } else {
      consentCache = {
        geolocation: consents.geolocation ?? false,
        notifications: consents.notifications ?? false,
        analytics: consents.analytics ?? false,
      }
    }

    logger.info('Consents updated', consents)
  } catch (error) {
    logger.error('Error setting consents', error)
    throw error
  }
}

export const consentService = {
  /**
   * Vérifie si un consentement spécifique a été donné
   */
  hasConsent: async (type: ConsentType): Promise<boolean> => {
    const consents = await getConsents()
    return consents[type]
  },

  /**
   * Vérifie si l'utilisateur a donné au moins un consentement
   * (utilisé pour déterminer si le banner doit être affiché)
   */
  hasAnyConsent: async (): Promise<boolean> => {
    const consents = await getConsents()
    return consents.geolocation || consents.notifications || consents.analytics
  },

  /**
   * Enregistre un consentement côté serveur
   */
  setConsent,

  /**
   * Enregistre plusieurs consentements en une seule fois
   */
  setConsents,

  /**
   * Révoque tous les consentements
   */
  revokeAllConsents: async (): Promise<void> => {
    await setConsents({
      geolocation: false,
      notifications: false,
      analytics: false,
    })
  },

  /**
   * Récupère tous les consentements
   */
  getAllConsents: async (): Promise<ConsentPreferences> => {
    return await getConsents()
  },

  /**
   * Marque le banner comme affiché (en mémoire, ne persiste pas entre rechargements)
   */
  markBannerAsShown: (): void => {
    hasBannerBeenShown = true
  },

  /**
   * Vérifie si le banner a déjà été affiché dans cette session
   */
  wasBannerShown: (): boolean => {
    return hasBannerBeenShown
  },

  /**
   * Réinitialise le cache (pour tests uniquement)
   */
  resetCache: resetConsentCache,
}

export default consentService
