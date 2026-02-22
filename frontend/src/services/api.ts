import axios from 'axios'
import { emitSessionExpired } from './authEvents'
import { getCsrfToken, requiresCsrf, CSRF_HEADER, fetchCsrfToken } from './csrf'

// En dev, on force un baseURL relatif pour passer par le proxy Vite (/api)
// et éviter les problèmes localhost vs 127.0.0.1 (cookies/CORS).
// En prod, VITE_API_URL peut être défini pour pointer vers l'API.
const configuredApiUrl = import.meta.env.VITE_API_URL || ''
const baseURL = import.meta.env.DEV ? '' : configuredApiUrl

// Avertissement si VITE_API_URL n'est pas défini en production
if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
  console.warn(
    '[API] VITE_API_URL non défini en production. Les requêtes API utiliseront des chemins relatifs.'
  )
}

// Validation HTTPS en production (sécurité)
if (import.meta.env.PROD && baseURL && !baseURL.startsWith('https://')) {
  console.warn(
    `[API] VITE_API_URL devrait utiliser HTTPS en production. Valeur actuelle: ${baseURL}`
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
    // Exempter les endpoints d'authentification du CSRF (login initial, etc.)
    const url = config.url || ''
    const isAuthEndpoint = url.includes('/api/auth/login') || url.includes('/api/auth/csrf-token')
    if (!isAuthEndpoint) {
      let csrfToken = getCsrfToken()
      // Si pas de token CSRF, en récupérer un
      if (!csrfToken) {
        csrfToken = await fetchCsrfToken()
      }
      config.headers[CSRF_HEADER] = csrfToken
    }
  }

  return config
})

// URLs à exclure de la logique de session expirée (authentification et vérifications)
const AUTH_URLS = ['/api/auth/me', '/api/auth/login', '/api/auth/logout', '/api/auth/csrf-token']

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
