import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { authService, User } from '../services/auth'
import { onSessionExpired, emitLogout } from '../services/authEvents'
import { clearCsrfToken } from '../services/csrf'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Fonction logout mémorisée pour être utilisée comme callback
  const logout = useCallback(() => {
    sessionStorage.removeItem('access_token')
    // Nettoyer le token CSRF pour éviter sa réutilisation
    clearCsrfToken()
    setUser(null)
    // Notifier les autres onglets du logout
    emitLogout()
  }, [])

  useEffect(() => {
    // Vérifier si un token existe au chargement
    // sessionStorage est plus sécurisé que localStorage (non accessible après fermeture navigateur)
    const checkAuth = async () => {
      const token = sessionStorage.getItem('access_token')
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
        } catch {
          sessionStorage.removeItem('access_token')
        }
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
    // sessionStorage: token supprimé à la fermeture du navigateur (plus sécurisé)
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
