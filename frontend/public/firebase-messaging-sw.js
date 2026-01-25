/**
 * Service Worker pour Firebase Cloud Messaging.
 *
 * Gère les notifications push en arrière-plan (quand l'app n'est pas au premier plan).
 *
 * Ce fichier DOIT être à la racine du site (public/) pour fonctionner.
 */

/* eslint-disable no-undef */

// Import Firebase scripts (CDN)
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js')
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js')

// Configuration Firebase
// Ces valeurs doivent correspondre à celles du frontend
const firebaseConfig = {
  apiKey: self.FIREBASE_API_KEY || '',
  authDomain: self.FIREBASE_AUTH_DOMAIN || '',
  projectId: self.FIREBASE_PROJECT_ID || '',
  storageBucket: self.FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: self.FIREBASE_MESSAGING_SENDER_ID || '',
  appId: self.FIREBASE_APP_ID || '',
}

// Initialiser Firebase si configuré
if (firebaseConfig.apiKey && firebaseConfig.projectId) {
  firebase.initializeApp(firebaseConfig)

  const messaging = firebase.messaging()

  // Gestion des messages en arrière-plan
  messaging.onBackgroundMessage((payload) => {
    console.log('[SW] Message reçu en arrière-plan:', payload)

    const { title, body, icon, data } = payload.notification || {}

    const notificationOptions = {
      body: body || '',
      icon: icon || '/icon-192.png',
      badge: '/icon-72.png',
      tag: data?.type || 'default',
      data: payload.data,
      // Actions possibles
      actions: getActionsForType(payload.data?.type),
    }

    self.registration.showNotification(
      title || 'Hub Chantier',
      notificationOptions
    )
  })
}

/**
 * Retourne les actions selon le type de notification.
 */
function getActionsForType(type) {
  switch (type) {
    case 'reservation_demande':
      return [
        { action: 'view', title: 'Voir' },
        { action: 'validate', title: 'Valider' },
      ]
    case 'signalement':
      return [
        { action: 'view', title: 'Voir' },
      ]
    default:
      return [
        { action: 'view', title: 'Voir' },
      ]
  }
}

/**
 * Gestion du clic sur une notification.
 */
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification cliquée:', event)

  event.notification.close()

  const data = event.notification.data || {}
  let url = '/'

  // Déterminer l'URL selon le type
  switch (data.type) {
    case 'reservation_demande':
      url = '/logistique?tab=validations'
      break
    case 'reservation_validee':
    case 'reservation_refusee':
    case 'rappel_reservation':
      url = data.reservation_id
        ? `/logistique/reservations/${data.reservation_id}`
        : '/logistique'
      break
    case 'signalement':
      url = data.signalement_id
        ? `/signalements/${data.signalement_id}`
        : '/signalements'
      break
  }

  // Gérer les actions
  if (event.action === 'validate' && data.reservation_id) {
    // Action de validation rapide (future feature)
    url = `/logistique/reservations/${data.reservation_id}?action=validate`
  }

  // Ouvrir ou focus sur la fenêtre
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Chercher une fenêtre existante
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url)
            return client.focus()
          }
        }
        // Sinon ouvrir une nouvelle fenêtre
        if (clients.openWindow) {
          return clients.openWindow(url)
        }
      })
  )
})

console.log('[SW] Firebase Messaging Service Worker initialisé')
