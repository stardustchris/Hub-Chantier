/**
 * Service de gestion des tokens CSRF
 * Implémente le pattern "Double Submit Cookie" pour les SPA
 *
 * Le token CSRF est:
 * 1. Récupéré depuis le backend via GET /api/csrf-token
 * 2. Stocké en mémoire (pas de localStorage pour éviter XSS)
 * 3. Envoyé dans le header X-CSRF-Token pour chaque requête mutable
 */

import api from './api'

// Stockage en mémoire du token CSRF (non accessible via XSS)
let csrfToken: string | null = null
let csrfTokenPromise: Promise<string> | null = null

/**
 * Header utilisé pour envoyer le token CSRF
 */
export const CSRF_HEADER = 'X-CSRF-Token'

/**
 * Méthodes HTTP nécessitant un token CSRF
 */
export const CSRF_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']

/**
 * Vérifie si une méthode HTTP nécessite un token CSRF
 */
export function requiresCsrf(method: string): boolean {
  return CSRF_METHODS.includes(method.toUpperCase())
}

/**
 * Récupère le token CSRF depuis le backend
 * Utilise un singleton promise pour éviter les requêtes multiples
 */
export async function fetchCsrfToken(): Promise<string> {
  // Si on a déjà le token, le retourner
  if (csrfToken) {
    return csrfToken
  }

  // Si une requête est déjà en cours, attendre son résultat
  if (csrfTokenPromise) {
    return csrfTokenPromise
  }

  // Sinon, faire la requête
  csrfTokenPromise = (async () => {
    try {
      // Le backend doit exposer cet endpoint
      const response = await api.get<{ csrf_token: string }>('/api/csrf-token')
      csrfToken = response.data.csrf_token
      return csrfToken
    } catch (error) {
      // En cas d'erreur (endpoint non disponible), on génère un token côté client
      // Ce token sera validé si le backend implémente aussi un cookie CSRF
      console.warn('[CSRF] Endpoint /api/csrf-token non disponible, utilisation du fallback')
      csrfToken = generateClientToken()
      return csrfToken
    } finally {
      csrfTokenPromise = null
    }
  })()

  return csrfTokenPromise
}

/**
 * Génère un token CSRF côté client comme fallback
 * Utilisé si le backend n'expose pas d'endpoint CSRF
 */
function generateClientToken(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * Récupère le token CSRF actuel (synchrone)
 * Retourne null si le token n'a pas encore été récupéré
 */
export function getCsrfToken(): string | null {
  return csrfToken
}

/**
 * Réinitialise le token CSRF (à appeler après logout)
 */
export function clearCsrfToken(): void {
  csrfToken = null
  csrfTokenPromise = null
}

/**
 * Service CSRF exporté
 */
export const csrfService = {
  fetchToken: fetchCsrfToken,
  getToken: getCsrfToken,
  clear: clearCsrfToken,
  requiresCsrf,
  CSRF_HEADER,
}

export default csrfService
