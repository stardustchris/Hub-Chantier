import axios from 'axios'
import { emitSessionExpired } from './authEvents'
import { getCsrfToken, requiresCsrf, CSRF_HEADER, fetchCsrfToken } from './csrf'

// En dev, Vite proxy les requêtes /api vers le backend
// En prod, VITE_API_URL doit être configuré dans l'environnement
const baseURL = import.meta.env.VITE_API_URL || ''

// Avertissement si VITE_API_URL n'est pas défini en production
if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
  console.warn(
    '[API] VITE_API_URL non défini en production. Les requêtes API utiliseront des chemins relatifs.'
  )
}

// Validation HTTPS en production (sécurité)
if (import.meta.env.PROD && baseURL && !baseURL.startsWith('https://')) {
  throw new Error(
    `[API] VITE_API_URL doit utiliser HTTPS en production. Valeur actuelle: ${baseURL}`
  )
}

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 secondes
  withCredentials: true, // Include HttpOnly cookies in requests
})

// Intercepteur pour ajouter le token d'authentification et CSRF
api.interceptors.request.use(async (config) => {
  // Token d'authentification géré automatiquement par cookie HttpOnly
  // avec withCredentials: true - Pas besoin de header Authorization manuel

  // Token CSRF pour les méthodes mutables (POST, PUT, DELETE, PATCH)
  if (config.method && requiresCsrf(config.method)) {
    let csrfToken = getCsrfToken()
    // Si pas de token CSRF, en récupérer un
    if (!csrfToken) {
      try {
        csrfToken = await fetchCsrfToken()
      } catch {
        // Continuer sans token CSRF si impossible de le récupérer
      }
    }
    if (csrfToken) {
      config.headers[CSRF_HEADER] = csrfToken
    }
  }

  return config
})

// URLs à exclure de la logique de session expirée (authentification et vérifications)
const AUTH_URLS = ['/api/auth/me', '/api/auth/login', '/api/auth/logout', '/api/csrf-token']

// Compteur pour détecter les 401 répétés (évite déconnexion sur erreur transitoire)
let consecutive401Count = 0
const MAX_CONSECUTIVE_401 = 2

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => {
    // Réinitialiser le compteur sur toute réponse réussie
    consecutive401Count = 0
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || ''

      // Ne pas traiter les 401 sur les URLs d'authentification
      const isAuthUrl = AUTH_URLS.some(authUrl => url.includes(authUrl))
      if (isAuthUrl) {
        return Promise.reject(error)
      }

      // Incrémenter le compteur de 401 consécutifs
      consecutive401Count++

      // Ne déclencher la déconnexion qu'après plusieurs 401 consécutifs
      // Cela évite les déconnexions sur erreurs transitoires (hot-reload, race conditions)
      if (consecutive401Count >= MAX_CONSECUTIVE_401) {
        // Notifie AuthContext pour mettre à jour l'état user et nettoyer le cookie
        emitSessionExpired()
        consecutive401Count = 0
      }
    }
    return Promise.reject(error)
  }
)

export default api
