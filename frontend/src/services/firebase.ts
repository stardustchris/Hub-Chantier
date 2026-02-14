/**
 * Configuration Firebase pour les notifications push.
 *
 * CONFIGURATION REQUISE:
 * 1. Créer un projet Firebase sur https://console.firebase.google.com
 * 2. Activer Cloud Messaging
 * 3. Copier la configuration dans les variables d'environnement
 *
 * Variables d'environnement (à ajouter dans .env):
 * VITE_FIREBASE_API_KEY=xxx
 * VITE_FIREBASE_AUTH_DOMAIN=xxx.firebaseapp.com
 * VITE_FIREBASE_PROJECT_ID=xxx
 * VITE_FIREBASE_STORAGE_BUCKET=xxx.appspot.com
 * VITE_FIREBASE_MESSAGING_SENDER_ID=xxx
 * VITE_FIREBASE_APP_ID=xxx
 * VITE_FIREBASE_VAPID_KEY=xxx (pour Web Push)
 */

/**
 * Phase 2 Performance: Firebase lazy loaded (350KB+ chargé uniquement si utilisé)
 */
import type { FirebaseApp } from 'firebase/app'
import type { Messaging } from 'firebase/messaging'
import { logger } from './logger'

// Configuration Firebase depuis les variables d'environnement
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY

// Singleton
let app: FirebaseApp | null = null
let messaging: Messaging | null = null

/**
 * Vérifie si Firebase est configuré.
 */
export const isFirebaseConfigured = (): boolean => {
  return Boolean(
    firebaseConfig.apiKey &&
    firebaseConfig.projectId &&
    firebaseConfig.messagingSenderId
  )
}

/**
 * Initialise Firebase avec lazy loading.
 * Charge firebase/app uniquement quand appelé (économise ~350KB au chargement initial)
 */
export const initFirebase = async (): Promise<FirebaseApp | null> => {
  if (app) return app

  if (!isFirebaseConfigured()) {
    // Firebase non configuré - ne pas logger en production
    if (import.meta.env.DEV) {
      logger.warn(
        'Firebase non configuré. Définir les variables VITE_FIREBASE_* dans .env'
      )
    }
    return null
  }

  try {
    // Lazy load firebase/app
    const { initializeApp } = await import('firebase/app')
    app = initializeApp(firebaseConfig)
    if (import.meta.env.DEV) {
      logger.info('Firebase initialisé (lazy loaded)')
    }
    return app
  } catch (error) {
    if (import.meta.env.DEV) {
      logger.error('Erreur initialisation Firebase', error, { context: 'firebase' })
    }
    return null
  }
}

/**
 * Récupère l'instance Messaging avec lazy loading.
 */
export const getFirebaseMessaging = async (): Promise<Messaging | null> => {
  if (messaging) return messaging

  const firebaseApp = await initFirebase()
  if (!firebaseApp) return null

  try {
    // Lazy load firebase/messaging
    const { getMessaging } = await import('firebase/messaging')
    messaging = getMessaging(firebaseApp)
    return messaging
  } catch (error) {
    if (import.meta.env.DEV) {
      logger.error('Erreur initialisation Messaging', error, { context: 'firebase' })
    }
    return null
  }
}

/**
 * Demande la permission et récupère le token FCM avec lazy loading.
 *
 * @returns Token FCM ou null si refusé/erreur
 */
export const requestNotificationPermission = async (): Promise<string | null> => {
  // Vérifier support
  if (!('Notification' in window)) {
    if (import.meta.env.DEV) {
      logger.warn('Notifications non supportées par ce navigateur')
    }
    return null
  }

  // Demander permission
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') {
    if (import.meta.env.DEV) {
      logger.warn('Permission notifications refusée')
    }
    return null
  }

  // Récupérer le token
  const msg = await getFirebaseMessaging()
  if (!msg) {
    if (import.meta.env.DEV) {
      logger.warn('Firebase Messaging non disponible')
    }
    return null
  }

  try {
    // Lazy load getToken
    const { getToken } = await import('firebase/messaging')
    const token = await getToken(msg, {
      vapidKey: VAPID_KEY,
    })

    if (token) {
      if (import.meta.env.DEV) {
        logger.info('Token FCM obtenu:', token.substring(0, 20) + '...')
      }
      return token
    } else {
      if (import.meta.env.DEV) {
        logger.warn('Aucun token FCM disponible')
      }
      return null
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      logger.error('Erreur récupération token FCM', error, { context: 'firebase' })
    }
    return null
  }
}

/**
 * Écoute les messages en foreground avec lazy loading.
 *
 * @param callback Fonction appelée quand un message arrive
 * @returns Fonction de nettoyage ou null
 */
export const onForegroundMessage = async (
  callback: (payload: {
    title?: string
    body?: string
    data?: Record<string, string>
  }) => void
): Promise<(() => void) | null> => {
  const msg = await getFirebaseMessaging()
  if (!msg) return null

  // Lazy load onMessage
  const { onMessage } = await import('firebase/messaging')
  return onMessage(msg, (payload) => {
    if (import.meta.env.DEV) {
      logger.info('Message reçu (foreground):', payload)
    }
    callback({
      title: payload.notification?.title,
      body: payload.notification?.body,
      data: payload.data,
    })
  })
}

export default {
  initFirebase,
  isFirebaseConfigured,
  getFirebaseMessaging,
  requestNotificationPermission,
  onForegroundMessage,
}
