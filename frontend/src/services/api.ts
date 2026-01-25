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
  // Token d'authentification
  // Préférence: Cookie HttpOnly (géré automatiquement par le navigateur via withCredentials)
  // Fallback: sessionStorage pour compatibilité ascendante pendant la transition
  const token = sessionStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

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

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('access_token')
      // Notifie AuthContext pour mettre à jour l'état user
      emitSessionExpired()
    }
    return Promise.reject(error)
  }
)

export default api
