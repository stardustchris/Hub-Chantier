/**
 * Event bus pour les evenements d'authentification
 * Permet de synchroniser api.ts et AuthContext sur les 401
 * + Synchronisation multi-onglets via BroadcastChannel (avec fallback localStorage)
 */

type AuthEventListener = () => void

const listeners: Set<AuthEventListener> = new Set()

// BroadcastChannel pour synchroniser les onglets (navigateurs modernes)
let authChannel: BroadcastChannel | null = null

// Fallback: utiliser localStorage + storage event (IE11, anciens navigateurs)
const LOGOUT_KEY = 'hub-chantier-logout-event'
let useFallback = false

// Initialiser le channel si supporté, sinon fallback localStorage
if (typeof BroadcastChannel !== 'undefined') {
  try {
    authChannel = new BroadcastChannel('hub-chantier-auth')
    authChannel.onmessage = (event) => {
      if (event.data === 'logout') {
        // Notifier les listeners locaux sans re-émettre sur le channel
        listeners.forEach((listener) => listener())
      }
    }
  } catch {
    // BroadcastChannel peut échouer dans certains contextes (ex: file://)
    useFallback = true
  }
} else {
  useFallback = true
}

// Fallback: écouter les changements localStorage pour sync multi-onglets
if (useFallback && typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === LOGOUT_KEY && event.newValue) {
      // Notifier les listeners locaux
      listeners.forEach((listener) => listener())
    }
  })
}

/**
 * Emet un evenement de session expiree (401)
 * Appelé par api.ts quand une erreur 401 est reçue
 * Notifie aussi les autres onglets via BroadcastChannel ou localStorage
 */
export function emitSessionExpired(): void {
  // Notifier les listeners locaux
  listeners.forEach((listener) => listener())
  // Notifier les autres onglets
  broadcastLogout()
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
  broadcastLogout()
}

/**
 * Broadcast logout vers autres onglets
 * Utilise BroadcastChannel si disponible, sinon localStorage
 */
function broadcastLogout(): void {
  if (authChannel) {
    authChannel.postMessage('logout')
  } else if (useFallback && typeof localStorage !== 'undefined') {
    // Fallback: écrire dans localStorage déclenche l'event 'storage' dans les autres onglets
    // On utilise un timestamp pour que chaque logout soit unique
    localStorage.setItem(LOGOUT_KEY, Date.now().toString())
    // Nettoyer immédiatement pour éviter de polluer le storage
    localStorage.removeItem(LOGOUT_KEY)
  }
}
