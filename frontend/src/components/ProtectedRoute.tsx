import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import type { UserRole } from '../types'

interface ProtectedRouteProps {
  children: React.ReactNode
  /** Si défini, seuls ces rôles peuvent accéder à la route. Sinon, tous les utilisateurs authentifiés. */
  allowedRoles?: UserRole[]
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Vérification du rôle si des restrictions sont définies
  if (allowedRoles && user?.role && !allowedRoles.includes(user.role as UserRole)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
