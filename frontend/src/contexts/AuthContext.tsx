import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { authService, User } from '../services/auth'
import { onSessionExpired, emitLogout } from '../services/authEvents'
import { clearCsrfToken } from '../services/csrf'
import api from '../services/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Fonction logout mémorisée pour être utilisée comme callback
  const logout = useCallback(async () => {
    try {
      // Appeler l'API pour supprimer le cookie HttpOnly côté serveur
      await api.post('/api/auth/logout')
    } catch {
      // Continue même si l'appel échoue
    }
    // Supprimer aussi le token sessionStorage (fallback)
    sessionStorage.removeItem('access_token')
    // Nettoyer le token CSRF pour éviter sa réutilisation
    clearCsrfToken()
    setUser(null)
    // Notifier les autres onglets du logout
    emitLogout()
  }, [])

  useEffect(() => {
    // Vérifier si l'utilisateur est authentifié au chargement
    // Priorité: Cookie HttpOnly (envoyé automatiquement) > sessionStorage (fallback)
    const checkAuth = async () => {
      try {
        // Essayer de récupérer l'utilisateur (le cookie HttpOnly est envoyé automatiquement)
        const currentUser = await authService.getCurrentUser()
        setUser(currentUser)
      } catch {
        // Non authentifié - nettoyer le sessionStorage au cas où
        sessionStorage.removeItem('access_token')
      }
      setIsLoading(false)
    }
    checkAuth()
  }, [])

  // Écouter les événements de session expirée (401 de api.ts)
  useEffect(() => {
    const unsubscribe = onSessionExpired(() => {
      setUser(null)
      // Rediriger vers login après mise à jour de l'état
      window.location.href = '/login'
    })
    return unsubscribe
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password)
    // Le token est stocké automatiquement dans un cookie HttpOnly par le serveur
    // sessionStorage est conservé comme fallback pour compatibilité ascendante
    sessionStorage.setItem('access_token', response.access_token)
    setUser(response.user)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
