import axios from 'axios'
import { emitSessionExpired } from './authEvents'

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
})

// Intercepteur pour ajouter le token
api.interceptors.request.use((config) => {
  // sessionStorage: plus sécurisé que localStorage (non accessible après fermeture navigateur)
  const token = sessionStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
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
