/**
 * Event bus pour les evenements d'authentification
 * Permet de synchroniser api.ts et AuthContext sur les 401
 * + Synchronisation multi-onglets via BroadcastChannel
 */

type AuthEventListener = () => void

const listeners: Set<AuthEventListener> = new Set()

// BroadcastChannel pour synchroniser les onglets
let authChannel: BroadcastChannel | null = null

// Initialiser le channel si supporté
if (typeof BroadcastChannel !== 'undefined') {
  authChannel = new BroadcastChannel('hub-chantier-auth')
  authChannel.onmessage = (event) => {
    if (event.data === 'logout') {
      // Notifier les listeners locaux sans re-émettre sur le channel
      listeners.forEach((listener) => listener())
    }
  }
}

/**
 * Emet un evenement de session expiree (401)
 * Appelé par api.ts quand une erreur 401 est reçue
 * Notifie aussi les autres onglets via BroadcastChannel
 */
export function emitSessionExpired(): void {
  // Notifier les listeners locaux
  listeners.forEach((listener) => listener())
  // Notifier les autres onglets
  authChannel?.postMessage('logout')
}

/**
 * S'abonne aux evenements de session expiree
 * Retourne une fonction pour se désabonner
 */
export function onSessionExpired(listener: AuthEventListener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

/**
 * Emet un evenement de logout manuel (utilisateur)
 * Synchronise les autres onglets
 */
export function emitLogout(): void {
  authChannel?.postMessage('logout')
}
