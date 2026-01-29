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
import { logger } from './logger'

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
      // Ne PAS générer un token client-side factice : il ne serait pas validé
      // par le backend et donnerait un faux sentiment de sécurité.
      // Les requêtes mutables seront bloquées si le token n'est pas disponible.
      logger.warn('[CSRF] Endpoint /api/csrf-token non disponible, requêtes mutables bloquées', error)
      throw error
    } finally {
      csrfTokenPromise = null
    }
  })()

  return csrfTokenPromise
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
